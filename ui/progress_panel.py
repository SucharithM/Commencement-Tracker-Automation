import flet as ft

from app.theme import (
    BORDER_LIGHT,
    PRIMARY,
    SURFACE,
    TEXT_MUTED,
    TEXT_PRIMARY,
)


def build_progress_panel(state) -> ft.Control:
    has_pages = state.total_pages > 0
    progress_color = PRIMARY if has_pages else TEXT_MUTED
    progress_text = (
        f"{state.processed_pages} / {state.total_pages} pages processed"
        if has_pages
        else "No pages queued"
    )
    percent_text = f"{state.progress_percent}%"

    return ft.Container(
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER_LIGHT),
        border_radius=16,
        padding=18,
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text(
                                    state.progress_message,
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                    color=TEXT_PRIMARY if has_pages else TEXT_MUTED,
                                ),
                                ft.Text(
                                    _build_detail_text(state),
                                    size=12,
                                    color=TEXT_MUTED,
                                ),
                            ],
                        ),
                        ft.Text(
                            percent_text,
                            size=18,
                            weight=ft.FontWeight.W_700,
                            color=progress_color,
                        ),
                    ],
                ),
                ft.ProgressBar(
                    value=state.progress_value,
                    color=progress_color,
                    bgcolor="#E9ECEF",
                    height=7,
                    border_radius=10,
                ),
                ft.Text(
                    progress_text,
                    size=12,
                    color=TEXT_MUTED,
                ),
            ],
        ),
    )


def _build_detail_text(state) -> str:
    if not state.total_pages:
        return "Select one or more PDFs to begin."

    if state.is_processing and state.current_pdf_name:
        return (
            f"{state.current_pdf_name} page {state.current_pdf_page} of "
            f"{state.current_pdf_total_pages} | "
            f"{state.selected_pdf_count} PDFs selected"
        )

    if state.processing_complete:
        return f"{state.selected_pdf_count} PDFs processed."

    return f"{state.selected_pdf_count} PDFs selected."
