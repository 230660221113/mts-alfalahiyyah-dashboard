# Dashboard Analitik Kesiswaan (Streamlit)

Visualisasi tren jumlah siswa + prediksi 1–3 tahun ajaran, dengan dua peran:
**operator** (unggah/kelola data) dan **pimpinan** (hanya melihat dashboard & prediksi).

## Struktur
```
app.py                 entry point: login -> navigasi menurut peran
core/                  config, constants, auth (Supabase / demo)
data/                  repository (Supabase & SQLite), validasi, templat, transform
forecasting/           4 model (LR, Holt, ARIMA, RF) + evaluasi MAE/RMSE/MAPE
ui/charts.py           grafik Altair
views/                 login, dashboard, prediksi, unggah, kelola
supabase/schema.sql    tabel + Row Level Security
tests/                 pytest (validasi & forecasting)
```

## Jalankan (mode demo, tanpa Supabase)
```bash
pip install -r requirements.txt
python -m scripts.seed_demo        # data contoh 2018/2019–2025/2026
streamlit run app.py               # login: operator atau pimpinan / demo123
```

## Mode produksi (Supabase)
1. Buat proyek Supabase, jalankan `supabase/schema.sql` di SQL Editor.
2. Buat pengguna di Authentication, lalu set peran operator:
   `update public.profiles set role='operator' where id='<uuid>';`
3. Salin `.streamlit/secrets.toml.example` → `secrets.toml`, isi `SUPABASE_URL` dan `SUPABASE_KEY` (anon key).
4. `streamlit run app.py`. Hak akses ditegakkan di database lewat RLS, bukan hanya di UI.

## Catatan metode
- Target prediksi: total siswa per tahun ajaran; minimal 6 tahun data.
- Evaluasi: backtest expanding-window satu langkah ke depan; model terbaik default = RMSE terkecil.
- Random Forest dilatih pada selisih antar-tahun agar tidak datar di luar rentang data.
