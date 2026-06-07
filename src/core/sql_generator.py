import os
from pathlib import Path
from datetime import datetime
from src.models.sql_objects import sql_objects
from src.utils.enumerators import objects_types
from src.utils.enumerators import table_get_options
from src.sql.connection import sql_class
from src.utils.utils import utils
from src.utils.enumerators import sql_definitions

class sql_generator:

    def __init__(self, download_path, clipboard, table_options):
        self.download_path = download_path
        self.clipboard = clipboard
        self.table_options = table_options
        self.db = sql_class()
        self.db.connect()

    def download(self, list_sql_objects, on_progress=None):
        try:
            if not self.clipboard and not Path(self.download_path).exists():
                raise Exception("The route provided does not exist")

            _sp_definitions = []
            _table_definitions = []
            _function_definitions = []
            _table_records = ""
            scripts = ""

            stored_procedures = [item for item in list_sql_objects if item.Object_Key == objects_types.SP.value]
            tables = [item for item in list_sql_objects if item.Object_Key == objects_types.TBL.value]
            functions = [item for item in list_sql_objects if item.Object_Key == objects_types.FN.value]

            schema_mode = self.table_options in [table_get_options.Schema_Data.name, table_get_options.Schema_Only.name]
            data_mode = self.table_options in [table_get_options.Schema_Data.name, table_get_options.Data_Only.name]

            total = (len(stored_procedures) + len(tables) + len(functions)) * int(schema_mode) \
                  + len(tables) * int(data_mode)
            _done = [0]

            def report(name, kind):
                _done[0] += 1
                if on_progress:
                    on_progress(f"{kind}: {name}  ({_done[0]}/{total})")

            if schema_mode:
                _sp_definitions = self.get_sp_definition(stored_procedures, notify=lambda n: report(n, "SP"))
                _table_definitions = self.get_tbl_definition(tables, notify=lambda n: report(n, "Table"))
                _function_definitions = self.get_fn_definitions(functions, notify=lambda n: report(n, "Function"))
                scripts = self.generate_definitions(_sp_definitions, _function_definitions, _table_definitions)

            if data_mode:
                _table_records = self.get_tbl_records(tables, notify=lambda n: report(n, "Table data"))
                scripts += _table_records

            message = None

            if not self.clipboard:
                base_name = f"Scripts_SQL_{datetime.now().strftime('%d_%m_%Y')}.sql"
                download_path = self.download_path.strip().strip('"')
                filename = utils.get_unique_filepath(download_path, base_name)
                with open(filename, 'w', encoding="utf-8") as file:
                    file.write(scripts)
                message = "File successfully generated"
                return True, message, None
            else:
                message = "Records successfully generated in the clipboard"
                return True, message, scripts

        except Exception as ex:
            return False, f"Error: {ex}", None

    # ── Private helper ────────────────────────────────────────────────────────

    def _get_file_based_definitions(
        self,
        items: list[sql_objects],
        sql_file_enum,
        build_declare,
        go_suffix: str = "\nGO\n",
        notify=None,
        catch_errors: bool = False,
    ) -> list:
        if not items:
            return []

        definitions = []
        items.sort(key=lambda x: x.Name.lower())

        file_path = utils.resource_path(sql_file_enum.value)
        with open(file_path, 'r', encoding='utf-8') as sql_file:
            base_sql = sql_file.read()

        for item in items:
            if notify:
                notify(item.Name)
            query = build_declare(item) + base_sql
            try:
                result = self.db.execute(query)
                script = "".join(row[0] for row in result) + go_suffix
                # script = script.replace("\r", "")
            except Exception as ex:
                if catch_errors:
                    script = f"-- Error generating script:\n-- {ex}\n"
                else:
                    raise
            definitions.append([item.Schema, item.Name, script, item.Sql_Object])

        return definitions

    # ── Public definition methods ─────────────────────────────────────────────

    def get_sp_definition(self, stored_procedures: list[sql_objects], notify=None):

        if len(stored_procedures) == 0:
            return []

        procedures_definition = []
        stored_procedures.sort(key=lambda x: x.Name.lower())

        for sp in stored_procedures:
            if notify: notify(sp.Name)
            result = self.db.execute(f"{sql_definitions.SP_FILE.value} '{sp.Schema}.{sp.Name}'")
            script = ""
            for row in result:
                script += row[0]
            script += "GO\n"
            script = script.replace("\r", "")
            procedures_definition.append([sp.Schema, sp.Name, script, sp.Sql_Object])

        return procedures_definition

    def get_fn_definitions(self, functions: list[sql_objects], notify=None):
        return self._get_file_based_definitions(
            functions,
            sql_definitions.FUNCTIONS_FILE,
            lambda func: f"DECLARE @ID_Function INTEGER = {func.ID} ",
            notify=notify,
        )

    def get_tbl_definition(self, tables: list[sql_objects], notify=None):
        return self._get_file_based_definitions(
            tables,
            sql_definitions.TABLES_FILE,
            lambda tbl: f"DECLARE @ID_Table INTEGER = {tbl.ID} ",
            notify=notify,
            catch_errors=True,
        )

    def get_tbl_records(self, tables: list[sql_objects], notify=None):
        table_records = ""
        tables.sort(key=lambda x: x.Name.lower())

        tables_records_path = utils.resource_path(sql_definitions.TABLE_RECORDS.value)
        with open(tables_records_path, 'r', encoding='utf-8') as sql_file:
            records_sql = sql_file.read()

        for tbl in tables:
            if notify: notify(tbl.Name)
            query = f"DECLARE @ID_Table INTEGER = {tbl.ID} " + records_sql
            script = self.db.execute(query)

            tbl_script = f"-- [{tbl.Schema}].[{tbl.Name}]\n"
            if len(script) == 0:
                tbl_script += "-- No records found"
            else:
                for row in script:
                    tbl_script += f"{row[0]}\n"

            table_records += tbl_script + "\n"

        result = f"\n-- TABLE RECORDS:\n"
        result += "-- --------------------------------------------------------------------------- \n"
        result += table_records

        return result

    def generate_definitions(self, _sp_definitions, _function_definitions, _table_definitions):

        database = self.db.database

        sp_count = len(_sp_definitions)
        fn_count = len(_function_definitions)
        tbl_count = len(_table_definitions)
        items_count = sp_count + fn_count + tbl_count
        result = ""

        definitions = _table_definitions + _sp_definitions + _function_definitions
        definitions.sort(key=lambda x: (x[0], x[1]))

        object_sql_list_names = "\n".join(f"-- {sql_type} - {schema}.{name}" for schema, name, _, sql_type in definitions) + "\n"

        result += F"--------------------------------------------------------------------------------------------------------\r"
        result += F"----------------------------------    OPERATION RESULTS   ----------------------------------------------\n"
        result += F"--------------------------------------------------------------------------------------------------------\r"
        result += F"-- Total: {items_count} \r"
        result += F"--   * TABLES: {tbl_count} \r"
        result += F"--   * STORED PROCEDURES: {sp_count} \r"
        result += F"--   * FUNCTIONS: {fn_count} \r"
        result += f"{object_sql_list_names}"
        result += F"--------------------------------------------------------------------------------------------------------\r\n"
        result += f"USE [{database}]\nGO\n"

        for schema, name, script, sql_object_type in definitions:
            result += f"-- /****** Object: {sql_object_type} [{schema}].[{name}] Script Date: {datetime.now()} ******/\n"
            result += "SET ANSI_NULLS ON\nGO\nSET QUOTED_IDENTIFIER ON\nGO\n"
            result += script

        return result
