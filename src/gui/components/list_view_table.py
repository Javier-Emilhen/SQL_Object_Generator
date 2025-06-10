import flet as ft
from src.models.sql_objects import sql_objects

def list_view_table(on_select_all = None, on_select_row = None, columns= None):

    _select_all_checkbox = ft.Checkbox(value=False, on_change=on_select_all, width=30)

    _data_checkbox = []
    
    rows = [_select_all_checkbox]
    
    for column in columns:
        titulo = column.get('caption', '') 
        width = column.get('width', None) 
        expand = column.get('expand', False) 
        
        rows.append(ft.Text(
            value=titulo, 
            width=width, 
            expand=expand,
            weight="bold", 
            text_align=ft.TextAlign.CENTER
            )
        )
    
    #List View (Table)
    titles_list_view = ft.Container(
        bgcolor=ft.Colors.BLUE_GREY_800,
        border= ft.border.all(2,ft.Colors.BLUE_GREY_800),
        border_radius=10,
        padding=5,
        content=ft.Row(controls=rows)
    )
    
    table_list_view = ft.ListView(
        expand=True,
        spacing=5,
        auto_scroll=False,
    )
    
    
    def load_data(data: list[sql_objects]):
        table_list_view.controls.clear()
        _data_checkbox.clear()
        
        _select_all_checkbox.value = False
        _select_all_checkbox.update()
        
        for obj in data:
                checkbox = ft.Checkbox(
                    value=False,
                    width=30,
                    on_change=lambda e, x=obj: on_select_row(x, e.control.value)
                )

                _data_checkbox.append({"data": obj, "checkbox": checkbox})

                fila = ft.Container(
                    padding=2,
                    border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.BLUE_GREY_800)),
                    content=ft.Row([
                        checkbox,
                        ft.Text(str(obj.ID), width=120, text_align=ft.TextAlign.CENTER, selectable=True),
                        ft.Text(str(obj.Schema), width=150, text_align=ft.TextAlign.CENTER, selectable=True),
                        ft.Text(str(obj.Name), expand=2, text_align=ft.TextAlign.START, selectable=True),
                        ft.Text(str(obj.Object_Key), expand=1, text_align=ft.TextAlign.CENTER, selectable=True),
                        ft.Text(str(obj.Sql_Object), expand=1, text_align=ft.TextAlign.CENTER, selectable=True),
                        ft.Text(str(obj.Modification_Date), expand=1, text_align=ft.TextAlign.CENTER, selectable=True),
                    ])
                )

                table_list_view.controls.append(fila)

        table_list_view.update()

    return titles_list_view, table_list_view, load_data, _select_all_checkbox, _data_checkbox