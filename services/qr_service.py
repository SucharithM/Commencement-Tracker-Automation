import csv
import json
import cv2
from dataclasses import dataclass
from io import StringIO
from urllib.parse import parse_qs

from models.student_details import RecordStatus, StudentRecord

QR_FIELDS = [
    "Name Card ID",
    "Last Name",
    "First Name",
    "College",
    "Session",
]

FIELD_ALIASES = {
    "name card id": "card_id",
    "card id": "card_id",
    "last name": "last_name",
    "lastname": "last_name",
    "first name": "first_name",
    "firstname": "first_name",
    "college": "college",
    "school": "college",
    "session": "session",
}


@dataclass
class QRDecodeResult:
    payload: str = ""
    error_message: str = ""


def decode_qr_payload(image_array) -> QRDecodeResult:
    detector = cv2.QRCodeDetector()
    payloads = _decode_multi(detector, image_array)

    if not payloads:
        payloads = _decode_single(detector, image_array)

    if not payloads:
        grayscale = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        payloads = _decode_single(detector, grayscale)

    if not payloads:
        return QRDecodeResult(error_message="No QR code detected on this page.")

    return QRDecodeResult(payload=payloads[0])


def build_record_from_payload(
    payload: str,
    source_file: str,
    page_number: int,
    source_pdf_path: str = "",
) -> StudentRecord:
    values = _parse_csv_payload(payload)
    record = StudentRecord(
        source_file=source_file,
        page_number=page_number,
        source_pdf_path=source_pdf_path,
        card_id=values.get("card_id", ""),
        last_name=values.get("last_name", ""),
        first_name=values.get("first_name", ""),
        college=values.get("college", ""),
        session=values.get("session", ""),
    )
    record.validate()
    return record


def build_error_record(
    source_file: str,
    page_number: int,
    error_message: str,
    source_pdf_path: str = "",
) -> StudentRecord:
    return StudentRecord(
        source_file=source_file,
        page_number=page_number,
        source_pdf_path=source_pdf_path,
        status=RecordStatus.ERROR,
        error_message=error_message,
        scan_failed=True,
        scan_error_message=error_message,
    )


def _decode_multi(detector, image_array) -> list[str]:
    try:
        success, decoded_info, _points, _straight_qrcode = (
            detector.detectAndDecodeMulti(image_array)
        )
        print(f"This is the decoded info -> {decoded_info}")
    except Exception:
        return []

    if not success:
        return []

    return [
        each_payload.strip()
        for each_payload in decoded_info
        if each_payload and each_payload.strip()
    ]


def _decode_single(detector, image_array) -> list[str]:
    try:
        payload, _points, _straight_qrcode = detector.detectAndDecode(image_array)
    except Exception:
        return []

    if not payload or not payload.strip():
        return []
    return [payload.strip()]


def _parse_csv_payload(payload: str) -> dict[str, str]:
    clean_payload = payload.strip()
    reader = csv.reader(StringIO(clean_payload), skipinitialspace=True)
    try:
        row = next(reader)
    except StopIteration:
        return {}

    values = [each_value.strip() for each_value in row]
    if len(values) < len(QR_FIELDS):
        return {}

    return {
        "card_id": values[0],
        "last_name": values[1],
        "first_name": values[2],
        "college": values[3],
        "session": values[4],
    }
