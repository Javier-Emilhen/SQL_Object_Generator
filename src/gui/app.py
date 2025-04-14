import flet as ft
from src.core.sql_search_engine import sql_search_engine
from src.core.sql_generator import sql_generator
from src.utils.enumerators import object_types
from src.utils.validators import validators
from src.gui.components.config_menu import show_config_alert
from src.gui.components.list_view_table import list_view_table
from src.gui.components.file_explorer import btn_open_file_explorer
from src.gui.components.file_explorer import add_path_picker
from src.gui.components.alert_loading import loading_alert
from src.gui.components.alert_message import alert_message
from src.config.config import settings

def main(page: ft.Page):
    page.title = "SQL Object Generator"
    page.bgcolor = ft.Colors.BLUE_GREY_900
    page.window.maximized = True

    _selected_rows = set()
    _selected_types = list(object_types)
    _data_checkbox = []
    _settings = settings()
    _alert_loading = loading_alert(page)
    _alert_message = alert_message(page)
        
    #Funciones
    def on_change_tipo_checkboxes(e):
        selected_chboxs = [cb for cb in object_types_checkboxes if cb.value]
        if len(selected_chboxs) == 0 and not e.control.value:
            e.control.value = True 
            e.control.update()
        else:
            _selected_types.clear()
            _selected_types.extend([object_types(cb.label) for cb in object_types_checkboxes if cb.value])
        
    def validate_date(e):
        valid = validators.date_validator(e.data)
        
        if valid == False:
            e.control.error_text = "Invalid formato. Use dd/mm/yyyy"
        elif valid == True:
            e.control.error_text = None  
        elif valid == None:
            e.control.error_text = "Validation error"  
            
        e.control.update()
        
    def on_change_date(e, text_field):
        text_field.value = e.control.value.strftime('%d/%m/%Y')
        text_field.update()
    
    def on_change_clipboard(e):
        path_txt_field.disabled= e.control.value
        path_txt_field.update()
    
    #Funciones del datatable
    def on_select_all(e):
        all_selected = _select_all_checkbox.value
    
        for item in _data_checkbox:
            data = item["data"]
            checkbox = item["checkbox"]
            checkbox.value = all_selected
            checkbox.update() 
        
            if all_selected:
                _selected_rows.add(data)
            else:
                _selected_rows.discard(data)
                
        count_selected =  len(_selected_rows)
        selected_items_txt_field.value = count_selected
        generate_button.disabled = not count_selected > 0

        selected_items_txt_field.update()
        generate_button.update()
        
    def on_select_row(data, checked):
        if checked:
            _selected_rows.add(data)
        else:
            _selected_rows.discard(data)
            
        count_selected =  len(_selected_rows)
        selected_items_txt_field.value = count_selected

        generate_button.disabled = not count_selected > 0
        
        selected_items_txt_field.update()
        generate_button.update()

    def on_click_generate(e):   
        
        _alert_loading.show()
        
        if path_txt_field.value == "" and not clipboard_switch.value :
           path_txt_field.error_text ="This field is requiered."
           path_txt_field.update()
           return
        else:
            path_txt_field.error_text =None
            path_txt_field.update()
            
        definition = sql_generator(path_txt_field.value, clipboard_switch.value)
        result, message, scripts = definition.download(list_sql_objects=_selected_rows)
        
        if(not result):
            content = ft.Text(message)
        else:
            
            if(clipboard_switch.value):
                page.set_clipboard(scripts)
                content = ft.Text(message)
            else:
                content = btn_open_file_explorer(message, path_txt_field.value)
            
        _alert_message.show(content)
        
        _alert_loading.hide()
        
    def on_click_search(e):
        try:
            
            _alert_loading.show()

            object_type = ";".join([tipo.name for tipo in _selected_types])

            search_engine = sql_search_engine(
                filter_txt_field.value,
                init_date_txt_field.value, 
                end_date_txt_field.value,
                object_type, 
                schema_txt_field.value)
            
            sql_data = search_engine.find_sql_objects()

            # Load data in the list view
            load_data(sql_data)
            
            totals_txt_field.value= len(sql_data)
            selected_items_txt_field.value = None

            _selected_rows.clear()
            
            totals_txt_field.update()
            selected_items_txt_field.update()

        except Exception as ex:
            _alert_message.show(ex)
        finally:
            _alert_loading.hide()
    
    def on_close_config():
        server_txt.value = _settings.get_server_name()
        db_txt.value = _settings.get_db_name()
        server_txt.update()
        db_txt.update()
    
    #Controls
    #----------------------------------------------------------------------------------------
    container_title = ft.Container(
        margin= ft.margin.only(bottom=5, top=5),
        content= ft.ResponsiveRow(        
            controls=[
                ft.Text(
                    value="SQL Object Generator",
                    size= 25,
                    color= ft.Colors.WHITE,
                    weight= ft.FontWeight.BOLD,
                    text_align= "CENTER"
                )
            ]
        )
    )
    
    schema_txt_field = ft.TextField( 
        label="Schema",
        value="",
        border=ft.border.all(1, ft.colors.GREY)
    )
    
    filter_txt_field = ft.TextField(
        label="Filtro de nombre",
        value="",
        border=ft.border.all(1, ft.colors.GREY)
    )

    path_txt_field = ft.TextField(
        label="Download Path",
        hint_text="Example: C:/Downloads",
        value="C:\\Users\\javierrodriguez\\Downloads\\Test",
        border=ft.border.all(1, ft.colors.GREY),
        disabled=True
    )
    add_path_picker(page, path_txt_field)
    
    init_date_txt_field = ft.TextField(
        label="Modification init date",
        # value='08/04/2025',
        border=ft.border.all(1, ft.colors.GREY),
        max_length=10,
        on_change= validate_date,
        suffix_icon=ft.IconButton(
            icon=ft.icons.CALENDAR_MONTH, 
            on_click=lambda e:page.open(ft.DatePicker(
                on_change= lambda e: on_change_date(e,init_date_txt_field)
                )))
    )
    
    end_date_txt_field = ft.TextField(
        label="Modification end date",
        border=ft.border.all(1, ft.colors.GREY),
        max_length=10,
        on_change= validate_date,
        suffix_icon= ft.IconButton(
            icon=ft.icons.CALENDAR_MONTH, 
            on_click=lambda e:page.open(ft.DatePicker(
                on_change= lambda e: on_change_date(e,end_date_txt_field)
                )))
    )
    
    clipboard_switch = ft.Checkbox(
        "Save to clipboard",
        value=True, 
        on_change=on_change_clipboard, 
        label_position=ft.LabelPosition.LEFT
    )
        
    object_types_checkboxes = [ft.Checkbox(label=option.value, value=True, on_change=on_change_tipo_checkboxes) for option in object_types]
    
    search_btn = ft.ElevatedButton(
        text = "Search",
        icon = ft.icons.SEARCH_OUTLINED,
        width= 150,
        height= 30,
        on_click=on_click_search
    )

    generate_button = ft.ElevatedButton(
        text = "Generate",
        icon = ft.icons.DOWNLOAD,
        width= 150,
        height= 30,
        disabled=True,
        on_click=on_click_generate
    )
    
    settings_btn = ft.ElevatedButton(
        "Settings", 
        ft.icons.SETTINGS, 
        on_click= lambda e: show_config_alert(page,on_close_config),  
        width= 150,
        height= 50
    )
    
    #Total de elementos
    totals_txt_field =  ft.Text()
    selected_items_txt_field =  ft.Text()
    server_txt = ft.Text(_settings.get_server_name() )
    db_txt = ft.Text(_settings.get_db_name() )
    
    info_container = ft.Container(
            content= ft.Row(
                [
                 ft.Container(ft.Row([
                    ft.Row([ft.Text("Server: ",weight=ft.FontWeight.BOLD),server_txt]),
                    ft.Row([ft.Text("Database: ",weight=ft.FontWeight.BOLD),db_txt]),
                    ft.Row([ft.Text("Items: ",weight=ft.FontWeight.BOLD), totals_txt_field]), 
                    ft.Row([ft.Text("Selected: ",weight=ft.FontWeight.BOLD),selected_items_txt_field])
                    ], 
                        spacing=100),
                    ),
                 ft.Container(ft.Row([search_btn, generate_button]))
                 ],
                alignment= ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.all(10)
        )
    
    titles_list_view,table_list_view, load_data,_select_all_checkbox, _data_checkbox = list_view_table(
        on_select_all= on_select_all,
        on_select_row= on_select_row,
        columns=[
            {"caption": "ID", "width": 120,},
            {"caption": "Schema", "width": 150},
            {"caption": "Name", 'expand': 2},
            {"caption": "Object Key", 'expand': 1},
            {"caption": "SQL Object Type", 'expand': 1},
            {"caption": "Modification date", 'expand': 1}
        ]
    )
    
    # Layout
    controls_container = ft.ResponsiveRow(
        controls=[
            ft.ResponsiveRow(
                col=12,
                controls=[
                    ft.Container(
                        content=schema_txt_field,
                        padding=5,
                        col={"sm": 2, "md": 4, "xl": 2},
                    ),
                    ft.Container(
                        content=filter_txt_field,
                        padding=5,
                        col={"sm": 10, "md": 4, "xl":6},
                    ),
                    
                    ft.Container(
                        content=ft.Row(object_types_checkboxes),
                        padding=5,
                        col={"sm": 12, "md": 4, "xl": 4},
                    )      
                ],
                spacing= 15
            ),
            
            ft.ResponsiveRow(
                expand=True,
                controls = [
                    ft.Container(
                        content=init_date_txt_field, 
                        padding=5,
                        col={"sm": 4, "md": 4, "xl": 2},
                        ),
                    ft.Container(
                        content=end_date_txt_field, 
                        padding=5,
                        col={"sm": 4, "md": 4, "xl": 2},
                        ),
                    ft.Container(
                        content=clipboard_switch, 
                        padding=5,
                        col={"sm": 4, "md": 4, "xl": 2},
                        ),
                    ft.Container(
                        content=path_txt_field, 
                        padding=5,
                        col={"sm": 12, "md": 4, "xl": 6},
                        )
                ]
            ),
        ]
    )
    
    page.floating_action_button = settings_btn
    
    page.add(
        container_title,
        controls_container,
        info_container,
        titles_list_view,
        table_list_view
    )