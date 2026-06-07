import flet as ft
from src.core.insert_exporter import insert_exporter
from src.config.config import settings
from src.gui.components.alert_loading import LoadingAlert
from src.gui.components.alert_message import alert_message
from src.gui.components.file_explorer import add_path_picker
from src.gui.helpers import handle_generation_result, validate_required_field


def show_insert_exporter(page: ft.Page, on_close=None):

    _settings = settings()
    _loading  = LoadingAlert(page)
    _msg      = alert_message(page)

    schema_field = ft.TextField(
        label="Schema",
        value="dbo",
        border=ft.border.all(1, ft.Colors.GREY),
    )
    table_field = ft.TextField(
        label="Table Name",
        hint_text="Example: Users",
        border=ft.border.all(1, ft.Colors.GREY),
    )
    where_field = ft.TextField(
        label="WHERE clause (optional)",
        hint_text="Example: ID BETWEEN 3 AND 5",
        multiline=True,
        min_lines=2,
        max_lines=4,
        border=ft.border.all(1, ft.Colors.GREY),
    )
    path_field = ft.TextField(
        label="Download Path",
        hint_text="Example: C:\\Downloads",
        value=_settings.get_download_path(),
        border=ft.border.all(1, ft.Colors.GREY),
        disabled=True,
    )
    add_path_picker(page, path_field)

    clipboard_check = ft.Checkbox(
        "Save to clipboard",
        value=True,
        label_position=ft.LabelPosition.LEFT,
        on_change=lambda e: _toggle_path(e),
    )

    def _toggle_path(e):
        path_field.disabled = e.control.value
        path_field.error_text = None
        path_field.update()

    def _on_click_generate(e):
        if not validate_required_field(table_field):
            return
        if not clipboard_check.value and not validate_required_field(path_field):
            return

        _loading.show()

        exporter = insert_exporter(
            schema=schema_field.value,
            table_name=table_field.value,
            where_clause=where_field.value,
            download_path=path_field.value,
            clipboard=clipboard_check.value,
        )
        success, message, scripts = exporter.generate()

        handle_generation_result(
            page, success, message, scripts,
            use_clipboard=clipboard_check.value,
            path=path_field.value,
            loading_alert=_loading,
            msg_alert=_msg,
        )

    def _close():
        dlg.open = False
        page.update()
        if on_close:
            on_close()

    dlg = ft.AlertDialog(
        modal=True,
        content_padding=20,
        title_padding=ft.padding.all(20),
        title=ft.Text("Export INSERTs", text_align=ft.TextAlign.CENTER),
        content=ft.Column(
            [
                schema_field,
                table_field,
                where_field,
                ft.Row([clipboard_check], alignment=ft.MainAxisAlignment.START),
                path_field,
            ],
            tight=True,
            spacing=15,
            width=480,
        ),
        actions_alignment=ft.MainAxisAlignment.END,
        actions=[
            ft.Row(
                [
                    ft.TextButton("Close", on_click=lambda e: _close()),
                    ft.ElevatedButton(
                        "Generate INSERTs",
                        icon=ft.Icons.DOWNLOAD,
                        on_click=_on_click_generate,
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
            )
        ],
    )

    if dlg not in page.overlay:
        page.overlay.append(dlg)
    dlg.open = True
    page.update()
