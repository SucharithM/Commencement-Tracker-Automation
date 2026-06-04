from app.state import AppState
from app.theme import APP_BG
import flet as ft


async def main(page: ft.Page):
    state = AppState()
    page.title = "Commencement Tracker"
    page.bgcolor = APP_BG
    page.padding = 24
    # build_layout(page, state)


ft.run(main)
