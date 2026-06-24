import asyncio
from pathlib import Path

import flet as ft

from configs import constants
from ui.upload_zone import build_upload_zone
from ui.filter_tabs import build_filter_tabs
from ui.progress_panel import build_progress_panel
from ui.records_table import EDITABLE_FIELDS, build_records_table
from ui.footer import build_footer
from services.excel_service import export_records_to_excel
from services.pdf_service import get_page_count, render_page_data_url, scan_pdf_page


def build_layout(page: ft.Page, state) -> None:
    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    upload_container = ft.Container()
    filter_container = ft.Container()
    progress_container = ft.Container()
    table_container = ft.Container(expand=True)
    footer_container = ft.Container()

    def populate_dynamic_sections() -> None:
        upload_container.content = build_upload_zone(state, handle_choose_pdf)
        upload_container.visible = not state.is_processing
        progress_container.content = build_progress_panel(state)
        progress_container.visible = state.is_processing

        should_show_records = bool(state.records) and not state.is_processing
        filter_container.visible = should_show_records
        table_container.visible = should_show_records
        footer_container.visible = should_show_records

        if should_show_records:
            filter_container.content = build_filter_tabs(state, refresh_ui)
            table_container.content = build_records_table(
                state,
                refresh_ui,
                move_edit_focus,
                handle_preview_page,
            )
            footer_container.content = build_footer(state, handle_export)
        else:
            filter_container.content = ft.Container()
            table_container.content = ft.Container()
            footer_container.content = ft.Container()

    def refresh_ui() -> None:
        populate_dynamic_sections()
        page.update()

    def set_status(message: str) -> None:
        state.progress_message = message
        refresh_ui()

    async def handle_choose_pdf(e) -> None:
        selected_files = await file_picker.pick_files(
            dialog_title="Choose commencement card PDFs",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["pdf"],
            allow_multiple=True,
        )
        if not selected_files:
            return

        pdf_paths = [
            selected_file.path
            for selected_file in selected_files
            if selected_file.path
        ]
        if not pdf_paths:
            set_status("Could not access the selected PDF paths.")
            return

        duplicate_names = find_duplicate_pdf_names(pdf_paths)
        if duplicate_names:
            show_message_dialog(
                title="Duplicate PDF filename",
                message=(
                    "The selected files include duplicate PDF names: "
                    f"{', '.join(duplicate_names)}. Please rename one file "
                    "and try again."
                ),
            )
            return

        previously_uploaded_names = [
            Path(pdf_path).name
            for pdf_path in pdf_paths
            if Path(pdf_path).name in state.processed_pdf_names
        ]
        if previously_uploaded_names:
            show_message_dialog(
                title="PDF already uploaded",
                message=(
                    "These PDFs were already uploaded: "
                    f"{', '.join(previously_uploaded_names)}. Please choose "
                    "different files or rename the PDFs before uploading again."
                ),
            )
            return

        await process_pdfs(pdf_paths)

    def find_duplicate_pdf_names(pdf_paths: list[str]) -> list[str]:
        seen_names = set()
        duplicate_names = []
        for pdf_path in pdf_paths:
            file_name = Path(pdf_path).name
            if file_name in seen_names and file_name not in duplicate_names:
                duplicate_names.append(file_name)
            seen_names.add(file_name)
        return duplicate_names

    def show_message_dialog(title: str, message: str) -> None:
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton(
                    content="OK",
                    on_click=lambda e: page.pop_dialog(),
                )
            ],
        )
        page.show_dialog(dialog)

    async def process_pdfs(pdf_paths: list[str]) -> None:
        if state.is_processing:
            return

        selected_count = len(pdf_paths)
        state.selected_file_name = (
            Path(pdf_paths[0]).name
            if selected_count == 1
            else f"{selected_count} PDFs selected"
        )
        state.selected_file_path = ""
        state.processed_pages = 0
        state.current_page = 0
        state.current_pdf_name = ""
        state.current_pdf_page = 0
        state.current_pdf_total_pages = 0
        state.selected_pdf_count = selected_count
        state.total_pages = 0
        state.is_processing = True
        state.processing_complete = False
        state.clear_editing_cell()
        set_status("Reading selected PDFs...")

        try:
            page_counts = []
            for pdf_path in pdf_paths:
                page_count = await asyncio.to_thread(get_page_count, pdf_path)
                page_counts.append((pdf_path, page_count))
                state.processed_pdf_names.add(Path(pdf_path).name)

            state.total_pages = sum(page_count for _pdf_path, page_count in page_counts)
            state.progress_message = (
                f"{selected_count} PDFs selected | "
                f"{state.total_pages} total pages"
            )
            refresh_ui()

            for file_index, (pdf_path, page_count) in enumerate(page_counts, start=1):
                source_name = Path(pdf_path).name
                state.selected_file_path = pdf_path
                state.current_pdf_name = source_name
                state.current_pdf_total_pages = page_count

                for page_index in range(page_count):
                    state.current_pdf_page = page_index + 1
                    state.progress_message = (
                        f"Processing {source_name} page {page_index + 1} of "
                        f"{page_count} | {state.processed_pages} of "
                        f"{state.total_pages} pages complete"
                    )
                    refresh_ui()

                    record = await asyncio.to_thread(
                        scan_pdf_page,
                        pdf_path,
                        page_index,
                    )
                    state.add_record(record)
                    state.processed_pages += 1
                    state.current_page = state.processed_pages
                    state.progress_message = (
                        f"Processing {source_name} page {page_index + 1} of "
                        f"{page_count} | {state.processed_pages} of "
                        f"{state.total_pages} pages complete"
                    )
                    refresh_ui()
                    await asyncio.sleep(0)

            state.processing_complete = True
            state.progress_message = (
                f"Processing complete: {state.processed_pages} pages processed."
            )
        except Exception as exc:
            state.progress_message = f"Processing failed: {exc}"
        finally:
            state.is_processing = False
            refresh_ui()

    async def handle_preview_page(record) -> None:
        if not record.source_pdf_path:
            set_status("No source PDF path is available for this row.")
            return

        try:
            image_src = await asyncio.to_thread(
                render_page_data_url,
                record.source_pdf_path,
                record.page_number,
            )
        except Exception as exc:
            set_status(f"Could not preview page: {exc}")
            return

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(record.source_location),
            content=ft.Container(
                width=820,
                height=620,
                bgcolor="#F8F9FA",
                border_radius=12,
                padding=12,
                content=ft.Image(
                    src=image_src,
                    fit=ft.BoxFit.CONTAIN,
                    width=796,
                    height=596,
                ),
            ),
            actions=[
                ft.TextButton(
                    content="Close",
                    on_click=lambda e: page.pop_dialog(),
                )
            ],
        )
        page.show_dialog(dialog)

    async def handle_export(e) -> None:
        if state.warning_count() or state.error_count():
            show_export_options_dialog()
            return

        await export_selected_records(state.records)

    def show_export_options_dialog() -> None:
        async def export_all(e) -> None:
            page.pop_dialog()
            await export_selected_records(state.records)

        async def export_success_only(e) -> None:
            page.pop_dialog()
            success_records = [
                record
                for record in state.records
                if record.status.value == state.FILTER_SUCCESS
            ]
            await export_selected_records(success_records)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Export Records"),
            content=ft.Text(
                "Warnings or errors exist in the table. Include them in the "
                "Excel export? The Notes column will contain the reason for "
                "each warning or error."
            ),
            actions=[
                ft.TextButton(
                    content="Cancel",
                    on_click=lambda e: page.pop_dialog(),
                ),
                ft.TextButton(
                    content="Export Success Only",
                    on_click=export_success_only,
                ),
                ft.TextButton(
                    content="Export All",
                    on_click=export_all,
                ),
            ],
        )
        page.show_dialog(dialog)

    async def export_selected_records(records) -> None:
        if not records:
            set_status("No records are available for the selected export option.")
            return

        export_path = await file_picker.save_file(
            dialog_title="Export verified records",
            file_name="commencement_qr_data.xlsx",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["xlsx"],
        )
        if not export_path:
            return

        if not export_path.lower().endswith(".xlsx"):
            export_path = f"{export_path}.xlsx"

        try:
            await asyncio.to_thread(
                export_records_to_excel,
                records,
                export_path,
            )
            state.export_path = export_path
            success_count = sum(
                record.status.value == constants.SUCCESS
                for record in records
            )
            warning_count = sum(
                record.status.value == constants.WARNING
                for record in records
            )
            error_count = sum(
                record.status.value == constants.ERROR
                for record in records
            )
            set_status(
                f"Exported {len(records)} rows: {success_count} success, "
                f"{warning_count} warnings, {error_count} errors."
            )
            show_message_dialog(
                title="Export complete",
                message=(
                    f"Exported {len(records)} rows to:\n{export_path}"
                ),
            )
        except Exception as exc:
            set_status(f"Export failed: {exc}")

    def move_edit_focus(object_id: str, field_name: str, direction: str) -> None:
        visible_records = state.paginated_visible_records()
        current_row_index = next(
            (
                index
                for index, record in enumerate(visible_records)
                if record.object_id == object_id
            ),
            -1,
        )
        if current_row_index == -1:
            state.clear_editing_cell()
            refresh_ui()
            return

        current_field_index = EDITABLE_FIELDS.index(field_name)
        next_row_index = current_row_index
        next_field_index = current_field_index

        if direction == "right":
            if current_field_index < len(EDITABLE_FIELDS) - 1:
                next_field_index += 1
            elif current_row_index < len(visible_records) - 1:
                next_row_index += 1
                next_field_index = 0
        else:
            if current_row_index < len(visible_records) - 1:
                next_row_index += 1

        next_record = visible_records[next_row_index]
        state.set_editing_cell(
            next_record.object_id,
            EDITABLE_FIELDS[next_field_index],
        )
        refresh_ui()

    def handle_keyboard(e: ft.KeyboardEvent) -> None:
        if not state.editing_cell:
            return

        object_id, field_name = state.editing_cell
        if e.key == "Tab":
            move_edit_focus(object_id, field_name, "right")

    page.on_keyboard_event = handle_keyboard

    populate_dynamic_sections()

    page.add(
        ft.Column(
            expand=True,
            spacing=18,
            controls=[
                upload_container,
                progress_container,
                filter_container,
                table_container,
                footer_container,
            ],
        )
    )
