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
    
    def on_change_validate(e):
        if(not e.data or e.data == ""):
            e.control.error_text = "This field is required"
        else:
            e.control.error_text = None
        e.control.update()
    
    def validate_value(control):
        if(not control.value or control.value == ""):
            control.error_text = "This field is required"
        else:
            control.error_text = None
        control.update()
        
    def on_click_save(e):

        disable_controls(True)

        result = test_connection()
        
        if not result:
            disable_controls(False)
            return
        
        config["db_config"] = {
            "server": text_server.value,
            "username": text_user.value,
            "password": txt_password.value,
            "database": txt_db.value
        }
        
        save_data(config)
        
        if on_close:
            on_close()
            
        page.close(dlg)
        page.update()
    
    def on_click_test(e):
        disable_controls(True)
        test_connection()
        disable_controls(False)
    
    def test_connection():
        
        #Validate Controls
        controls = [text_server,text_user,txt_password,txt_db]
        
        for control in controls:
            validate_value(control)
        
        if(any(c.error_text for c in controls)):
            return False
    
        #Test connection
        db = sql_class()
        result, message = db.test_connection(server= text_server.value, username= text_user.value, password=txt_password.value, database=txt_db.value)
        
        message_text.value = message
        message_container.visible = True
        
        if(not result):
            message_text.color = ft.Colors.RED
        else:
            message_text.color = ft.Colors.GREEN
        
        message_container.update()
        message_text.update()
        
        return result
    
    def disable_controls(disabled: bool):
        text_server.disabled = disabled
        text_user.disabled = disabled
        txt_password.disabled = disabled
        txt_db.disabled = disabled
        
        if(disabled):
            message_text.value = "Loading..."
            message_text.color = ft.Colors.WHITE
        
        text_server.update()
        text_user.update()
        txt_password.update()
        txt_db.update()
        message_text.update()
        
    config = load_data()
    db_config = config.get("db_config", {})
    text_server = ft.TextField(label="Server", value=db_config["server"], on_change=on_change_validate)
    text_user = ft.TextField(label="Username", value=db_config["username"], on_change=on_change_validate)
    txt_password = ft.TextField(label="Password", value=db_config["password"], password=True, can_reveal_password=True, on_change=on_change_validate)
    txt_db = ft.TextField(label="Database", value= db_config["database"], on_change=on_change_validate)

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
        
    dlg = ft.AlertDialog(
        modal=True,
        content_padding=20,
        title_padding=ft.padding.all(20),
        title=ft.Text("DB connection", text_align=ft.TextAlign.CENTER),
        content=ft.Column([
            text_server,
            text_user,
            txt_password,
            txt_db,
            message_container
        ], tight=True, spacing=20),
        actions_alignment=ft.MainAxisAlignment.END,
        actions=[
            ft.Row(
                [
                 ft.Container(
                     ft.TextButton("Test connection", on_click=on_click_test)),
                 ft.Container(ft.Row([
                        ft.TextButton("Cancel", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
                        ft.ElevatedButton("Save", on_click=on_click_save)]))
                ],
                alignment= ft.MainAxisAlignment.SPACE_BETWEEN, 
            )
        ]
    )

    page.open(dlg)
    page.update()