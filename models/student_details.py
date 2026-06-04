from dataclasses import dataclass
from enum import Enum


class RecordStatus(Enum):
    SUCCESS = "Success"
    WARNING = "Warning"
    ERROR = "Error"


@dataclass
class StudentRecord:
    source_file: str
    page_number: str
    student_id: str = ""
    first_name: str = ""
    last_name: str = ""
    status: RecordStatus = RecordStatus.ERROR
    error_message: str = ""

    @property
    def source_location(self) -> str:
        return f"{self.source_file} (Page {self.page_number})"

    def validate(self):
        missing_fields = []

        if not self.student_id.strip():
            missing_fields.append("Student ID")

        if not self.first_name.strip():
            missing_fields.append("First Name")

        if not self.last_name.strip():
            missing_fields.append("Last Name")

        if not missing_fields:
            self.status = RecordStatus.SUCCESS
            self.error_message = ""
        else:
            self.status = RecordStatus.WARNING
            self.error_message = "Missing: " + ", ".join(missing_fields)
