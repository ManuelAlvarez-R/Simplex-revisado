"""
gui/ventana_principal.py
========================
Ventana principal de la aplicación Simplex & Gran M Solver.

Autor: JD Puerta
Versión: 1.0
"""

import tkinter as tk
from tkinter import ttk
from gui.panel_entrada import PanelEntrada
from gui.panel_resultado import PanelResultado


class VentanaPrincipal(tk.Tk):
    """
    Ventana principal de la aplicación.

    Organiza la interfaz en dos paneles:
    entrada (izquierda) y resultados (derecha).
    """

    def __init__(self):
        super().__init__()
        self._configurar_estilos()
        self._configurar_ventana()
        self._construir_layout()

    def _configurar_estilos(self):
        """Configura el tema visual con ttk.Style."""
        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        BG     = '#f5f5f5'
        FG     = '#1a1a1a'
        ACCENT = '#2c5f9e'
        BG2    = '#ffffff'
        BORDER = '#cccccc'

        self.configure(bg=BG)

        self.style.configure('.',
            background=BG,
            foreground=FG,
            font=('Segoe UI', 10)
        )
        self.style.configure('TFrame', background=BG)
        self.style.configure('TLabel', background=BG, foreground=FG)
        self.style.configure('TLabelframe',
            background=BG,
            foreground=FG,
            bordercolor=BORDER,
            relief='groove'
        )
        self.style.configure('TLabelframe.Label',
            background=BG,
            foreground=ACCENT,
            font=('Segoe UI', 9, 'bold')
        )
        self.style.configure('TButton',
            background=ACCENT,
            foreground='white',
            padding=6,
            relief='flat'
        )
        self.style.map('TButton',
            background=[('active', '#1a4a7a')]
        )
        self.style.configure('TRadiobutton',
            background=BG,
            foreground=FG
        )
        self.style.configure('TCombobox',
            fieldbackground=BG2,
            background=BG2,
            foreground=FG
        )
        self.style.configure('TNotebook',
            background=BG,
            bordercolor=BORDER
        )
        self.style.configure('TNotebook.Tab',
            background='#e0e0e0',
            foreground=FG,
            padding=[8, 4]
        )
        self.style.map('TNotebook.Tab',
            background=[('selected', ACCENT)],
            foreground=[('selected', 'white')]
        )
        self.style.configure('TSeparator', background=BORDER)
        self.style.configure('TScrollbar',
            background=BORDER,
            troughcolor=BG
        )
        self.style.configure('Header.TLabel',
            font=('Segoe UI', 11, 'bold'),
            background=BG,
            foreground=FG
        )
        self.style.configure('Title.TLabel',
            font=('Segoe UI', 14, 'bold'),
            background='#1a1a2e',
            foreground='white'
        )
        self.style.configure('Z.TLabel',
            font=('Segoe UI', 13, 'bold'),
            background=BG,
            foreground=ACCENT
        )
        self.style.configure('Warn.TLabel',
            background=BG,
            foreground='#cc6600',
            font=('Segoe UI', 9)
        )
        self.style.configure('Green.TButton',
            background='#2e7d4f',
            foreground='white',
            font=('Segoe UI', 11, 'bold'),
            padding=8,
            relief='flat'
        )
        self.style.map('Green.TButton',
            background=[('active', '#1f5c38')]
        )
        self.style.configure('Purple.TButton',
            background='#5c35a0',
            foreground='white',
            font=('Segoe UI', 10, 'bold'),
            padding=6,
            relief='flat'
        )
        self.style.map('Purple.TButton',
            background=[('active', '#4a2980')]
        )
  

    def _configurar_ventana(self):
        """Configura título, tamaño y posición."""
        self.title("Simplex & Gran M Solver v1.0")
        self.geometry("1280x720")
        self.minsize(1000, 600)
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 640
        y = (self.winfo_screenheight() // 2) - 360
        self.geometry(f'+{x}+{y}')

    def _construir_layout(self):
        """Construye el layout con barra superior y dos paneles."""

        # Barra superior
        barra = tk.Frame(self, bg='#1e1e1e', height=45)
        barra.pack(fill='x', side='top')
        barra.pack_propagate(False)

        tk.Label(
            barra,
            text="⚙  Simplex & Gran M Solver",
            bg='#1e1e1e', fg='white',
            font=('Segoe UI', 13, 'bold')
        ).pack(side='left', padx=20, pady=10)

        tk.Label(
            barra,
            text="Programación Lineal",
            bg='#1e1e1e', fg='gray',
            font=('Segoe UI', 10)
        ).pack(side='right', padx=20, pady=10)

        # Contenedor principal
        contenedor = ttk.Frame(self)
        contenedor.pack(fill='both', expand=True, padx=10, pady=10)

        contenedor.columnconfigure(0, weight=2)
        contenedor.columnconfigure(1, weight=5)
        contenedor.rowconfigure(0, weight=1)

        # Panel entrada
        self.panel_entrada = PanelEntrada(
            contenedor,
            callback_resolver=self._on_resolver
        )
        self.panel_entrada.grid(
            row=0, column=0, sticky='nsew', padx=(0, 5)
        )

        # Panel resultado
        self.panel_resultado = PanelResultado(contenedor)
        self.panel_resultado.grid(
            row=0, column=1, sticky='nsew', padx=(5, 0)
        )

    def _on_resolver(self, problema, resultado):
        """Callback: recibe resultado del solver y lo muestra."""
        self.panel_resultado.mostrar_resultado(problema, resultado)
