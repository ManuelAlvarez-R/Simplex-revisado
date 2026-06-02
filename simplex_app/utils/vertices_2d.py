"""
utils/vertices_2d.py
====================
Enumeración exhaustiva de vértices factibles para problemas
de programación lineal con 2 variables y no negatividad (x₁, x₂ ≥ 0).

No modifica el solver; solo geometría para la visualización.
"""

import numpy as np

TOL = 1e-9


def punto_cumple_restricciones(px, py, A, b, tipos, tol=TOL):
    """
    Verifica si (px, py) satisface todas las restricciones del problema.

    Args:
        px, py (float): Coordenadas del punto.
        A (array-like): Matriz de restricciones 2D.
        b (array-like): Términos independientes.
        tipos (list): Tipos por fila ('<=', '>=', '=').
        tol (float): Tolerancia numérica.

    Returns:
        bool: True si el punto es factible.
    """
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)

    for fila, bi, tipo in zip(A, b, tipos):
        lhs = fila[0] * px + fila[1] * py
        if tipo == '<=' and lhs > bi + tol:
            return False
        if tipo == '>=' and lhs < bi - tol:
            return False
        if tipo == '=' and abs(lhs - bi) > tol:
            return False
    return True


def _deduplicar_vertices(puntos, decimales=6):
    """
    Elimina vértices duplicados usando redondeo.

    Args:
        puntos (list): Lista de tuplas (x, y).
        decimales (int): Precisión para comparar.

    Returns:
        list: Vértices únicos ordenados lexicográficamente.
    """
    unicos = []
    vistos = set()

    for px, py in puntos:
        clave = (round(float(px), decimales), round(float(py), decimales))
        if clave not in vistos:
            vistos.add(clave)
            unicos.append(clave)

    return sorted(unicos)


def enumerar_vertices_factibles_2d(A, b, tipos, tol=TOL):
    """
    Encuentra todos los vértices del poliedro factible en 2D.

    Un vértice es la intersección de dos fronteras activas entre:
    - x₁ = 0, x₂ = 0 (no negatividad)
    - aᵢ₁x₁ + aᵢ₂x₂ = bᵢ para cada restricción (línea frontera)

    Args:
        A (array-like): Matriz de restricciones (m × 2).
        b (array-like): Vector de términos independientes.
        tipos (list): Tipos de restricción por fila.
        tol (float): Tolerancia numérica.

    Returns:
        list: Vértices factibles únicos como [(x₁, x₂), ...].
    """
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)

    # Fronteras: ejes + rectas de cada restricción
    lineas = [
        (np.array([1.0, 0.0]), 0.0),   # x₁ = 0
        (np.array([0.0, 1.0]), 0.0),   # x₂ = 0
    ]
    for fila, bi in zip(A, b):
        lineas.append((np.array(fila, dtype=float), float(bi)))

    candidatos = []
    n_lineas = len(lineas)

    for i in range(n_lineas):
        for j in range(i + 1, n_lineas):
            c1, r1 = lineas[i]
            c2, r2 = lineas[j]
            matriz = np.array([c1, c2])

            if abs(np.linalg.det(matriz)) < tol:
                continue

            try:
                punto = np.linalg.solve(matriz, np.array([r1, r2]))
                candidatos.append((float(punto[0]), float(punto[1])))
            except np.linalg.LinAlgError:
                continue

    factibles = []
    for px, py in candidatos:
        if px < -tol or py < -tol:
            continue
        if punto_cumple_restricciones(px, py, A, b, tipos, tol):
            factibles.append((px, py))

    return _deduplicar_vertices(factibles)


def ordenar_vertices_poligono(vertices):
    """
    Ordena vértices en sentido antihorario para dibujar el polígono factible.

    Args:
        vertices (list): Lista de (x, y).

    Returns:
        np.ndarray: Array (n, 2) ordenado, o None si hay menos de 3 puntos.
    """
    if len(vertices) < 3:
        return None

    puntos = np.array(vertices, dtype=float)
    centro = puntos.mean(axis=0)
    angulos = np.arctan2(
        puntos[:, 1] - centro[1],
        puntos[:, 0] - centro[0],
    )
    orden = np.argsort(angulos)
    return puntos[orden]
