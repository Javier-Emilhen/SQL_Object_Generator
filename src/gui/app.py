import flet as ft
from src.core.sql_search_engine import sql_search_engine
from src.core.sql_generator import sql_generator
from src.utils.enumerators import object_types
from src.utils.enumerators import table_get_options
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
    page.window.icon = '../assets/favicon.ico'

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
            
        # table_options_dropdown.disabled = not any(
        #     chkbox.value and chkbox.label == object_types.TBL.value
        #     for chkbox in selected_chboxs
        # )
        
        # table_options_dropdown.update()
            
        
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
        
        path_txt_field.error_text =None
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
        
        if path_txt_field.value == "" and not clipboard_switch.value :
           path_txt_field.error_text ="This field is requiered."
           path_txt_field.update()
           return
        else:
            path_txt_field.error_text =None
            path_txt_field.update()
            
        _alert_loading.show()
            
        definition = sql_generator(path_txt_field.value, clipboard_switch.value, table_options_dropdown.value)
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
            _alert_message.show(str(ex))
        finally:
            _alert_loading.hide()
    
    def on_close_config():
        server_txt.value = _settings.get_server_name()
        db_txt.value = _settings.get_db_name()
        server_txt.update()
        db_txt.update()
        db_txt.update()
        
        #Reiniciar controles al cambiar conexion
        generate_button.disabled=True
        table_list_view.controls.clear()
        _select_all_checkbox.value = False
        _data_checkbox.clear()
        totals_txt_field.value= None
        selected_items_txt_field.value=None
        
        totals_txt_field.update()
        selected_items_txt_field.update()
        generate_button.update()
        _select_all_checkbox.update()
        table_list_view.update()
    
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
        hint_text="Example: C:\Downloads",
        # value="C:\\Users\\javierrodriguez\\Downloads\\Test",
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
   
    # records_checkbox = ft.Checkbox(
    #     "Generate table records",
    #     value=True, 
    #     label_position=ft.LabelPosition.LEFT
    # )
    
    table_options_dropdown = ft.Dropdown(
        label= "Table Options",
        options=[ft.DropdownOption(key=option.name, text=option.value) for option in table_get_options],
        value= table_get_options.Schema_Only.name,
        expand=False
    )
        
    object_types_checkboxes = [ft.Checkbox(label=option.value, value=True, on_change=on_change_tipo_checkboxes) for option in object_types]
    
    search_btn = ft.ElevatedButton(
        text = "Search",
        icon = ft.icons.SEARCH_OUTLINED,
        width= 150,
        height= 40,
        on_click=on_click_search
    )

    generate_button = ft.ElevatedButton(
        text = "Generate",
        icon = ft.icons.DOWNLOAD,
        width= 150,
        height= 40,
        disabled=True,
        on_click=on_click_generate
    )
    
    settings_btn = ft.ElevatedButton(
        "Settings", 
        ft.icons.SETTINGS, 
        on_click= lambda e: show_config_alert(page,on_close_config),  
        width= 150,
        height= 40
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
            {"caption": "SQL ID", "width": 120,},
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
                        col={"sm": 10, "md": 4, "xl":4},
                    ),
                    
                    ft.Container(
                        content=ft.Row(object_types_checkboxes, alignment=ft.MainAxisAlignment.CENTER),
                        margin=ft.margin.only(top=10),
                        padding=5,
                        # border=ft.border.all(1, ft.colors.RED),
                        col={"sm": 12, "md": 4, "xl": 3},
                    ),
                    ft.Container(
                       content=table_options_dropdown,
                    #    border=ft.border.all(1, ft.colors.RED),
                       expand=True,
                       col={"sm": 4, "md": 5, "xl": 3},
                       ),
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
                        content=ft.Row(
                            [clipboard_switch],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ), 
                        margin= ft.Margin(10,10,0,0),
                        alignment=ft.alignment.top_center,
                        col={"sm": 4, "md": 4, "xl": 2}
                        ),
                   
                    ft.Container(
                        content=path_txt_field, 
                        padding=2,
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