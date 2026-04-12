# Dark mode color palette | Paleta de colores para el modo oscuro
DARK = {
    "bg":       "#0d0f14", # Main background | Fondo principal
    "surface":  "#13161e", # Cards and containers | Tarjetas y contenedores
    "surface2": "#1a1e2a", # Secondary surfaces | Superficies secundarias
    "border":   "#252836", # Borders and dividers | Bordes y divisores
    "text":     "#e2ddd6", # Primary text | Texto principal
    "text2":    "#8b8fa8", # Secondary text | Texto secundario
    "text3":    "#3a3f52", # Disabled or subtle text | Texto deshabilitado o sutil
    "accent":   "#f0a500", # QuoteCraft brand color | Color de marca QuoteCraft
}

# Light mode color palette | Paleta de colores para el modo claro
LIGHT = {
    "bg":       "#f5f5f5",
    "surface":  "#ffffff",
    "surface2": "#f0f0f0",
    "border":   "#dddddd",
    "text":     "#111111",
    "text2":    "#555555",
    "text3":    "#888888",
    "accent":   "#d97700", # Slightly darker orange for better contrast | Naranja un poco más oscuro para mejor contraste
}

def get_theme(mode):
    """
    Returns the dictionary of colors based on the selected mode.
    Retorna el diccionario de colores basado en el modo seleccionado.
    """
    return DARK if mode == "dark" else LIGHT