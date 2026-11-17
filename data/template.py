"""Pembuat templat spreadsheet terstandar (.xlsx)."""
from __future__ import annotations

from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from data.transform import COLUMNS


def build_template() -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Data"
    ws.append(COLUMNS)
    for kelas, l, p in (("VII", 60, 62), ("VIII", 58, 60), ("IX", 55, 57)):
        ws.append(["2025/2026", kelas, l, p])

    head_fill = PatternFill("solid", fgColor="1F4E79")
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = head_fill
        cell.alignment = Alignment(horizontal="center")
    for col, w in zip("ABCD", (16, 10, 14, 14)):
        ws.column_dimensions[col].width = w

    info = wb.create_sheet("Petunjuk")
    for line in (
        "Petunjuk pengisian",
        "1. Isi sheet 'Data', satu baris per kombinasi tahun ajaran dan kelas.",
        "2. tahun_ajaran: format 2025/2026 (tahun berurutan).",
        "3. kelas: VII, VIII, atau IX.",
        "4. laki_laki dan perempuan: bilangan bulat >= 0.",
        "5. Hapus baris contoh sebelum mengunggah data Anda.",
    ):
        info.append([line])
    info["A1"].font = Font(bold=True)
    info.column_dimensions["A"].width = 70

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
