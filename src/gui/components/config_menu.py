import flet as ft
import json
from pathlib import Path
from src.config.config import settings
from src.sql.connection import sql_class

_settings = settings()
CONFIG_PATH = _settings.ensure_config_available()

def load_data():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
         
def save_data(data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def show_config_alert(page: ft.Page, on_close=None):

    db_config = _settings.get_db_config() or {}
    
    # Inputs
    text_server = ft.TextField(label="Server", value=db_config.get("server", ""), on_change=lambda e: reload_databases())
    text_user = ft.TextField(label="Username", value=db_config.get("username", ""), on_change=lambda e: reload_databases())
    txt_password = ft.TextField(label="Password", value=db_config.get("password", ""), password=True, can_reveal_password=True, on_change=lambda e: reload_databases())

    _saved_db = db_config.get("database") or None
    dd_db = ft.Dropdown(
        label="Database",
        # value=_saved_db,
        options=[ft.DropdownOption(_saved_db)] if _saved_db else [],
        expand=True,
        editable=True
    )

    inputs = [text_server, text_user, txt_password]

    # Validation messages
    message_text = ft.Text(
        selectable=True,
        value="",
        overflow= ft.TextOverflow.VISIBLE,
        no_wrap=True
    )

    message_container = ft.ResponsiveRow(
        controls=[ft.Column(
            [message_text],
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
            )
        ],
        visible=False
    )

        # --- Helper functions
    def validate_fields():
        valid = True
        for field in inputs:
            if not (field.value or "").strip():
                field.error_text = "This field is required"
                valid = False
            else:
                field.error_text = None
            field.update()
        if dd_db.value == " ":
            dd_db.error_text = "This field is required"
            dd_db.update()
            valid = False
        elif dd_db.error_text:
            dd_db.error_text = None
            dd_db.update()
        return valid

    def disable_controls(disabled: bool):
        for field in inputs:
            field.disabled = disabled
            field.update()

        if(disabled):
            message_container.visible = True
            message_text.value = "Loading..." if disabled else ""
            message_text.color = ft.Colors.WHITE
            message_text.update()
    
    # def on_change_validate(e):
    #     if(not e.data or e.data == ""):
    #         e.control.error_text = "This field is required"
    #     else:
    #         e.control.error_text = None
    #     e.control.update()
    
    _empty_option = ft.DropdownOption(key="", text=" ")

    def reload_databases(preselect=None):
        dd_db.options = [_empty_option]
        dd_db.value = " "
        dd_db.update()
        if not all([text_server.value.strip(), text_user.value.strip(), txt_password.value.strip()]):
            return
        db = sql_class()
        databases, error_msg = db.list_databases(
            server=text_server.value,
            username=text_user.value,
            password=txt_password.value,
        )
        if not databases:
            message_text.value = error_msg
            message_text.color = ft.Colors.RED
            message_container.visible = True
            message_container.update()
            message_text.update()
            return
        message_container.visible = False
        message_container.update()
        dd_db.options = [ft.DropdownOption(d) for d in databases]
        dd_db.value = preselect if preselect and preselect in databases else " "
        dd_db.update()

    def test_connection():
        
        #Validate Controls
        if not validate_fields():
            return False

        #Test connection
        db = sql_class()
        result, message = db.test_connection(
            server= text_server.value,
            username= text_user.value,
            password=txt_password.value,
            database=dd_db.value
        )
        
        message_text.value = message
        message_container.visible = True
        message_text.color = ft.Colors.GREEN if result else ft.Colors.RED
        
        message_container.update()
        message_text.update()
        
        return result
    
    def on_click_test(e):
        disable_controls(True)
        test_connection()
        disable_controls(False)
        
    def on_click_save(e):

        disable_controls(True)

        if not test_connection():
            disable_controls(False)
            return

        _settings.save_db_config(
            server=text_server.value,
            username=text_user.value,
            password=txt_password.value,
            database=dd_db.value
        )
        sql_class.invalidate_cache()
        
        if on_close:
            on_close()
            
        dlg.open = False
        page.update()
    
    def on_click_cancel(e):
        dlg.open = False
        page.update()
    
    # Dialog definition
    dlg = ft.AlertDialog(
        modal=True,
        content_padding=20,
        title_padding=ft.padding.all(20),
        title=ft.Text("DB connection", text_align=ft.TextAlign.CENTER),
        content=ft.Column([
            text_server,
            text_user,
            txt_password,
            dd_db,
            message_container
        ], tight=True, spacing=20),
        actions_alignment=ft.MainAxisAlignment.END,
        actions=[
            ft.Row(
                [
                 ft.Container(
                     ft.TextButton("Test connection", on_click=on_click_test)),
                 ft.Container(ft.Row([
                        ft.TextButton("Cancel", on_click=on_click_cancel),
                        ft.ElevatedButton("Save", on_click=on_click_save)]))
                ],
                alignment= ft.MainAxisAlignment.SPACE_BETWEEN, 
            )
        ]
    )
    
    if dlg not in page.overlay: page.overlay.append(dlg)

    dlg.open = True
    page.update()

    reload_databases(preselect=_saved_db)

    # page.open(dlg)