import flet as ft

from app.theme import (
    PRIMARY,
    SURFACE,
    TEXT_PRIMARY,
    TEXT_MUTED,
    WHITE,
)


def build_upload_zone(state) -> ft.Control:
    selected_file_text = (
        f"{state.selected_file_name} | {state.total_pages} pages"
        if state.selected_file_name
        else "No file selected"
    )

    progress_text = (
        f"Processing page {state.current_page} of {state.total_pages}..."
        if state.is_processing
        else "Waiting for PDF upload..."
    )

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
                                    "Upload PDF Batch",
                                    size=20,
                                    weight=ft.FontWeight.W_700,
                                    color=TEXT_PRIMARY,
                                ),
                                ft.Text(
                                    "Choose a multi-page PDF containing scanned student cards.",
                                    size=13,
                                    color=TEXT_MUTED,
                                ),
                            ],
                        ),
                        ft.ElevatedButton(
                            content="Choose PDF",  # type: ignore
                            icon=ft.Icons.UPLOAD_FILE,
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
                ft.Divider(height=1, color="#E9ECEF"),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            f"Selected file: {selected_file_text}",
                            size=13,
                            color=TEXT_PRIMARY,
                        ),
                        ft.Text(
                            progress_text,
                            size=13,
                            color=TEXT_MUTED,
                        ),
                    ],
                ),
                ft.ProgressBar(
                    value=0,
                    color=PRIMARY,
                    bgcolor="#E9ECEF",
                    height=4,
                    border_radius=10,
                ),
            ],
        ),
    )
