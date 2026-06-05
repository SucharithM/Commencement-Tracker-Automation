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
        self.total_pages = 0
        self.current_page = 0
        self.is_processing = "False"

    def add_records(self, record):
        self.records.append(record)

    def delete_records(self, index):
        if 0 <= index < len(self.records):
            self.records.pop(index)

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

    def load_fake_records(self):
        self.records = [
            StudentRecord(
                source_file="Batch1.pdf",
                page_number="1",
                student_id="0222",
                first_name="John",
                last_name="Doe",
                status=RecordStatus.SUCCESS,
            ),
            StudentRecord(
                source_file="Batch2.pdf",
                page_number="3",
                student_id="08852",
                first_name="Jane",
                last_name="Doe",
                status=RecordStatus.WARNING,
            ),
            StudentRecord(
                source_file="Batch3.pdf",
                page_number="2",
                student_id="055662",
                first_name="Bill",
                last_name="Doe",
                status=RecordStatus.ERROR,
            ),
        ]
