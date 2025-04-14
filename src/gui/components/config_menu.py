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

def show_config_alert(page: ft.Page):
    
    config = load_data()
    db_config = config.get("db_config", {})
    
    text_server = ft.TextField(label="Server", value=db_config["server"])
    text_user = ft.TextField(label="Username", value=db_config["username"])
    txt_password = ft.TextField(label="Password", value=db_config["password"], password=True, can_reveal_password=True)
    txt_db = ft.TextField(label="Database", value= db_config["database"])

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
        page.close(dlg)
        page.update()
    
    def test_connection():
    
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
        
    
    def on_click_test(e):
        result = test_connection()
        
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
                     ft.TextButton("Test connection", on_click=on_click_test)),
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