# Documento de Requisitos — Simplex & Gran M Solver
**Versión:** 1.0  
**Fecha:** Mayo 2026  
**Autor:** JD Puerta  

---

## 1. Descripción general

Aplicación de escritorio en Python para resolver problemas de 
Programación Lineal mediante el método Simplex estándar y el 
método de la Gran M. Permite maximizar y minimizar funciones 
objetivo con n variables y m restricciones.

---

## 2. Requisitos funcionales

| ID    | Descripción |
|-------|-------------|
| RF01  | Ingresar función objetivo (maximizar o minimizar) |
| RF02  | Ingresar restricciones con operadores ≤, ≥, = |
| RF03  | Resolver por método Simplex estándar |
| RF04  | Resolver por método Gran M |
| RF05  | Mostrar tablas intermedias de cada iteración |
| RF06  | Mostrar la solución óptima (valores de variables + Z) |
| RF07  | Indicar si el problema es no acotado o no factible |
| RF08  | Mostrar gráfica 2D de región factible (solo 2 variables) |
| RF09  | Sin límite fijo de variables ni restricciones |
| RF10  | Exportar reporte en PDF con iteraciones y solución óptima |

---

## 3. Requisitos no funcionales

| ID     | Descripción |
|--------|-------------|
| RNF01  | Interfaz gráfica de escritorio (Windows) |
| RNF02  | Código documentado con docstrings |
| RNF03  | Estructura modular (archivos separados por responsabilidad) |
| RNF04  | README con instrucciones de instalación y uso |

---

## 4. Tecnologías

| Componente      | Tecnología        |
|-----------------|-------------------|
| Lenguaje        | Python 3.13       |
| GUI             | CustomTkinter     |
| Álgebra lineal  | NumPy             |
| Gráficas        | Matplotlib        |
| Exportar PDF    | ReportLab         |

---

## 5. Estructura del proyecto
simplex_app/
├── main.py
├── README.md
├── gui/
│   ├── ventana_principal.py
│   ├── panel_entrada.py
│   └── panel_resultado.py
├── solver/
│   ├── simplex.py
│   └── gran_m.py
├── utils/
│   ├── validaciones.py
│   └── exportar_pdf.py
├── docs/
│   └── requisitos.md
└── assets/
---

## 6. Flujo de uso

1. El usuario define número de variables y restricciones
2. Presiona "Generar tabla" → aparece grilla editable
3. Ingresa coeficientes de F.O. y restricciones
4. Selecciona método (Simplex / Gran M) y objetivo (Max / Min)
5. Presiona "Resolver"
6. El panel derecho muestra iteraciones y solución óptima
7. Si hay 2 variables, aparece la gráfica 2D
8. Puede exportar el reporte en PDF
