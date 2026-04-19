import flet as ft
from database import connection
from database import queries
from views.home import HomeView
from locales.i18n import I18n
import ctypes
import os
import sys

# --- 1. SET APPLICATION ID | CONFIGURAR ID DE LA APLICACIÓN ---
# Ensures Windows recognizes the app for taskbar grouping | Asegura que Windows reconozca la app para agruparla en la barra de tareas.
if os.name == 'nt':
    try:
        myappid = 'Darley.QuoteCraft.App.v1.1.0' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

def main(page: ft.Page):
    # --- 2. MANAGE ASSET PATHS | GESTIÓN DE RUTAS DE RECURSOS ---
    # Check if app is running as .exe (frozen) or .py script | Verifica si la app corre como .exe o como script .py.
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS # Path for compiled executable | Ruta para el ejecutable compilado.
    else:
        base_path = os.path.abspath(".") # Path for regular execution | Ruta para ejecución normal.
    
    icon_path = os.path.join(base_path, "assets", "favicon.ico")

    # --- 3. WINDOW CONFIGURATION | CONFIGURACIÓN DE LA VENTANA ---
    page.title = "QuoteCraft"
    if os.path.exists(icon_path):
        page.window.icon = icon_path # Set the app icon | Establece el icono de la app.
    
    # Set window size and behavior | Define el tamaño y comportamiento de la ventana.
    page.window.maximized = True
    page.window.width = 1100
    page.window.height = 750
    page.padding = 0
    
    # Initialize database and ensure tables exist | Inicializa la base de datos y asegura que las tablas existan.
    connection.create_tables()

    # --- SMART PERSISTENCE LOGIC | LÓGICA DE PERSISTENCIA INTELIGENTE ---
    # 1. Get language preference from DB | Obtener preferencia de idioma de la DB.
    db_lang = connection.get_user_language()

    # 2. DECISION: If DB is empty, use English. If not, use DB value | DECISIÓN: Si la DB está vacía, usa Inglés. Si no, usa el valor de la DB.
    if db_lang is None or db_lang == "":
        current_lang = "en"
        # Save "en" to initialize the DB | Guardar "en" para inicializar la DB.
        connection.update_user_language("en")
    else:
        current_lang = db_lang

    # 3. Store global data (theme/i18n) in page.data | Guardar datos globales (tema/i18n) en page.data.
    page.data = {
        "theme": queries.get_theme_preference() or "dark", 
        "i18n": I18n(lang=current_lang) 
    }

    # Set colors based on theme preference | Configurar colores según la preferencia de tema.
    if page.data["theme"] == "light":
        page.bgcolor = "#f5f5f5"
        page.theme_mode = ft.ThemeMode.LIGHT
    else:
        page.bgcolor = "#0d0f14"
        page.theme_mode = ft.ThemeMode.DARK

    # Load initial Home View | Cargar la vista de inicio inicial.
    page.add(HomeView(page))
    page.update()

# Start the application | Iniciar la aplicación.
if __name__ == "__main__":
    ft.run(main, assets_dir="assets")