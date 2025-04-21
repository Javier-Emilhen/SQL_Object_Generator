import os
from pathlib import Path
import sys

class utils:
    
    def open_path(path: str):
        os.startfile(path)
        
    def resource_path():
        if getattr(sys, 'frozen', False):
        # Ejecutable empaquetado (PyInstaller)
            base_path = Path(sys._MEIPASS)  # Ruta temporal donde PyInstaller extrae los archivos
        else:
        # Entorno de desarrollo
            base_path = Path(__file__).resolve().parent.parent  # Sube desde utils/ a src/

        config_path = base_path / "config" / "config.json"
        return config_path