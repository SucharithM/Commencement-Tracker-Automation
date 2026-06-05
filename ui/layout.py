import flet as ft

from ui.upload_zone import build_upload_zone
from ui.filter_tabs import build_filter_tabs
from ui.records_table import build_records_table
from ui.footer import build_footer


def build_layout(page: ft.Page, state) -> None:
    filter_container = ft.Container()
    table_container = ft.Container(expand=True)
    footer_container = ft.Container()

    def populate_dynamic_sections() -> None:
        filter_container.content = build_filter_tabs(state, refresh_ui)
        table_container.content = build_records_table(state, refresh_ui)
        footer_container.content = build_footer(state)

    def refresh_ui() -> None:
        populate_dynamic_sections()
        page.update()

    populate_dynamic_sections()

    page.add(
        ft.Column(
            expand=True,
            spacing=18,
            controls=[
                build_upload_zone(state),
                filter_container,
                table_container,
                footer_container,
            ],
        )
    )
