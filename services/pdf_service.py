from pathlib import Path
from base64 import b64encode
import fitz
import numpy as np

from services.qr_service import (
    build_error_record,
    build_record_from_payload,
    decode_qr_payload,
)


def get_page_count(pdf_path: str) -> int:
    with fitz.open(pdf_path) as document:
        return document.page_count


def scan_pdf_page(pdf_path: str, page_index: int):
    source_file = Path(pdf_path).name
    page_number = page_index + 1

    try:
        image_array = render_page_to_rgb_array(pdf_path, page_index)
    except Exception as exc:
        return build_error_record(
            source_file=source_file,
            page_number=page_number,
            source_pdf_path=pdf_path,
            error_message=f"Could not render page: {exc}",
        )

    decode_result = decode_qr_payload(image_array)
    if decode_result.error_message:
        return build_error_record(
            source_file=source_file,
            page_number=page_number,
            source_pdf_path=pdf_path,
            error_message=decode_result.error_message,
        )

    return build_record_from_payload(
        payload=decode_result.payload,
        source_file=source_file,
        page_number=page_number,
        source_pdf_path=pdf_path,
    )


def render_page_to_rgb_array(pdf_path: str, page_index: int, zoom: float = 2.5):
    with fitz.open(pdf_path) as document:
        page = document.load_page(page_index)
        matrix = fitz.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        image_array = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
            pixmap.height,
            pixmap.width,
            pixmap.n,
        )
        if pixmap.n == 4:
            image_array = image_array[:, :, :3]
        return image_array.copy()


def render_page_data_url(pdf_path: str, page_number: int, zoom: float = 1.8) -> str:
    page_index = page_number - 1
    with fitz.open(pdf_path) as document:
        page = document.load_page(page_index)
        matrix = fitz.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        png_bytes = pixmap.tobytes("png")

    encoded_png = b64encode(png_bytes).decode("ascii")
    return f"data:image/png;base64,{encoded_png}"
