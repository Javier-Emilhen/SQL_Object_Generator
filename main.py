import logging
import os
import sys
import flet as ft
from src.gui.app import main

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

if __name__ == "__main__":
    if hasattr(sys, '_MEIPASS'):
        os.environ['FLET_APP_HIDDEN'] = 'true'

    ft.app(target=main)