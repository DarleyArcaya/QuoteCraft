import json
from pathlib import Path

class I18n:
    # Initialize the class with a language and the path to translation files
    # Inicializa la clase con un idioma y la ruta a los archivos de traducción
    def __init__(self, lang="es", subfolder="languages/app_language"):
        self.lang = lang
        self.subfolder = subfolder
        self.translations = self._load_translations()

    def _load_translations(self):
        # Determine the base path of the 'locales' folder
        # Determina la ruta base de la carpeta 'locales'
        base_path = Path(__file__).parent
        
        # Build the full path: locales / languages / app_language / es.json
        # Construye la ruta completa: locales / languages / app_language / es.json
        file_path = base_path / self.subfolder / f"{self.lang}.json"
        
        try:
            # Open and read the JSON file with UTF-8 encoding
            # Abre y lee el archivo JSON con codificación UTF-8
            with file_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            # Show an error if the file is missing or corrupted
            # Muestra un error si el archivo falta o está dañado
            print(f"Error: The language file was not found in: {file_path}")
            return {}

    def t(self, key, **kwargs):
        # Search for a translation key; if not found, return the key itself
        # Busca una clave de traducción; si no existe, devuelve la clave misma
        text = self.translations.get(key, key)
        try:
            # Format the text if dynamic variables are provided (e.g., names or amounts)
            # Formatea el texto si se pasan variables dinámicas (ej: nombres o montos)
            return text.format(**kwargs) if kwargs else text
        except (KeyError, ValueError):
            return text
    
    def set_lang(self, lang):
        # Change the current language and reload the translation dictionary
        # Cambia el idioma actual y recarga el diccionario de traducción
        self.lang = lang
        self.translations = self._load_translations()