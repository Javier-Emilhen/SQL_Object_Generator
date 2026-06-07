import flet as ft

class LoadingAlert:

    def __init__(self, page: ft.Page):
        self.page = page
        self._label = ft.Text("", size=13, color=ft.Colors.WHITE70, text_align=ft.TextAlign.CENTER)
        self.dialog = ft.AlertDialog(
            modal=True,
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Loading...", size=20, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                        ft.ProgressRing(color=ft.Colors.WHITE, width=50, height=50),
                        self._label,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    tight=True,
                    spacing=12,
                ),
                alignment=ft.alignment.center,
                padding=20,
                width=320,
            ),
            bgcolor="transparent"
        )

        if self.dialog not in self.page.overlay:
            self.page.overlay.append(self.dialog)

    def show(self):
        self._label.value = ""
        self.dialog.open = True
        self.page.update()

    def hide(self):
        self._label.value = ""
        self.dialog.open = False
        self.page.update()

    def update_progress(self, label: str):
        self._label.value = label
        self.page.update()
