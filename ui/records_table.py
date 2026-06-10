import flet as ft

from app.theme import (
    BORDER_LIGHT,
    ERROR_BG,
    ERROR_TEXT,
    PRIMARY,
    SUCCESS,
    SURFACE,
    TEXT_MUTED,
    TEXT_PRIMARY,
    WARNING,
)
from models.student_details import RecordStatus, StudentRecord


EDITABLE_FIELDS = [
    "card_id",
    "first_name",
    "last_name",
    "college",
    "session",
]


def build_records_table(
    state,
    refresh_ui,
    move_edit_focus,
    preview_page,
) -> ft.Control:
    state.clamp_table_page()
    visible_records = state.visible_records()
    page_records = state.paginated_visible_records()

    data_table = ft.DataTable(
        columns=[
            _column("Source Location"),
            _column("Card ID"),
            _column("First Name"),
            _column("Last Name"),
            _column("College"),
            _column("Session"),
            _column("Status"),
            _column("Actions"),
        ],
        rows=[
            _build_record_row(
                record,
                state,
                refresh_ui,
                move_edit_focus,
                preview_page,
            )
            for record in page_records
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
            spacing=12,
            controls=[
                table_content,
                _build_pagination_controls(state, refresh_ui, len(visible_records)),
            ],
        ),
        opacity=0.55 if state.is_processing else 1,
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


def _build_pagination_controls(state, refresh_ui, visible_count: int) -> ft.Control:
    if visible_count == 0:
        return ft.Container()

    start_row = (state.table_page * state.page_size) + 1
    end_row = min(start_row + state.page_size - 1, visible_count)

    def handle_previous(e):
        state.previous_table_page()
        refresh_ui()

    def handle_next(e):
        state.next_table_page()
        refresh_ui()

    return ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text(
                f"Showing {start_row}-{end_row} of {visible_count} rows",
                size=12,
                color=TEXT_MUTED,
            ),
            ft.Row(
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.CHEVRON_LEFT,
                        tooltip="Previous page",
                        disabled=state.table_page == 0,
                        on_click=handle_previous,
                    ),
                    ft.Text(
                        f"Page {state.table_page + 1} of {state.page_count()}",
                        size=12,
                        color=TEXT_MUTED,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CHEVRON_RIGHT,
                        tooltip="Next page",
                        disabled=state.table_page >= state.page_count() - 1,
                        on_click=handle_next,
                    ),
                ],
            ),
        ],
    )


def _build_record_row(
    record: StudentRecord,
    state,
    refresh_ui,
    move_edit_focus,
    preview_page,
) -> ft.DataRow:
    is_error = record.status == RecordStatus.ERROR

    text_color = ERROR_TEXT if is_error else TEXT_PRIMARY
    source_color = ERROR_TEXT if is_error else TEXT_MUTED

    def handle_delete(e):
        state.delete_record(record.object_id)
        refresh_ui()

    async def handle_preview(e):
        await preview_page(record)

    def edit_handler(field_name: str):
        if state.is_processing:
            return None
        return lambda e: _begin_edit(
            state,
            refresh_ui,
            record.object_id,
            field_name,
        )

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
                _editable_cell_content(
                    record,
                    "card_id",
                    state,
                    refresh_ui,
                    move_edit_focus,
                    text_color,
                ),
                show_edit_icon=True,
                on_double_tap=edit_handler("card_id"),
            ),
            ft.DataCell(
                _editable_cell_content(
                    record,
                    "first_name",
                    state,
                    refresh_ui,
                    move_edit_focus,
                    text_color,
                ),
                show_edit_icon=True,
                on_double_tap=edit_handler("first_name"),
            ),
            ft.DataCell(
                _editable_cell_content(
                    record,
                    "last_name",
                    state,
                    refresh_ui,
                    move_edit_focus,
                    text_color,
                ),
                show_edit_icon=True,
                on_double_tap=edit_handler("last_name"),
            ),
            ft.DataCell(
                _editable_cell_content(
                    record,
                    "college",
                    state,
                    refresh_ui,
                    move_edit_focus,
                    text_color,
                ),
                show_edit_icon=True,
                on_double_tap=edit_handler("college"),
            ),
            ft.DataCell(
                _editable_cell_content(
                    record,
                    "session",
                    state,
                    refresh_ui,
                    move_edit_focus,
                    text_color,
                ),
                show_edit_icon=True,
                on_double_tap=edit_handler("session"),
            ),
            ft.DataCell(_status_text(record)),
            ft.DataCell(
                ft.Row(
                    spacing=2,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.VISIBILITY_OUTLINED,
                            icon_color=PRIMARY,
                            tooltip="Preview source page",
                            disabled=state.is_processing,
                            visible=record.status in [
                                RecordStatus.WARNING,
                                RecordStatus.ERROR,
                            ],
                            on_click=handle_preview,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=ERROR_TEXT,
                            tooltip="Delete row",
                            disabled=state.is_processing,
                            on_click=handle_delete,
                        ),
                    ],
                )
            ),
        ],
    )


def _begin_edit(state, refresh_ui, object_id: str, field_name: str) -> None:
    state.set_editing_cell(object_id, field_name)
    refresh_ui()


def _editable_cell_content(
    record: StudentRecord,
    field_name: str,
    state,
    refresh_ui,
    move_edit_focus,
    text_color: str,
) -> ft.Control:
    value = getattr(record, field_name)
    is_editing = state.editing_cell == (record.object_id, field_name)
    is_missing = not value.strip()

    if state.is_processing:
        return ft.Text(
            value if value else "-",
            color=TEXT_MUTED,
            size=13,
            no_wrap=True,
        )

    if is_editing:
        def handle_change(e):
            state.update_record_field(record.object_id, field_name, e.control.value)

        def handle_submit(e):
            state.update_record_field(record.object_id, field_name, e.control.value)
            move_edit_focus(record.object_id, field_name, "down")

        def handle_blur(e):
            state.update_record_field(record.object_id, field_name, e.control.value)

        return ft.TextField(
            value=value,
            autofocus=True,
            dense=True,
            border=ft.InputBorder.UNDERLINE,
            border_color=PRIMARY,
            focused_border_color=PRIMARY,
            color=TEXT_PRIMARY,
            text_size=13,
            content_padding=ft.Padding.symmetric(horizontal=4, vertical=2),
            on_change=handle_change,
            on_submit=handle_submit,
            on_blur=handle_blur,
            width=170,
        )

    display = ft.Text(
        value if value else "-",
        color=ERROR_TEXT if is_missing else text_color,
        size=13,
        no_wrap=True,
    )

    controls = [display]

    if is_missing:
        controls.append(
            ft.Icon(
                icon=ft.Icons.ERROR_OUTLINE,
                color=WARNING,
                size=15,
                tooltip="Missing value",
            )
        )

    controls.append(
        ft.IconButton(
            icon=ft.Icons.EDIT_OUTLINED,
            icon_color=TEXT_MUTED,
            icon_size=16,
            tooltip="Edit value",
            on_click=lambda e: _begin_edit(
                state,
                refresh_ui,
                record.object_id,
                field_name,
            ),
        )
    )

    return ft.Row(
        spacing=6,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=controls,
    )


def _cell_text(value: str, color: str) -> ft.Text:
    return ft.Text(
        value if value else "-",
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
