import flet as ft


class loading_alert:
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.dialog = ft.AlertDialog(
            modal=True,
            content=ft.Stack(
                [
                    ft.Container(
                        expand=True,
                        # width= page.window.width,
                        # height= page.window.height
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Loading...", size=20, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
                                ft.ProgressRing(color=ft.colors.WHITE, width=50, height=50),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        alignment=ft.alignment.center,
                    )
                ]
            ),
        bgcolor="transparent"
    )

    
    def show(self):
        self.page.open(self.dialog)
        
    def hide(self):
        self.page.close(self.dialog)
    
    
    
