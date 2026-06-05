import flet as ft

from app.state import AppState
from app.theme import APP_BG
from ui.layout import build_layout


async def main(page: ft.Page):
    state = AppState()
    state.load_fake_records()

    page.title = "Commencement QR Data Utility"
    page.bgcolor = APP_BG
    page.padding = 24
    page.scroll = ft.ScrollMode.AUTO

    page.theme = ft.Theme(
        font_family="Segoe UI",
    )

    build_layout(page, state)


ft.app(target=main)
