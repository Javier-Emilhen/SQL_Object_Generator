import os
from datetime import datetime
from src.sql.connection import sql_class
from src.utils.utils import utils
from src.utils.enumerators import sql_definitions


class insert_exporter:

    def __init__(self, schema: str, table_name: str, where_clause: str,
                 download_path: str, clipboard: bool):
        self.schema        = schema.strip() if schema and schema.strip() else "dbo"
        self.table_name    = table_name.strip() if table_name else ""
        self.where_clause  = where_clause.strip() if where_clause and where_clause.strip() else None
        self.download_path = download_path
        self.clipboard     = clipboard
        self.db = sql_class()
        self.db.connect()

    def generate(self) -> tuple[bool, str, str | None]:
        try:
            if not self.clipboard and not os.path.exists(self.download_path.strip().strip('"')):
                raise Exception("The route provided does not exist.")
            if not self.table_name:
                raise Exception("Table name is required.")

            sql_path = utils.resource_path(sql_definitions.TABLE_RECORDS_FILTERED.value)
            with open(sql_path, 'r', encoding='utf-8') as f:
                records_sql = f.read()

            where_val = f"N'{self._escape(self.where_clause)}'" if self.where_clause else "NULL"
            declare_block = (
                f"DECLARE @Schema_Name AS NVARCHAR(128) = N'{self._escape(self.schema)}';\n"
                f"DECLARE @Table_Name  AS NVARCHAR(128) = N'{self._escape(self.table_name)}';\n"
                f"DECLARE @Where_Clause AS NVARCHAR(MAX) = {where_val};\n"
            )
            query = declare_block + records_sql
            result_rows = self.db.execute(query)

            header  = f"-- INSERT Export: [{self.schema}].[{self.table_name}]\n"
            if self.where_clause:
                header += f"-- WHERE: {self.where_clause}\n"
            header += f"-- Generated: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            header += "-- ---------------------------------------------------------------------------\n"

            if not result_rows:
                scripts = header + "-- No records found matching the filter.\n"
            else:
                scripts = header + "".join(f"{row[0]}\n" for row in result_rows)

            if self.clipboard:
                return True, "INSERTs successfully copied to clipboard.", scripts

            base_name = (
                f"Inserts_{self.schema}_{self.table_name}_"
                f"{datetime.now().strftime('%d_%m_%Y')}.sql"
            )
            download_path = self.download_path.strip().strip('"')
            filename = utils.get_unique_filepath(download_path, base_name)

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(scripts)

            return True, "File successfully generated.", None

        except Exception as ex:
            return False, self._clean_error(ex), None

    @staticmethod
    def _clean_error(ex: Exception) -> str:
        msg = str(ex)
        marker = "[SQL Server]"
        idx = msg.find(marker)
        if idx != -1:
            clean = msg[idx + len(marker):].split("\n")[0].strip()
            # Remove trailing SQLAlchemy hint "(Background on this error...)"
            paren = clean.rfind("(Background")
            if paren != -1:
                clean = clean[:paren].strip()
            return clean
        return f"Error: {ex}"

    @staticmethod
    def _escape(value: str) -> str:
        return value.replace("'", "''")
