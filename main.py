import flet as ft

from app.state import AppState
from app.theme import APP_BG
from ui.layout import build_layout


async def main(page: ft.Page):
    state = AppState()

    page.title = "Commencement Card Automation"
    page.bgcolor = APP_BG
    page.padding = 24
    page.scroll = ft.ScrollMode.AUTO

    page.theme = ft.Theme(
        font_family="Segoe UI",
    )

    build_layout(page, state)


ft.app(target=main)
