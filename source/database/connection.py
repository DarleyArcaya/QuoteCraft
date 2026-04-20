import sqlite3 as sql
import sys
import pathlib as pl
import os

# --- PERMANENT PATH LOGIC | LÓGICA DE RUTA PERMANENTE ---

# Reference to the project root (used in development) | Referencia a la raíz del proyecto (usada en desarrollo)
_dev_path = pl.Path(__file__).resolve().parent.parent

# [CHANGE] Cross-platform persistent data directory.
# Windows → %APPDATA%\QuoteCraft
# macOS   → ~/Library/Application Support/QuoteCraft
# Linux   → ~/.local/share/QuoteCraft
#
# [CAMBIO] Directorio de datos persistente multiplataforma.
# Windows → %APPDATA%\QuoteCraft
# macOS   → ~/Library/Application Support/QuoteCraft
# Linux   → ~/.local/share/QuoteCraft
if sys.platform == "win32":
    _appdata_dir = pl.Path(os.environ["APPDATA"]) / "QuoteCraft"
elif sys.platform == "darwin":
    _appdata_dir = pl.Path.home() / "Library" / "Application Support" / "QuoteCraft"
else:
    _appdata_dir = pl.Path.home() / ".local" / "share" / "QuoteCraft"

# [CHANGE] _is_flet_build detection made cross-platform.
# On Windows, check if path starts with APPDATA.
# On macOS/Linux, flet build uses different paths — default to False in development.
#
# [CAMBIO] Detección de _is_flet_build hecha multiplataforma.
# En Windows, verifica si la ruta empieza con APPDATA.
# En macOS/Linux, flet build usa rutas diferentes — por defecto False en desarrollo.
if sys.platform == "win32":
    _is_flet_build = str(_dev_path).lower().startswith(os.environ.get("APPDATA", "").lower())
else:
    _is_flet_build = False

# If PyInstaller .exe, flet build, or any AppData execution → use persistent data folder
# Si es .exe de PyInstaller, flet build, o cualquier ejecución desde AppData → usar carpeta persistente
if getattr(sys, 'frozen', False) or _is_flet_build:
    BASE_DIR = _appdata_dir
else:
    # In development, save inside the project folder | En desarrollo, guardamos dentro de la carpeta del proyecto
    BASE_DIR = _dev_path

# Set the database path | Establece la ruta de la base de datos
DB_PATH = BASE_DIR / 'data' / 'estimate.db'

# Create the data folder if it doesn't exist | Crea la carpeta de datos si no existe
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def dict_factory(cursor, row):
    # Converts database rows into Python dictionaries | Convierte las filas de la DB en diccionarios de Python
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_connection():
    # Establishes connection to SQLite | Establece la conexión con SQLite
    conn = sql.connect(DB_PATH)
    conn.row_factory = dict_factory  # Enable dictionary mode | Habilita el modo de diccionario
    conn.execute('PRAGMA foreign_keys = ON')  # Enable foreign key support | Habilita soporte para claves foráneas
    return conn


def create_tables():
    # Create all necessary tables for the app | Crea todas las tablas necesarias para la app
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS income (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount      REAL NOT NULL,
            date        TEXT DEFAULT (date('now')),
            notes       TEXT
        );
                         
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount      REAL NOT NULL,
            date        TEXT DEFAULT (date('now')),
            notes       TEXT
        );
                         
        CREATE TABLE IF NOT EXISTS users (
            id              INTEGER PRIMARY KEY,
            name            TEXT NOT NULL,
            phone           TEXT,
            email           TEXT,
            address         TEXT,
            logo_path       TEXT,
            estimate_prefix TEXT DEFAULT 'EST',
            theme           TEXT DEFAULT 'dark',
            lang            TEXT DEFAULT 'es'
        );
                         
        CREATE TABLE IF NOT EXISTS clients (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL,
            phone     TEXT,
            email     TEXT,
            address   TEXT,
            logo_path TEXT
        );
        
        CREATE TABLE IF NOT EXISTS estimates (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL,
            phone     TEXT,
            email     TEXT,
            address   TEXT,
            create_at TEXT DEFAULT (date('now'))
        );
                   
        CREATE TABLE IF NOT EXISTS items (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            estimate_number TEXT NOT NULL UNIQUE,
            client_id       INTEGER NOT NULL,
            title           TEXT,
            description     TEXT,
            status          TEXT DEFAULT 'draft',
            notes           TEXT,
            created_at      TEXT DEFAULT (date('now')),
            valid_until     TEXT,
            tax_rate        REAL DEFAULT 0.0,
            subtotal        REAL DEFAULT 0.0,
            total           REAL DEFAULT 0.0,
            language        TEXT DEFAULT 'es',
            FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS estimate_items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            estimate_id INTEGER NOT NULL,
            category    TEXT,
            description TEXT,
            quantity    REAL NOT NULL,
            unit        TEXT,
            unit_price  REAL NOT NULL,
            FOREIGN KEY (estimate_id) REFERENCES items(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS expense_items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_id  INTEGER NOT NULL,
            description TEXT NOT NULL,
            amount      REAL NOT NULL,
            FOREIGN KEY (expense_id) REFERENCES expenses(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT NOT NULL,
            type        TEXT NOT NULL,
            description TEXT NOT NULL,
            color       TEXT DEFAULT '#f0a500',
            time        TEXT DEFAULT ''
        );
    ''')

    # --- MIGRATIONS | MIGRACIONES ---
    # Add new columns if they don't exist in older DB versions | Añade columnas nuevas si no existen en versiones viejas de la DB
    try: conn.execute("ALTER TABLE users ADD COLUMN estimate_prefix TEXT DEFAULT 'EST'")
    except: pass
    try: conn.execute("ALTER TABLE users ADD COLUMN theme TEXT DEFAULT 'dark'")
    except: pass
    try: conn.execute("ALTER TABLE users ADD COLUMN lang TEXT DEFAULT 'es'")
    except: pass
    try: conn.execute("ALTER TABLE users ADD COLUMN logo_path TEXT")
    except: pass
    try: conn.execute("ALTER TABLE events ADD COLUMN time TEXT DEFAULT ''")
    except: pass
    try: conn.execute("ALTER TABLE items ADD COLUMN language TEXT DEFAULT 'es'")
    except: pass

    # Ensure at least one admin user exists for settings | Asegura que exista al menos un usuario admin para ajustes
    user_exists = conn.execute("SELECT id FROM users WHERE id = 1").fetchone()
    if not user_exists:
        conn.execute("INSERT INTO users (id, name, lang, theme) VALUES (1, '', 'es', 'dark')")

    conn.commit()
    conn.close()


# --- PERSISTENCE FUNCTIONS | FUNCIONES DE PERSISTENCIA ---

def get_user_language():
    """Gets the saved user language (id=1) | Obtiene el idioma guardado del usuario (id=1)"""
    try:
        conn = get_connection()
        user = conn.execute("SELECT lang FROM users WHERE id = 1").fetchone()
        conn.close()
        return user['lang'] if user and 'lang' in user else "es"
    except:
        return "es"

def save_user_language(lang):
    """Saves the preferred language to the database | Guarda el idioma preferido en la base de datos"""
    conn = get_connection()
    conn.execute("UPDATE users SET lang = ? WHERE id = 1", (lang,))
    conn.commit()
    conn.close()

def save_logo_path(path):
    """Saves the company logo path to the database | Guarda la ruta del logo de la empresa en la base de datos"""
    conn = get_connection()
    conn.execute("UPDATE users SET logo_path = ? WHERE id = 1", (path,))
    conn.commit()
    conn.close()

def get_logo_path():
    """Retrieves the saved company logo path | Recupera la ruta guardada del logo de la empresa"""
    try:
        conn = get_connection()
        user = conn.execute("SELECT logo_path FROM users WHERE id = 1").fetchone()
        conn.close()
        return user['logo_path'] if user else None
    except:
        return None