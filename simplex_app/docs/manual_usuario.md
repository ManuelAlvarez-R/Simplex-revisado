# Manual de usuario rápido — Simplex & Gran M Solver

**Versión:** 1.0  
**Aplicación:** Simplex & Gran M Solver (programación lineal)

---

## 1. Qué hace la aplicación

Resuelve problemas de **programación lineal**: maximizar o minimizar una función objetivo sujeta a restricciones lineales. Ofrece:

- **Método Simplex** — solo restricciones `<=`
- **Método Gran M** — restricciones `<=`, `>=` e `=`

Además muestra:

- Tableaux de cada iteración (con pivote resaltado)
- Solución óptima y valor de Z
- Análisis de sensibilidad (holguras e intervalos)
- Gráfica 2D y **todos los vértices** factibles (solo con 2 variables)
- Exportación de reporte en PDF

---

## 2. Requisitos e inicio

**Necesitas:** Python 3.x y las librerías `numpy`, `matplotlib` y `reportlab`.

```bash
pip install numpy matplotlib reportlab
cd simplex_app
python main.py
```

Se abre una ventana con dos zonas: **entrada (izquierda)** y **resultados (derecha)**.

Si usas el ejecutable generado con PyInstaller, basta con abrir el `.exe`; no hace falta la consola.

---

## 3. Pantalla principal

| Zona               | Contenido                                          |
|------              |-----------                                         |
| **Izquierda**      | Definir el problema y pulsar **Resolver**          |
| **Derecha**        | Solución, iteraciones, sensibilidad, gráfica y PDF |
| **Barra superior** | Título de la aplicación                            |

En el panel derecho puedes usar la **rueda del ratón** para desplazarte si hay mucho contenido.

---

## 4. Paso a paso: resolver un problema

### Paso 1 — Dimensiones

1. En **Dimensiones**, indica:
   - **Variables** (por ejemplo `2`)
   - **Restricciones** (por ejemplo `2`)
2. Pulsa **Generar tabla**.

La tabla de coeficientes se redibuja según esos números.

### Paso 2 — Función objetivo y método

- **Objetivo:** elige **Maximizar** o **Minimizar**.
- **Método:**
  - **Simplex** si todas las restricciones son `<=`
  - **Gran M** si hay `>=` o `=`

Si alguna restricción no es `<=`, la opción Simplex se desactiva automáticamente y aparece el aviso: *"Simplex solo acepta restricciones <="*.

### Paso 3 — Coeficientes

En la tabla **Coeficientes**:

| Fila          | Significado                                     |
|------         |-------------                                    |
| **Z**         | Coeficientes de la función objetivo (c₁, c₂, …) |
| **R1, R2, …** | Coeficientes de cada restricción                |
| **Tipo**      | `<=`, `>=` o `=`                                |  
| **b**         | Término independiente (lado derecho)            |

**Formato del problema en la app:**

```
Optimizar  Z = c₁x₁ + c₂x₂ + …
Sujeto a   aᵢ₁x₁ + aᵢ₂x₂ + …  {≤, ≥, =}  bᵢ
```

**Reglas de entrada:**

- Solo números (enteros o decimales).
- Los valores de **b deben ser ≥ 0**.

### Paso 4 — Resolver

Pulsa **▶ Resolver**.

- Si hay error de datos, aparece un mensaje (número inválido, b negativo, etc.).
- Si todo es correcto, los resultados se muestran a la derecha.

### Paso 5 — Limpiar (opcional)

**🗑 Limpiar** pone todos los coeficientes en `0` sin cambiar el tamaño de la tabla.

---

## 5. Panel de resultados

### Solución óptima

Muestra el método usado, si es max o min, los valores de x₁, x₂, … y **Z óptimo**.

### Iteraciones del tableau

Pestañas **Inicial**, **Iteración 1**, **Iteración 2**, etc.:

- **Columna y fila resaltadas** — pivote de esa iteración
- **Entra / Sale** — variable entrante y saliente
- Valores muy grandes se muestran como **M** (penalización en Gran M)

### Análisis de sensibilidad

- **Holgura** de cada restricción e indicación si está **activa** (rojo) o **no activa** (verde).
- Cálculo de intervalos:
  - **Análisis de recursos (bᵢ)** — rango del lado derecho de una restricción
  - **Análisis de coeficientes (cᵢ)** — rango del costo de una variable básica
  - **Análisis gráfico de pendientes** — solo con 2 variables; intervalos de c₁ y c₂

Pasos: elige el tipo de análisis → selecciona restricción o variable (si aplica) → **Calcular**.

### Gráfica 2D (solo con 2 variables)

- Región factible en verde (si está acotada)
- Rectas de restricciones
- **Vértices** en morado
- **Punto óptimo** en dorado, con coordenadas
- Recta de **isoutilidad** con el Z óptimo
- Líneas de pendientes mín/máx. en análisis gráfico de sensibilidad (cuando aplica)

### Vértices factibles

Lista de **todos** los vértices de la región factible. El vértice óptimo lleva la marca **★ Óptimo**.

### Exportar PDF

Pulsa **📄 Exportar reporte PDF**, elige carpeta y nombre de archivo. El PDF incluye datos del problema, solución e iteraciones del tableau.

---

## 6. Mensajes especiales

| Mensaje                   | Significado                                              |
|---------                  |-------------                                             |
| **Problema no factible**  | No existe solución que cumpla todas las restricciones    |
| **Problema no acotado**   | La función objetivo puede mejorar sin límite             |
| **Sin convergencia**      | Se alcanzó el límite de iteraciones; revisa los tableaux |
| **Simplex desactivado**   | Hay restricciones `>=` o `=`; usa Gran M                 |

---

## 7. Ejemplo rápido (2 variables, Simplex)

**Maximizar** Z = 3x₁ + 2x₂

- x₁ + x₂ ≤ 4
- 2x₁ + x₂ ≤ 6
- x₁, x₂ ≥ 0 (implícito en la gráfica)

|    | x₁| x₂| Tipo | b |
|--- |---|---|------|---|
| Z  | 3 | 2 | —    | — |
| R1 | 1 | 1 | <=   | 4 |
| R2 | 2 | 1 | <=   | 6 |

1. Variables: **2**, Restricciones: **2** → **Generar tabla**
2. Rellenar la tabla como arriba
3. Método: **Simplex**, Objetivo: **Maximizar**
4. **Resolver**

**Resultado esperado:** x₁ = 2, x₂ = 2, Z = 10.

---

## 8. Consejos prácticos

1. Tras cambiar el número de variables o restricciones, pulsa de nuevo **Generar tabla**.
2. Si usas `>=` o `=`, selecciona **Gran M**.
3. La gráfica y la lista de vértices solo aparecen con **2 variables** y cuando hay solución **óptima**.
4. Problemas con muchas variables o restricciones generan muchas pestañas de iteración; usa el scroll del panel derecho.
5. Para depuración con código fuente: `python main.py` desde la carpeta `simplex_app`.

---

## 9. Limitaciones

- La gráfica asume **x₁ ≥ 0** y **x₂ ≥ 0**.
- El método Simplex de la app está limitado a restricciones **<=**.
- Si la región es **no acotada**, puede no dibujarse un polígono cerrado y haber pocos vértices.
- El análisis de sensibilidad por tableau es más fiable en problemas resueltos con Simplex; con Gran M, coeficientes muy grandes (M) pueden afectar algunos intervalos.

---

## 10. Estructura de carpetas (referencia)

```
simplex_app/
├── main.py              ← ejecutar la app
├── README.md
├── docs/
│   ├── manual_usuario.md   ← este archivo
│   └── requisitos.md
├── gui/                 ← interfaz
├── solver/              ← Simplex y Gran M
└── utils/               ← validaciones, PDF, vértices 2D
```

---

*Autores del proyecto: Juan David Puerta Palacio, Manuel Felipe Alvarez Rua y Oscar Alberto Plaza* 
