"""
utils/exportar_pdf.py
=====================
Generación del reporte PDF con los resultados del solver.
Incluye datos del problema, iteraciones y solución óptima.

Autor: JD Puerta
Versión: 1.0
"""

from datetime import datetime


def _encabezados_tableau(tableau, n_vars, nombres_vars=None):
    """
    Genera encabezados de columnas para un tableau (Simplex o Gran M).

    Args:
        tableau (np.ndarray): Matriz del tableau.
        n_vars (int): Número de variables de decisión.
        nombres_vars (list | None): Nombres del solver Gran M, si existen.

    Returns:
        list: Etiquetas de columnas incluyendo 'b'.
    """
    n_cols = tableau.shape[1]
    encabezados = []

    for j in range(n_cols - 1):
        if nombres_vars is not None and j < len(nombres_vars):
            encabezados.append(nombres_vars[j])
        elif j < n_vars:
            encabezados.append(f'x{j + 1}')
        else:
            encabezados.append(f's{j - n_vars + 1}')

    encabezados.append('b')
    return encabezados


def _formatear_celda(valor):
    """Formatea un valor del tableau; muestra M para coeficientes de penalización."""
    if abs(valor) > 1e5 and valor != 0:
        return 'M'
    return f'{valor:.3f}'


def exportar_reporte(ruta, problema, resultado):
    """
    Genera un reporte PDF con los resultados del solver.

    Args:
        ruta (str): Ruta completa donde se guardará el PDF.
        problema (dict): Información del problema con claves:
            - 'metodo': 'Simplex' o 'Gran M'
            - 'modo': 'max' o 'min'
            - 'c': lista de coeficientes de la F.O.
            - 'n_vars': número de variables
            - 'n_restricciones': número de restricciones
        resultado (dict): Resultado del solver con claves:
            - 'estado': estado de la solución
            - 'solucion': array de valores de variables
            - 'z': valor óptimo
            - 'iteraciones': lista de tableaux
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    )
    import numpy as np

    doc = SimpleDocTemplate(
        ruta,
        pagesize=letter,
        rightMargin=inch * 0.75,
        leftMargin=inch * 0.75,
        topMargin=inch * 0.75,
        bottomMargin=inch * 0.75
    )

    estilos = getSampleStyleSheet()
    elementos = []

    # --- Título ---
    estilo_titulo = ParagraphStyle(
        'Titulo',
        parent=estilos['Title'],
        fontSize=18,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=6
    )
    estilo_subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=estilos['Normal'],
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=20
    )
    estilo_seccion = ParagraphStyle(
        'Seccion',
        parent=estilos['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#16213e'),
        spaceBefore=16,
        spaceAfter=8
    )
    estilo_normal = ParagraphStyle(
        'Normal2',
        parent=estilos['Normal'],
        fontSize=10,
        spaceAfter=4
    )

    elementos.append(Paragraph("Simplex & Gran M Solver", estilo_titulo))
    elementos.append(Paragraph(
        f"Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        estilo_subtitulo
    ))

    # --- Datos del problema ---
    elementos.append(Paragraph("1. Datos del problema", estilo_seccion))

    modo_texto = "Maximizar" if problema['modo'] == 'max' else "Minimizar"
    metodo_texto = problema['metodo']

    elementos.append(Paragraph(f"<b>Método:</b> {metodo_texto}", estilo_normal))
    elementos.append(Paragraph(f"<b>Objetivo:</b> {modo_texto}", estilo_normal))
    elementos.append(Paragraph(
        f"<b>Variables de decisión:</b> {problema['n_vars']}",
        estilo_normal
    ))
    elementos.append(Paragraph(
        f"<b>Restricciones:</b> {problema['n_restricciones']}",
        estilo_normal
    ))

    # Función objetivo
    terms = []
    for i, ci in enumerate(problema['c']):
        terms.append(f"{ci}x{i+1}")
    fo_texto = " + ".join(terms).replace("+ -", "- ")
    elementos.append(Paragraph(
        f"<b>Función objetivo:</b> Z = {fo_texto}",
        estilo_normal
    ))
    elementos.append(Spacer(1, 12))

    # --- Solución óptima ---
    elementos.append(Paragraph("2. Solución óptima", estilo_seccion))

    estado = resultado['estado']
    if estado == 'optimo':
        solucion = resultado['solucion']
        z = resultado['z']

        datos_solucion = [['Variable', 'Valor']]
        for i, val in enumerate(solucion):
            datos_solucion.append([f'x{i+1}', f'{val:.6f}'])
        datos_solucion.append(['Z óptimo', f'{z:.6f}'])

        tabla_sol = Table(datos_solucion, colWidths=[2 * inch, 2 * inch])
        tabla_sol.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16213e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f4f8')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2),
             [colors.white, colors.HexColor('#f5f5f5')]),
        ]))
        elementos.append(tabla_sol)

    else:
        mensajes = {
            'no_acotado': 'El problema no está acotado (solución infinita).',
            'no_factible': 'El problema no tiene solución factible.',
            'no_converge': (
                'No se certificó optimalidad dentro del límite de iteraciones.'
            ),
        }
        elementos.append(Paragraph(
            f"<b>Estado:</b> {mensajes.get(estado, estado)}",
            estilo_normal
        ))

    # --- Iteraciones ---
    elementos.append(Paragraph("3. Iteraciones del tableau", estilo_seccion))

    iteraciones = resultado['iteraciones']
    n_vars = problema['n_vars']
    nombres_vars = resultado.get('nombres_vars')

    for idx, tableau in enumerate(iteraciones):
        elementos.append(Paragraph(
            f"<b>Iteración {idx}</b>",
            estilo_normal
        ))

        encabezados = _encabezados_tableau(tableau, n_vars, nombres_vars)
        n_cols = tableau.shape[1]

        datos_tabla = [encabezados]
        for fila in tableau:
            datos_tabla.append([_formatear_celda(val) for val in fila])

        # Etiquetas de filas
        n_filas = len(datos_tabla)
        etiquetas = ['']
        for i in range(n_filas - 2):
            etiquetas.append(f'R{i+1}')
        etiquetas.append('Z')

        for i, etq in enumerate(etiquetas):
            datos_tabla[i].insert(0, etq)

        col_width = 0.6 * inch
        tabla_it = Table(
            datos_tabla,
            colWidths=[0.4 * inch] + [col_width] * (n_cols)
        )
        tabla_it.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3460')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#0f3460')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
            ('ROWBACKGROUNDS', (1, 1), (-1, -1),
             [colors.white, colors.HexColor('#f0f0f0')]),
        ]))
        elementos.append(tabla_it)
        elementos.append(Spacer(1, 8))

    # Construir PDF
    doc.build(elementos)
