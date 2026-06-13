import logging
import threading
import pyodbc
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from src.config.config import settings

logger = logging.getLogger(__name__)

class sql_class:

    _engine_cache: dict = {}
    _cache_lock = threading.Lock()

    def __init__(self):
        self.engine = None
        self.server = None
        self.database = None
        self.username = None
        self.password = None

        self.load_sql_data()

    def load_sql_data(self):

        config = settings()
        db_config = config.get_db_config()

        self.server = db_config["server"]
        self.username = db_config["username"]
        self.password = db_config["password"]
        self.database = db_config["database"]
        self.engine = None

    @staticmethod
    def _get_driver() -> str:
        installed = pyodbc.drivers()
        for preferred in [
            "ODBC Driver 18 for SQL Server",
            "ODBC Driver 17 for SQL Server",
            "SQL Server Native Client 11.0",
            "SQL Server",
        ]:
            if preferred in installed:
                return preferred
        raise Exception(f"No SQL Server ODBC driver found. Installed drivers: {installed}")

    @staticmethod
    def _build_url(server, username, password, database) -> URL:
        return URL.create(
            "mssql+pyodbc",
            username=username,
            password=password,
            host=server,
            database=database,
            query={
                "driver": sql_class._get_driver(),
                "TrustServerCertificate": "yes",
            },
        )

    def connect(self):
        if not all(v not in [None, ""] for v in [self.server, self.username, self.password, self.database]):
            raise Exception("The SQL configuration is required, go to the settings button below (Settings).")

        url = self._build_url(self.server, self.username, self.password, self.database)
        with sql_class._cache_lock:
            key = url.render_as_string(hide_password=False)
            if key not in sql_class._engine_cache:
                sql_class._engine_cache[key] = create_engine(url, pool_pre_ping=True)
            self.engine = sql_class._engine_cache[key]

    @classmethod
    def invalidate_cache(cls):
        with cls._cache_lock:
            for engine in cls._engine_cache.values():
                try:
                    engine.dispose()
                except Exception:
                    pass
            cls._engine_cache.clear()

    def execute(self, query, params=None):
        if self.engine is None:
            raise Exception("No database connection. Call connect() first.")

        with self.engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            return result.fetchall()

    def close(self):
        try:
            if self.engine:
                self.engine.dispose()
        except Exception as e:
            logger.error("Error closing engine: %s", e)

    def test_connection(self, server, username, password, database):
        try:
            url = self._build_url(server, username, password, database)
            engine = create_engine(url, pool_pre_ping=True)
            with engine.connect() as conn:
                pass
            engine.dispose()
            return True, "Successful connection"
        except Exception as ex:
            return False, f"Connection error: \n{repr(ex)}"

    def list_databases(self, server, username, password) -> tuple[list, str]:
        try:
            url = self._build_url(server, username, password, "master")
            engine = create_engine(url, pool_pre_ping=True)
            with engine.connect() as conn:
                rows = conn.execute(text("SELECT name FROM sys.databases WHERE state = 0 ORDER BY name")).fetchall()
            engine.dispose()
            return ([row[0] for row in rows], "Databases loaded successfully")
        except Exception as ex:
            return ([], f"Connection error: \n{repr(ex)}")
