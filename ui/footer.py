import flet as ft

from app.theme import PRIMARY, TEXT_MUTED, WHITE


def build_footer(state) -> ft.Control:
    summary = (
        f"Total Rows: {state.total_count()} | "
        f"Ready: {state.success_count()} | "
        f"Errors: {state.error_count()}"
    )

    return ft.Container(
        padding=ft.Padding.only(top=4),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    summary,
                    size=13,
                    color=TEXT_MUTED,
                    weight=ft.FontWeight.W_500,
                ),
                ft.ElevatedButton(
                    content="Export to Excel",  # type: ignore
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda e: None,
                    style=ft.ButtonStyle(
                        bgcolor=PRIMARY,
                        color=WHITE,
                        padding=ft.Padding.symmetric(
                            horizontal=22,
                            vertical=14,
                        ),
                        shape=ft.RoundedRectangleBorder(radius=14),
                    ),
                ),
            ],
        ),
    )
