"""Pembuat templat spreadsheet terstandar (.xlsx) dengan validasi sel Excel bawaan."""
from __future__ import annotations

from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

from data.transform import COLUMNS


def build_template() -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Data"
    ws.append(COLUMNS)

    contoh_rows = [
        ("2025/2026", "VII", 60, 62),
        ("2025/2026", "VIII", 58, 60),
        ("2025/2026", "IX", 55, 57),
    ]
    for r in contoh_rows:
        ws.append(list(r))

    head_fill = PatternFill("solid", fgColor="0F4C81")
    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1"),
    )

    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF", size=11)
        cell.fill = head_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
    ws.row_dimensions[1].height = 24

    for row in ws.iter_rows(min_row=2, max_row=4, min_col=1, max_col=4):
        for c in row:
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.border = thin_border
            if c.column == 1:
                c.number_format = "@"  # Paksa format Teks agar tidak berubah menjadi tanggal

    # Format teks pada kolom tahun_ajaran & kelas hingga baris 200
    for r_idx in range(2, 201):
        ws.cell(row=r_idx, column=1).number_format = "@"
        ws.cell(row=r_idx, column=2).number_format = "@"
        ws.cell(row=r_idx, column=3).number_format = "0"
        ws.cell(row=r_idx, column=4).number_format = "0"

    # Excel Data Validation untuk kolom kelas (dropdown VII, VIII, IX)
    dv_kelas = DataValidation(type="list", formula1='"VII,VIII,IX"', allow_blank=False)
    dv_kelas.errorTitle = "Kelas Tidak Valid"
    dv_kelas.error = "Pilih salah satu: VII, VIII, atau IX tanpa spasi."
    ws.add_data_validation(dv_kelas)
    dv_kelas.add("B2:B200")

    # Excel Data Validation untuk bilangan bulat >= 0 pada kolom laki_laki dan perempuan
    dv_int = DataValidation(type="whole", operator="greaterThanOrEqual", formula1="0", allow_blank=False)
    dv_int.errorTitle = "Angka Tidak Valid"
    dv_int.error = "Masukkan bilangan bulat >= 0 tanpa spasi, titik, atau koma."
    ws.add_data_validation(dv_int)
    dv_int.add("C2:D200")

    for col, w in zip("ABCD", (18, 12, 15, 15)):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A2"

    info = wb.create_sheet("Petunjuk")
    lines = [
        "PETUNJUK PENGISIAN TEMPLAT DATA KESISWAAN",
        "1. Isi data pada sheet 'Data', satu baris per kombinasi tahun ajaran dan tingkat kelas.",
        "2. Kolom tahun_ajaran: format tepat YYYY/YYYY berurutan (contoh: 2024/2025) TANPA spasi atau tanda baca lain.",
        "3. Kolom kelas: pilih VII, VIII, atau IX TANPA spasi atau titik koma.",
        "4. Kolom laki_laki dan perempuan: bilangan bulat >= 0 (tanpa titik pemisah ribuan, koma, atau spasi).",
        "5. Sistem menolak berkas yang mengandung spasi liar, titik koma (;), koma, atau karakter tersembunyi.",
        "6. Hapus 3 baris contoh bawaan sebelum mengunggah data asli madrasah.",
    ]
    for idx, line in enumerate(lines, start=1):
        info.append([line])
        c = info.cell(row=idx, column=1)
        if idx == 1:
            c.font = Font(bold=True, size=12, color="0F4C81")
        else:
            c.font = Font(size=10)
    info.column_dimensions["A"].width = 95

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
