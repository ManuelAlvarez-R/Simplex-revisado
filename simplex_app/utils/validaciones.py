"""
utils/validaciones.py
=====================
Funciones de validación para las entradas del usuario
antes de pasarlas al solver.

Autor: JD Puerta
Versión: 1.0
"""


def validar_coeficientes(valores):
    """
    Verifica que una lista de strings sean números válidos.

    Args:
        valores (list): Lista de strings ingresados por el usuario.

    Returns:
        tuple: (bool, str) — (True, '') si válido,
               (False, mensaje_error) si inválido.
    """
    for v in valores:
        try:
            float(v.strip())
        except ValueError:
            return False, f"'{v}' no es un número válido."
    return True, ''


def validar_dimensiones(n_vars, n_restricciones):
    """
    Verifica que el número de variables y restricciones sea válido.

    Args:
        n_vars (int): Número de variables de decisión.
        n_restricciones (int): Número de restricciones.

    Returns:
        tuple: (bool, str) — (True, '') si válido,
               (False, mensaje_error) si inválido.
    """
    if n_vars < 1:
        return False, "Debe haber al menos 1 variable."
    if n_restricciones < 1:
        return False, "Debe haber al menos 1 restricción."
    return True, ''


def validar_terminos_independientes(valores):
    """
    Verifica que los términos independientes (b) sean no negativos.

    Args:
        valores (list): Lista de strings con los valores de b.

    Returns:
        tuple: (bool, str) — (True, '') si válido,
               (False, mensaje_error) si inválido.
    """
    for v in valores:
        try:
            num = float(v.strip())
            if num < 0:
                return False, f"El término independiente '{v}' debe ser >= 0."
        except ValueError:
            return False, f"'{v}' no es un número válido."
    return True, ''


def validar_problema_completo(c, A, b, tipos):
    """
    Valida el problema completo antes de enviarlo al solver.

    Args:
        c (list): Coeficientes de la función objetivo (strings).
        A (list): Matriz de restricciones (lista de listas de strings).
        b (list): Términos independientes (strings).
        tipos (list): Tipos de restricción ('<=', '>=', '=').

    Returns:
        tuple: (bool, str) — (True, '') si todo válido,
               (False, mensaje_error) si hay algún problema.
    """
    # Validar función objetivo
    ok, msg = validar_coeficientes(c)
    if not ok:
        return False, f"Función objetivo: {msg}"

    # Validar cada fila de restricciones
    for i, fila in enumerate(A):
        ok, msg = validar_coeficientes(fila)
        if not ok:
            return False, f"Restricción {i+1}: {msg}"

    # Validar términos independientes
    ok, msg = validar_terminos_independientes(b)
    if not ok:
        return False, f"Término independiente: {msg}"

    # Validar tipos
    tipos_validos = {'<=', '>=', '='}
    for i, t in enumerate(tipos):
        if t not in tipos_validos:
            return False, f"Restricción {i+1}: tipo '{t}' no válido."

    return True, ''
