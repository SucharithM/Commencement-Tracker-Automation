import flet as ft

from app.theme import (
    PRIMARY,
    TEXT_MUTED,
    WHITE,
    PILL_BG,
)


def build_filter_tabs(state, refresh_ui) -> ft.Control:
    return ft.Row(
        spacing=10,
        controls=[
            _build_pill(
                label="All",
                count=state.total_count(),
                filter_value=state.FILTER_ALL,
                state=state,
                refresh_ui=refresh_ui,
            ),
            _build_pill(
                label="Success",
                count=state.success_count(),
                filter_value=state.FILTER_SUCCESS,
                state=state,
                refresh_ui=refresh_ui,
            ),
            _build_pill(
                label="Errors",
                count=state.error_count() + state.warning_count(),
                filter_value=state.FILTER_ERRORS,
                state=state,
                refresh_ui=refresh_ui,
            ),
        ],
    )


def _build_pill(
    label: str, count: int, filter_value: str, state, refresh_ui
) -> ft.Control:
    is_active = state.active_filter == filter_value

    def handle_click(e):
        state.active_filter = filter_value
        state.reset_table_page()
        refresh_ui()

    return ft.Container(
        on_click=handle_click,
        bgcolor=PRIMARY if is_active else PILL_BG,
        border_radius=999,
        padding=ft.Padding.symmetric(horizontal=18, vertical=10),
        content=ft.Text(
            f"{label} ({count})",
            size=13,
            weight=ft.FontWeight.W_600,
            color=WHITE if is_active else TEXT_MUTED,
        ),
    )
