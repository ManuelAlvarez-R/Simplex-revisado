"""
main.py
=======
Punto de entrada de la aplicación Simplex & Gran M Solver.

Ejecutar con:
    python main.py

Autor: JD Puerta
Versión: 1.0
"""

import sys
import traceback


def main():
    """Inicializa y lanza la ventana principal de la aplicación."""
    try:
        from gui.ventana_principal import VentanaPrincipal
        app = VentanaPrincipal()
        app.mainloop()
    except Exception:
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
        sys.exit(1)


if __name__ == "__main__":
    main()