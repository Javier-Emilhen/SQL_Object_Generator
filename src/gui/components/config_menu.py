import flet as ft
import json
from pathlib import Path
from src.sql.connection import sql_class

CONFIG_PATH = Path("src/config/config.json")

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
        
        result = test_connection()
        
        if not result:
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
            message_text.color = ft.colors.RED
        else:
            message_text.color = ft.colors.GREEN
        
        message_container.update()
        message_text.update()
        
        return result
        
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
        title=ft.Text("Database connection configuration"),
        content=ft.Column([
            text_server,
            text_user,
            txt_password,
            txt_db,
            message_container
        ], tight=True, spacing=20),
        actions=[
            ft.Row(
                [
                 ft.Container(
                     ft.TextButton("Test connection", on_click=lambda e: test_connection())),
                 ft.Container(ft.Row([
                        ft.TextButton("Cancel", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
                        ft.ElevatedButton("Save", on_click=on_click_save)]))
                ],
                alignment= ft.MainAxisAlignment.SPACE_BETWEEN, 
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    page.open(dlg)
    page.update()