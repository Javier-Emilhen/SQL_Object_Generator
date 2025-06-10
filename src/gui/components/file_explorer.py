import flet as ft
from src.utils.utils import utils
 
def btn_open_file_explorer(message, path):
    row = ft.ResponsiveRow(
        [
            ft.Text(message),
            ft.TextButton(
                "Open Folder",
                style=ft.ButtonStyle(
                    color=ft.Colors.BLUE,
                    overlay_color=ft.Colors.TRANSPARENT,
                    padding=0,
                    shape=ft.RoundedRectangleBorder(radius=0),
                    side=None,
                    ),
                on_click= lambda e: utils.open_path(path)
            )
        ],
        width= 120,
        expand=True,
        spacing=5
    )
    
    return row

def add_path_picker(page: ft.Page, path_text_field: ft.TextField):
    
    def on_result_picker(e: ft.FilePickerResultEvent, path_text_field: ft.TextField):
        if e.path:
            path_text_field.value = e.path
            
        path_text_field.update()
    
    file_picker = ft.FilePicker(on_result=lambda e: on_result_picker(e, path_text_field))
    
    page.overlay.append(file_picker)
    page.update()
    
    path_text_field.suffix_icon = ft.IconButton(
        icon=ft.Icons.FOLDER_OPEN,
        on_click=lambda e: file_picker.get_directory_path()
    )
        
    return file_picker