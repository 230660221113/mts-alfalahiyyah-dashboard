# Dashboard Kesiswaan MTs Al-Falahiyyah

Aplikasi dashboard Streamlit untuk memantau jumlah peserta didik, melihat proyeksi, mengunggah data kesiswaan, serta mengunduh rekap.

## Menjalankan secara lokal

```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1

pip install -r requirements.txt
streamlit run app.py
```

## Deployment Streamlit Community Cloud

- Repository: repository GitHub project ini.
- Main file path: `app.py`.
- Pastikan `requirements.txt` berada di root repository.
- Jika memakai akun khusus, tambahkan konfigurasi `users` pada Streamlit Secrets. Tanpa konfigurasi tersebut aplikasi menggunakan akun demo yang didefinisikan di `src/auth.py`.

## Struktur utama

- `app.py`: entry point Streamlit.
- `src/app.py`: alur halaman dan komponen aplikasi.
- `src/styles.py`: styling antarmuka.
- `src/data.py`: pemuatan data dan template Excel.
- `src/forecasting.py`: model peramalan.
- `src/visualization.py`: grafik Plotly.
- `src/auth.py`: autentikasi demo / konfigurasi pengguna.
- `src/validation.py`: validasi file Excel.
- `.streamlit/config.toml`: tema Streamlit.

## Catatan data

`src/data.py` saat ini memuat data contoh untuk demonstrasi. Penyimpanan hasil unggahan masih menggunakan session state dan belum dihubungkan ke tabel Supabase. Jangan menganggap angka yang tampil sebagai data resmi sekolah sebelum integrasi sumber data dilakukan.
