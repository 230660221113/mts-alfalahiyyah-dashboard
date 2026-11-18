"""Konstanta murni (tanpa dependensi Streamlit)."""
ROLE_OPERATOR = "operator"
ROLE_KEPALA_SEKOLAH = "kepala_sekolah"
# Alias kompatibilitas mundur dengan schema lama ('pimpinan')
ROLE_PIMPINAN = "pimpinan"
KEPALA_ROLES = (ROLE_KEPALA_SEKOLAH, ROLE_PIMPINAN)

KELAS_VALID = ("VII", "VIII", "IX")
MAX_HORIZON = 3      # prediksi 1-3 tahun ajaran
MIN_POINTS = 6       # minimal jumlah tahun ajaran agar prediksi dijalankan


def role_label(role: str) -> str:
    if role == ROLE_OPERATOR:
        return "Operator (Super Admin)"
    if role in KEPALA_ROLES:
        return "Kepala Sekolah"
    return role.replace("_", " ").title()
