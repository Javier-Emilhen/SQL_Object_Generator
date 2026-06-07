import flet as ft
from src.config.config import settings
from src.gui.components.file_explorer import btn_open_file_explorer


def validate_required_field(field: ft.TextField) -> bool:
    if not (field.value or "").strip():
        field.error_text = "This field is required."
        field.update()
        return False
    field.error_text = None
    field.update()
    return True


def handle_generation_result(
    page: ft.Page,
    success: bool,
    message: str,
    scripts: str | None,
    use_clipboard: bool,
    path: str,
    loading_alert,
    msg_alert,
):
    if not success:
        content = ft.Text(message)
    elif use_clipboard:
        page.set_clipboard(scripts)
        content = ft.Text(message)
    else:
        settings().set_download_path(path)
        content = btn_open_file_explorer(message, path)

    loading_alert.hide()
    msg_alert.show(content)
