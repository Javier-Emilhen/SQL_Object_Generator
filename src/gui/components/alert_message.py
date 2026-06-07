import flet as ft

class alert_message:
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Information"),
            # actions=[ft.TextButton("Ok", on_click=lambda e: page.close(self.dialog))],
            actions=[ft.TextButton("Ok", on_click=lambda e: self.hide())],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        if self.dialog not in self.page.overlay:
            self.page.overlay.append(self.dialog)
        
    def show(self, content):
        
        if isinstance(content, str):
            self.dialog.content = ft.Text(content, text_align= ft.TextAlign.CENTER)
        else:
            self.dialog.content = content
        
        self.dialog.open = True
        self.page.update()
        # self.page.open(self.dialog)
        
    def hide(self):
        self.dialog.open = False
        self.page.update()
        # self.page.close(self.dialog)