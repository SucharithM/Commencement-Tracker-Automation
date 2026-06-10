import flet as ft

from app.theme import (
    PRIMARY,
    SURFACE,
    TEXT_PRIMARY,
    TEXT_MUTED,
    WHITE,
)


def build_upload_zone(state, on_choose_pdf) -> ft.Control:
    return ft.Container(
        bgcolor=SURFACE,
        border=ft.Border.all(1.5, PRIMARY),
        border_radius=22,
        padding=24,
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=6,
                            controls=[
                                ft.Text(
                                    "Upload PDF Batches",
                                    size=20,
                                    weight=ft.FontWeight.W_700,
                                    color=TEXT_PRIMARY,
                                ),
                                ft.Text(
                                    "Choose one or more PDFs containing scanned student cards.",
                                    size=13,
                                    color=TEXT_MUTED,
                                ),
                            ],
                        ),
                        ft.ElevatedButton(
                            content="Choose PDFs",
                            icon=ft.Icons.UPLOAD_FILE,
                            disabled=state.is_processing,
                            on_click=on_choose_pdf,
                            style=ft.ButtonStyle(
                                bgcolor=PRIMARY,
                                color=WHITE,
                                padding=ft.Padding.symmetric(
                                    horizontal=20,
                                    vertical=14,
                                ),
                                shape=ft.RoundedRectangleBorder(radius=14),
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )
