import json
import logging
import os
import uuid
import hashlib
import base64
from pathlib import Path
import shutil
import sys
from cryptography.fernet import Fernet
from src.utils.utils import utils

logger = logging.getLogger(__name__)

_APP_SALT = b"SQLObjectGenerator_v1_salt"
_ENCRYPTED_PREFIX = "enc:"

def _get_machine_key() -> Fernet:
    mac_bytes = uuid.getnode().to_bytes(6, byteorder='big')
    key_material = hashlib.pbkdf2_hmac('sha256', mac_bytes, _APP_SALT, iterations=100_000, dklen=32)
    return Fernet(base64.urlsafe_b64encode(key_material))

class settings:

    _instance = None
    _config_cache: dict | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.config_path = self.ensure_config_available()
            self._initialized = True

    # ── Config cache helpers ──────────────────────────────────────────────────

    def _load_config(self) -> dict:
        if settings._config_cache is None:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                settings._config_cache = json.load(f)
        return settings._config_cache

    def _save_config(self, config: dict):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        settings._config_cache = config

    # ── DB config ─────────────────────────────────────────────────────────────

    def get_config_file_path(self):
        return self.config_path

    def get_db_config(self):
        config = self._load_config()
        db_config = dict(config.get("db_config", {}))
        db_config["password"] = self._decrypt_password(db_config.get("password", ""))
        return db_config

    def save_db_config(self, server: str, username: str, password: str, database: str):
        config = self._load_config()
        config["db_config"] = {
            "server": server,
            "username": username,
            "password": self._encrypt_password(password),
            "database": database
        }
        self._save_config(config)

    def _encrypt_password(self, plaintext: str) -> str:
        if not plaintext:
            return plaintext
        token = _get_machine_key().encrypt(plaintext.encode("utf-8"))
        return _ENCRYPTED_PREFIX + token.decode("utf-8")

    def _decrypt_password(self, stored: str) -> str:
        if not stored or not stored.startswith(_ENCRYPTED_PREFIX):
            return stored
        token = stored[len(_ENCRYPTED_PREFIX):].encode("utf-8")
        try:
            return _get_machine_key().decrypt(token).decode("utf-8")
        except Exception as ex:
            logger.warning("Password decryption failed (possibly different machine): %s", ex)
            return ""

    def get_db_name(self):
        return self.get_db_config()["database"]

    def get_server_name(self):
        return self.get_db_config()["server"]

    def is_configured(self):
        db_config = self.get_db_config()
        return all(v not in [None, ""] for v in db_config.values())

    # ── Download path ─────────────────────────────────────────────────────────

    def get_download_path(self):
        return self._load_config().get("download_path", "")

    def set_download_path(self, new_path):
        config = self._load_config()
        config["download_path"] = new_path
        self._save_config(config)

    # ── App paths ─────────────────────────────────────────────────────────────

    def get_user_config_path(self):
        appdata_dir = os.path.join(os.getenv("APPDATA"), "SQLObjectGenerator")
        os.makedirs(appdata_dir, exist_ok=True)
        return os.path.join(appdata_dir, "config.json")

    def get_installed_config_path(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        return os.path.join(base_path, "config.json")

    def ensure_config_available(self):
        user_config = self.get_user_config_path()
        if not os.path.exists(user_config):
            original_config = self.get_installed_config_path()
            shutil.copy2(original_config, user_config)
        return user_config
