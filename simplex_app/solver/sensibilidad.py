"""
solver/sensibilidad.py
======================
Análisis de sensibilidad post-óptimo para Simplex y Gran M.

Calcula intervalos de factibilidad (bi) y de optimalidad (ci)
manteniendo la base óptima actual.
"""

import numpy as np

TOL = 1e-9
INF = float('inf')


def construir_matriz_restricciones(A, tipos):
    """
    Reconstruye la matriz de coeficientes del tableau inicial
    (variables de decisión + holgura/exceso/artificial).

    Args:
        A (np.ndarray): Matriz de restricciones.
        tipos (list): Tipos de restricción por fila.

    Returns:
        tuple: (matriz, n_vars)
    """
    A = np.array(A, dtype=float)
    m, n = A.shape
    n_artificiales = sum(1 for t in tipos if t in ('>=', '='))
    total_vars = n + m + n_artificiales

    matriz = np.zeros((m, total_vars))
    matriz[:, :n] = A

    idx_holgura = n
    idx_artificial = n + m

    for i, tipo in enumerate(tipos):
        if tipo == '<=':
            matriz[i, idx_holgura] = 1.0
        elif tipo == '>=':
            matriz[i, idx_holgura] = -1.0
            matriz[i, idx_artificial] = 1.0
            idx_artificial += 1
        elif tipo == '=':
            matriz[i, idx_artificial] = 1.0
            idx_artificial += 1
        idx_holgura += 1

    return matriz, n


def _formatear_limite(valor):
    """Formatea un límite numérico o infinito para mostrar en la interfaz."""
    if valor is None or np.isnan(valor):
        return "?"
    if valor <= -INF / 2 or valor <= -1e15:
        return "-∞"
    if valor >= INF / 2 or valor >= 1e15:
        return "+∞"
    return f"{valor:.6f}"


def _formatear_mensaje(limite_inferior, limite_superior):
    """Genera el mensaje de resultado estándar."""
    li = _formatear_limite(limite_inferior)
    ls = _formatear_limite(limite_superior)
    return (
        f"El valor puede variar entre [{li}] y [{ls}] "
        "sin alterar la base óptima actual."
    )


def obtener_restricciones_disponibles(n_restricciones):
    """
    Devuelve las etiquetas de restricciones para el análisis de bi.

    Args:
        n_restricciones (int): Número de restricciones del problema.

    Returns:
        list: Etiquetas ['R1', 'R2', ...].
    """
    return [f"R{i + 1}" for i in range(n_restricciones)]


def obtener_variables_basicas(variables_base, n_vars):
    """
    Devuelve las variables de decisión básicas disponibles para análisis de ci.

    Args:
        variables_base (list): Índices de columnas básicas por fila.
        n_vars (int): Número de variables de decisión.

    Returns:
        list: Etiquetas ['x1', 'x2', ...] de variables básicas.
    """
    basicas = []
    for indice in variables_base:
        if indice < n_vars:
            basicas.append(f"x{indice + 1}")
    return sorted(basicas, key=lambda nombre: int(nombre[1:]))


def calcular_intervalo_bi(
    tableau_final,
    variables_base,
    indice_restriccion,
    A,
    b,
    tipos,
):
    """
    Calcula el intervalo de factibilidad del lado derecho b_i.

    Usa la matriz inversa de la base B⁻¹ para determinar los cambios
    admisibles en b_i que mantienen la base óptima factible.

    Args:
        tableau_final (np.ndarray): Tableau óptimo final.
        variables_base (list): Índices de variables básicas.
        indice_restriccion (int): Índice de la restricción (0-based).
        A (list | np.ndarray): Matriz de restricciones.
        b (list | np.ndarray): Vector de términos independientes.
        tipos (list): Tipos de restricción.

    Returns:
        dict: {
            'limite_inferior': float,
            'limite_superior': float,
            'valor_actual': float,
            'mensaje': str
        }
    """
    matriz, _ = construir_matriz_restricciones(A, tipos)
    m = len(variables_base)
    b = np.array(b, dtype=float)
    valor_actual = b[indice_restriccion]

    B = matriz[:, variables_base]
    try:
        B_inv = np.linalg.inv(B)
    except np.linalg.LinAlgError:
        return {
            'limite_inferior': None,
            'limite_superior': None,
            'valor_actual': valor_actual,
            'mensaje': "No se pudo calcular B⁻¹ para esta base.",
        }

    columna = B_inv[:, indice_restriccion]
    x_basica = tableau_final[:m, -1]

    delta_inferior = -INF
    delta_superior = INF

    for j in range(m):
        coef = columna[j]
        if coef > TOL:
            delta = -x_basica[j] / coef
            delta_inferior = max(delta_inferior, delta)
        elif coef < -TOL:
            delta = -x_basica[j] / coef
            delta_superior = min(delta_superior, delta)

    limite_inferior = valor_actual + delta_inferior
    limite_superior = valor_actual + delta_superior

    return {
        'limite_inferior': limite_inferior,
        'limite_superior': limite_superior,
        'valor_actual': valor_actual,
        'mensaje': _formatear_mensaje(limite_inferior, limite_superior),
    }


def calcular_intervalo_ci(
    tableau_final,
    variables_base,
    indice_variable,
    c,
    n_vars,
    modo='max',
):
    """
    Calcula el intervalo de optimalidad del coeficiente c_j de una
    variable básica de decisión.

    Usa los costos reducidos de las variables no básicas y la fila
    del tableau correspondiente a la variable básica seleccionada.

    Args:
        tableau_final (np.ndarray): Tableau óptimo final.
        variables_base (list): Índices de variables básicas.
        indice_variable (int): Índice de la variable de decisión (0-based).
        c (list | np.ndarray): Coeficientes originales de la función objetivo.
        n_vars (int): Número de variables de decisión.
        modo (str): 'max' o 'min'.

    Returns:
        dict: {
            'limite_inferior': float,
            'limite_superior': float,
            'valor_actual': float,
            'mensaje': str
        }
    """
    c = np.array(c, dtype=float)
    valor_actual = c[indice_variable]
    m = len(variables_base)

    if indice_variable not in variables_base:
        return {
            'limite_inferior': None,
            'limite_superior': None,
            'valor_actual': valor_actual,
            'mensaje': (
                f"La variable x{indice_variable + 1} no es básica "
                "en la solución óptima actual."
            ),
        }

    fila_basica = next(
        i for i, var in enumerate(variables_base)
        if var == indice_variable
    )

    n_cols = tableau_final.shape[1] - 1
    no_basicas = [
        j for j in range(n_cols)
        if j not in variables_base
    ]

    delta_inferior = -INF
    delta_superior = INF

    for j in no_basicas:
        costo_reducido = tableau_final[-1, j]
        coef_fila = tableau_final[fila_basica, j]

        if abs(coef_fila) <= TOL:
            continue

        delta = costo_reducido / coef_fila

        if coef_fila > TOL:
            delta_superior = min(delta_superior, delta)
        else:
            delta_inferior = max(delta_inferior, delta)

    if modo == 'min':
        delta_inferior, delta_superior = -delta_superior, -delta_inferior

    limite_inferior = valor_actual + delta_inferior
    limite_superior = valor_actual + delta_superior

    return {
        'limite_inferior': limite_inferior,
        'limite_superior': limite_superior,
        'valor_actual': valor_actual,
        'mensaje': _formatear_mensaje(limite_inferior, limite_superior),
    }


def _restriccion_activa(lhs, bi, tipo):
    """Indica si una restricción está activa en el punto evaluado."""
    if tipo == '<=':
        return abs(bi - lhs) < TOL
    if tipo == '>=':
        return abs(lhs - bi) < TOL
    return abs(lhs - bi) < TOL


def _pendiente_frontera(a1, a2):
    """
    Pendiente dx₂/dx₁ de la recta de frontera a₁x₁ + a₂x₂ = b.

    Returns:
        float | None: Pendiente finita, o None si la recta es vertical.
    """
    if abs(a2) < TOL:
        return None
    return -a1 / a2


def _restricciones_activas_con_pendientes(solucion, A, b, tipos):
    """
    Identifica restricciones activas en la solución óptima, incluyendo
    las de no negatividad, con su pendiente gráfica.
    """
    solucion = np.array(solucion, dtype=float)
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    activas = []

    if solucion[0] < TOL:
        activas.append({
            'nombre': 'x₁ = 0',
            'pendiente': 0.0,
            'origen': 'no_negatividad',
        })

    if solucion[1] < TOL:
        activas.append({
            'nombre': 'x₂ = 0',
            'pendiente': 0.0,
            'origen': 'no_negatividad',
        })

    for i, (fila, bi, tipo) in enumerate(zip(A, b, tipos)):
        lhs = np.dot(fila, solucion)
        if not _restriccion_activa(lhs, bi, tipo):
            continue

        a1, a2 = fila[0], fila[1]
        pendiente = _pendiente_frontera(a1, a2)
        activas.append({
            'nombre': f'R{i + 1}',
            'pendiente': pendiente,
            'origen': 'restriccion',
        })

    return activas


def _intervalo_c1_desde_pendiente(m_min, m_max, c2):
    """Calcula el intervalo admisible de c₁ fijando c₂."""
    if abs(c2) < TOL:
        return -INF, INF

    limite_a = -m_max * c2
    limite_b = -m_min * c2
    return min(limite_a, limite_b), max(limite_a, limite_b)


def _intervalo_c2_desde_pendiente(m_min, m_max, c1):
    """Calcula el intervalo admisible de c₂ fijando c₁."""
    if abs(c1) < TOL:
        if m_min <= 0 <= m_max:
            return -INF, INF
        return None, None

    valores = []
    if abs(m_min) > TOL:
        valores.append(-c1 / m_min)
    if abs(m_max) > TOL:
        valores.append(-c1 / m_max)

    if not valores:
        return -INF, INF

    return min(valores), max(valores)


def calcular_intervalos_ci_grafico(c, solucion, A, b, tipos, modo='max'):
    """
    Calcula intervalos de optimalidad de c₁ y c₂ mediante el método gráfico.

    Usa las pendientes de las restricciones activas en el vértice óptimo.
    La pendiente de la función objetivo (-c₁/c₂) debe permanecer entre
    las pendientes de las restricciones que forman ese vértice.

    Solo aplica a problemas con 2 variables de decisión.

    Args:
        c (list | np.ndarray): Coeficientes de la función objetivo.
        solucion (list | np.ndarray): Solución óptima (x₁, x₂).
        A (list | np.ndarray): Matriz de restricciones.
        b (list | np.ndarray): Vector de términos independientes.
        tipos (list): Tipos de restricción.
        modo (str): 'max' o 'min'.

    Returns:
        dict: Resultado con intervalos, pendientes y mensaje descriptivo.
    """
    c = np.array(c, dtype=float)
    solucion = np.array(solucion, dtype=float)

    activas = _restricciones_activas_con_pendientes(solucion, A, b, tipos)
    pendientes_finitas = [
        r['pendiente'] for r in activas
        if r['pendiente'] is not None
    ]

    if len(pendientes_finitas) < 2:
        nombres = ', '.join(r['nombre'] for r in activas) or 'ninguna'
        return {
            'limite_inferior_c1': None,
            'limite_superior_c1': None,
            'limite_inferior_c2': None,
            'limite_superior_c2': None,
            'pendiente_actual': None,
            'pendiente_min': None,
            'pendiente_max': None,
            'restricciones_activas': activas,
            'mensaje': (
                "No se pudo aplicar el análisis gráfico: se requieren al "
                f"menos dos restricciones activas con pendiente finita. "
                f"Activas detectadas: {nombres}."
            ),
        }

    m_min = min(pendientes_finitas)
    m_max = max(pendientes_finitas)

    if abs(c[1]) < TOL:
        pendiente_actual = -INF if c[0] > 0 else INF
    else:
        pendiente_actual = -c[0] / c[1]

    lim_inf_c1, lim_sup_c1 = _intervalo_c1_desde_pendiente(m_min, m_max, c[1])
    lim_inf_c2, lim_sup_c2 = _intervalo_c2_desde_pendiente(m_min, m_max, c[0])

    if lim_inf_c2 is None:
        return {
            'limite_inferior_c1': lim_inf_c1,
            'limite_superior_c1': lim_sup_c1,
            'limite_inferior_c2': None,
            'limite_superior_c2': None,
            'pendiente_actual': pendiente_actual,
            'pendiente_min': m_min,
            'pendiente_max': m_max,
            'restricciones_activas': activas,
            'mensaje': (
                "No se pudo determinar un intervalo finito para c₂ con c₁ = 0 "
                "y las pendientes activas actuales."
            ),
        }

    nombres = ', '.join(r['nombre'] for r in activas)
    pendiente_actual_txt = _formatear_limite(pendiente_actual)

    mensaje = (
        f"Restricciones activas en el óptimo: {nombres}.\n"
        f"Pendiente actual de Z: {pendiente_actual_txt} (= -c₁/c₂).\n"
        f"Pendiente admisible: [{_formatear_limite(m_min)}] "
        f"a [{_formatear_limite(m_max)}].\n\n"
        f"c₁: {_formatear_mensaje(lim_inf_c1, lim_sup_c1)}\n"
        f"c₂: {_formatear_mensaje(lim_inf_c2, lim_sup_c2)}"
    )

    return {
        'limite_inferior_c1': lim_inf_c1,
        'limite_superior_c1': lim_sup_c1,
        'limite_inferior_c2': lim_inf_c2,
        'limite_superior_c2': lim_sup_c2,
        'pendiente_actual': pendiente_actual,
        'pendiente_min': m_min,
        'pendiente_max': m_max,
        'restricciones_activas': activas,
        'mensaje': mensaje,
    }
