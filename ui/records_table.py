import flet as ft

from app.theme import (
    BORDER_LIGHT,
    ERROR_BG,
    ERROR_TEXT,
    SUCCESS,
    SURFACE,
    TEXT_MUTED,
    TEXT_PRIMARY,
    WARNING,
)
from models.student_details import RecordStatus, StudentRecord


def build_records_table(state, refresh_ui) -> ft.Control:
    visible_records = state.visible_records()

    data_table = ft.DataTable(
        columns=[
            _column("Source Location"),
            _column("Student ID"),
            _column("First Name"),
            _column("Last Name"),
            _column("Status"),
            _column("Actions"),
        ],
        rows=[
            _build_record_row(record, state, refresh_ui) for record in visible_records
        ],
        show_checkbox_column=False,
        heading_row_color="#F8F9FA",
        heading_text_style=ft.TextStyle(
            color=TEXT_MUTED,
            size=12,
            weight=ft.FontWeight.W_700,
        ),
        data_text_style=ft.TextStyle(
            color=TEXT_PRIMARY,
            size=13,
        ),
        column_spacing=28,
        divider_thickness=0.6,
        border=ft.Border.only(
            bottom=ft.BorderSide(0.5, BORDER_LIGHT),
        ),
    )

    table_content: ft.Control

    if visible_records:
        table_content = ft.Row(
            controls=[data_table],
            scroll=ft.ScrollMode.AUTO,
        )
    else:
        table_content = ft.Container(
            alignment=ft.Alignment.CENTER,
            padding=40,
            content=ft.Text(
                "No records available for this filter.",
                size=14,
                color=TEXT_MUTED,
            ),
        )

    return ft.Container(
        bgcolor=SURFACE,
        border_radius=22,
        padding=18,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                table_content,
            ],
        ),
    )


def _column(title: str) -> ft.DataColumn:
    return ft.DataColumn(
        label=ft.Text(
            title,
            color=TEXT_MUTED,
            size=12,
            weight=ft.FontWeight.W_700,
        )
    )


def _build_record_row(record: StudentRecord, state, refresh_ui) -> ft.DataRow:
    is_error = record.status == RecordStatus.ERROR

    text_color = ERROR_TEXT if is_error else TEXT_PRIMARY
    source_color = ERROR_TEXT if is_error else TEXT_MUTED

    def handle_delete(e):
        state.delete_records(record.object_id)
        refresh_ui()

    return ft.DataRow(
        color=ERROR_BG if is_error else None,
        cells=[
            ft.DataCell(
                _cell_text(
                    record.source_location,
                    color=source_color,
                )
            ),
            ft.DataCell(
                _cell_text(
                    record.student_id,
                    color=text_color,
                )
            ),
            ft.DataCell(
                _cell_text(
                    record.first_name,
                    color=text_color,
                )
            ),
            ft.DataCell(
                _cell_text(
                    record.last_name,
                    color=text_color,
                )
            ),
            ft.DataCell(_status_text(record)),
            ft.DataCell(
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=ERROR_TEXT,
                    tooltip="Delete row",
                    on_click=handle_delete,
                )
            ),
        ],
    )


def _cell_text(value: str, color: str) -> ft.Text:
    return ft.Text(
        value if value else "—",
        color=color,
        size=13,
        no_wrap=True,
    )


def _status_text(record: StudentRecord) -> ft.Text:
    if record.status == RecordStatus.SUCCESS:
        return ft.Text(
            record.status.value,
            color=SUCCESS,
            size=13,
            weight=ft.FontWeight.W_700,
        )

    if record.status == RecordStatus.WARNING:
        return ft.Text(
            record.status.value,
            color=WARNING,
            size=13,
            weight=ft.FontWeight.W_700,
            tooltip=record.error_message,
        )

    return ft.Text(
        record.status.value,
        color=ERROR_TEXT,
        size=13,
        weight=ft.FontWeight.W_700,
        tooltip=record.error_message,
    )
