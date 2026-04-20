import flet as ft
from database import connection
from database import queries
from views.home import HomeView
from locales.i18n import I18n
import ctypes
import os
import sys

# [CHANGE] Added for update checker — requests fetches version.json from GitHub,
# threading runs the check in background without blocking the UI startup.
# [CAMBIO] Agregado para el verificador de actualizaciones — requests obtiene version.json
# de GitHub, threading corre la verificación en segundo plano sin bloquear el arranque de la UI.
import requests
import threading

# --- 1. SET APPLICATION ID | CONFIGURAR ID DE LA APLICACIÓN ---
# Ensures Windows recognizes the app for taskbar grouping | Asegura que Windows reconozca la app para agruparla en la barra de tareas.
if os.name == 'nt':
    try:
        myappid = 'Darley.QuoteCraft.App.v1.2.0' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

# [CHANGE] Current app version — update this string with every release so the
# checker can compare it against the latest version in GitHub's version.json.
# [CAMBIO] Versión actual de la app — actualizar este string con cada release para
# que el checker pueda compararlo contra la última versión en version.json de GitHub.
CURRENT_VERSION = "1.2.0"

# [CHANGE] URL to the raw version.json file hosted on GitHub.
# This file only contains the latest version number and the Mega download link.
# Update version.json on GitHub whenever a new release is published — never put the .exe here.
# [CAMBIO] URL al archivo version.json alojado en GitHub (raw).
# Este archivo solo contiene el número de versión más reciente y el link de descarga en Mega.
# Actualiza version.json en GitHub cuando publiques un nuevo release — nunca subas el .exe aquí.
VERSION_URL = "https://raw.githubusercontent.com/DarleyArcaya/QuoteCraft/main/version.json"

def check_for_updates(page: ft.Page):
    """
    [CHANGE] Runs in a background daemon thread at app startup.
    Fetches version.json from GitHub and compares it to CURRENT_VERSION.
    If a newer version exists, stores the info in page.data so HomeView
    can display the update banner without any extra work.
    If there is no internet or the request fails for any reason,
    the exception is silently caught and the app continues normally.

    [CAMBIO] Corre en un hilo daemon en segundo plano al arrancar la app.
    Obtiene version.json de GitHub y lo compara con CURRENT_VERSION.
    Si existe una versión más nueva, guarda la info en page.data para que
    HomeView pueda mostrar el banner de actualización sin trabajo extra.
    Si no hay internet o la petición falla por cualquier razón, la excepción
    se captura silenciosamente y la app continúa con normalidad.
    """
    try:
        response = requests.get(VERSION_URL, timeout=5)
        data = response.json()
        latest_version = data["version"]
        download_url   = data["download_url"]

        if latest_version != CURRENT_VERSION:
            # Store update info in page.data for HomeView to pick up
            # Guardar info de actualización en page.data para que HomeView la use
            page.data["update_available"] = True
            page.data["update_version"]   = latest_version
            page.data["update_url"]       = download_url
    except:
        # No internet, timeout, or malformed JSON — continue silently
        # Sin internet, timeout, o JSON malformado — continuar silenciosamente
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
        "i18n": I18n(lang=current_lang),
        # [CHANGE] Initialize update keys as None — check_for_updates will populate
        # them if a newer version is found. HomeView reads these to show the banner.
        # [CAMBIO] Inicializar las keys de actualización como None — check_for_updates
        # las llenará si encuentra una versión más nueva. HomeView las lee para mostrar el banner.
        "update_available": False,
        "update_version":   None,
        "update_url":       None,
    }

    # Set colors based on theme preference | Configurar colores según la preferencia de tema.
    if page.data["theme"] == "light":
        page.bgcolor = "#f5f5f5"
        page.theme_mode = ft.ThemeMode.LIGHT
    else:
        page.bgcolor = "#0d0f14"
        page.theme_mode = ft.ThemeMode.DARK

    # [CHANGE] Launch update checker in a background daemon thread.
    # daemon=True ensures the thread dies automatically when the app closes.
    # [CAMBIO] Lanzar el verificador de actualizaciones en un hilo daemon en segundo plano.
    # daemon=True asegura que el hilo muera automáticamente cuando la app se cierra.
    threading.Thread(
        target=check_for_updates,
        args=(page,),
        daemon=True
    ).start()

    # Load initial Home View | Cargar la vista de inicio inicial.
    page.add(HomeView(page))
    page.update()

# Start the application | Iniciar la aplicación.
if __name__ == "__main__":
    ft.run(main, assets_dir="assets")