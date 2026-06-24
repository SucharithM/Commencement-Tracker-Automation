from configs import constants
from models.student_details import RecordStatus, StudentRecord


class AppState:
    FILTER_ALL = constants.FILTER_ALL
    FILTER_SUCCESS = constants.SUCCESS
    FILTER_ERRORS = constants.ERROR

    def __init__(self):
        self.records = []
        self.active_filter = self.FILTER_ALL
        self.selected_file_name = ""
        self.selected_file_path = ""
        self.total_pages = 0
        self.processed_pages = 0
        self.current_page = 0
        self.current_pdf_name = ""
        self.current_pdf_page = 0
        self.current_pdf_total_pages = 0
        self.selected_pdf_count = 0
        self.is_processing = False
        self.processing_complete = False
        self.progress_message = "Waiting for PDF upload..."
        self.export_path = ""
        self.editing_cell = None
        self.table_page = 0
        self.page_size = 100
        self.processed_pdf_names = set()

    @property
    def progress_value(self):
        if not self.total_pages:
            return 0
        return min(self.processed_pages / self.total_pages, 1)

    @property
    def progress_percent(self):
        return int(self.progress_value * 100)

    def reset_progress(self):
        self.total_pages = 0
        self.processed_pages = 0
        self.current_page = 0
        self.current_pdf_name = ""
        self.current_pdf_page = 0
        self.current_pdf_total_pages = 0
        self.selected_pdf_count = 0
        self.processing_complete = False
        self.progress_message = "Waiting for PDF upload..."

    def add_record(self, record):
        self.records.append(record)
        self.revalidate_records()

    def clear_records(self):
        self.records = []

    def delete_record(self, object_id):
        self.records = [
            each_record
            for each_record in self.records
            if each_record.object_id != object_id
        ]
        self.revalidate_records()
        self.clamp_table_page()

    def update_record_field(self, object_id, field_name, value):
        record = self.get_record(object_id)
        if record is None or not hasattr(record, field_name):
            return
        setattr(record, field_name, value)
        self.revalidate_records()

    def revalidate_records(self):
        for record in self.records:
            record.validate()

        card_id_groups = {}
        for record in self.records:
            normalized_card_id = record.card_id.strip().casefold()
            if not normalized_card_id:
                continue
            card_id_groups.setdefault(normalized_card_id, []).append(record)

        for duplicate_group in card_id_groups.values():
            if len(duplicate_group) < 2:
                continue
            for record in duplicate_group:
                self._append_duplicate_warning(record)

    def _append_duplicate_warning(self, record):
        duplicate_message = "Duplicate Card ID"
        if record.status == RecordStatus.SUCCESS:
            record.status = RecordStatus.WARNING
            record.error_message = duplicate_message
            return

        existing_messages = [
            each_message.strip()
            for each_message in record.error_message.split("|")
            if each_message.strip()
        ]
        if duplicate_message not in existing_messages:
            existing_messages.append(duplicate_message)
        record.error_message = " | ".join(existing_messages)

    def get_record(self, object_id):
        return next(
            (
                each_record
                for each_record in self.records
                if each_record.object_id == object_id
            ),
            None,
        )

    def record_index(self, object_id):
        for index, record in enumerate(self.records):
            if record.object_id == object_id:
                return index
        return -1

    def set_editing_cell(self, object_id, field_name):
        self.editing_cell = (object_id, field_name)

    def clear_editing_cell(self):
        self.editing_cell = None

    def total_count(self):
        return len(self.records)

    def success_count(self):
        return sum(
            each_record.status.value == constants.SUCCESS
            for each_record in self.records
        )

    def error_count(self):
        return sum(
            each_record.status.value == constants.ERROR for each_record in self.records
        )

    def warning_count(self):
        return sum(
            each_record.status.value == constants.WARNING
            for each_record in self.records
        )

    def visible_records(self):
        if self.active_filter == constants.SUCCESS:
            return [
                each_record
                for each_record in self.records
                if each_record.status.value == constants.SUCCESS
            ]
        if self.active_filter == constants.ERROR:
            return [
                each_record
                for each_record in self.records
                if each_record.status.value in [constants.ERROR, constants.WARNING]
            ]
        return self.records

    def paginated_visible_records(self):
        visible_records = self.visible_records()
        start_index = self.table_page * self.page_size
        end_index = start_index + self.page_size
        return visible_records[start_index:end_index]

    def page_count(self):
        visible_count = len(self.visible_records())
        if visible_count == 0:
            return 1
        return ((visible_count - 1) // self.page_size) + 1

    def next_table_page(self):
        if self.table_page < self.page_count() - 1:
            self.table_page += 1

    def previous_table_page(self):
        if self.table_page > 0:
            self.table_page -= 1

    def reset_table_page(self):
        self.table_page = 0

    def clamp_table_page(self):
        self.table_page = min(self.table_page, self.page_count() - 1)

    def load_fake_records(self):
        self.records = [
            StudentRecord(
                source_file="Batch1.pdf",
                page_number=1,
                card_id="NC-0222",
                first_name="John",
                last_name="Doe",
                college="College of Arts and Sciences",
                session="Morning",
                status=RecordStatus.SUCCESS,
            ),
            StudentRecord(
                source_file="Batch2.pdf",
                page_number=3,
                card_id="NC-08852",
                first_name="Jane",
                last_name="Doe",
                college="School of Business",
                session="Afternoon",
                status=RecordStatus.WARNING,
            ),
            StudentRecord(
                source_file="Batch3.pdf",
                page_number=2,
                card_id="NC-055662",
                first_name="Bill",
                last_name="Doe",
                college="",
                session="Evening",
                status=RecordStatus.ERROR,
            ),
        ]
