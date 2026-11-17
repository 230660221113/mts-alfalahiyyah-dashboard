from datetime import datetime, timedelta, timezone
from io import BytesIO

import numpy as np
import pandas as pd
import streamlit as st

from src import auth, data, forecasting as fc, styles, validation
from src import visualization as viz


def main():

    st.set_page_config(page_title="Dashboard MTs Al-Falahiyyah", page_icon="🎓", layout="wide")
    st.markdown(styles.CSS, unsafe_allow_html=True)
    role = auth.require_login()
    df = data.load()

    BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    NOW = datetime.now(timezone(timedelta(hours=7)))  # WIB
    TODAY = f"{NOW.day} {BULAN[NOW.month - 1]} {NOW.year}"
    STAMP = f"{NOW.day} {BULAN[NOW.month - 1][:3]} {NOW.year}, {NOW:%H.%M}"
    SAPA = "pagi" if NOW.hour < 11 else "siang" if NOW.hour < 15 else "sore" if NOW.hour < 18 else "malam"

    I_TREND = "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M3 17l6-6 4 4 8-8M15 7h6v6'/></svg>"
    I_SPARK = "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M12 3l2 5.5L19.5 10 14 12l-2 5.5L10 12 4.5 10 10 8.5z'/></svg>"
    I_USERS = "<svg viewBox='0 0 24 24' aria-hidden='true'><circle cx='9' cy='8' r='3.5'/><path d='M2.5 20c.6-3.6 3.2-5.5 6.5-5.5s5.9 1.9 6.5 5.5M16 4.5a3.5 3.5 0 010 7M18 14.8c1.8.7 3 2.3 3.5 5.2'/></svg>"
    I_UP = "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M12 19V5M6 11l6-6 6 6'/></svg>"
    I_DOWN = "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M12 5v14M6 13l6 6 6-6'/></svg>"
    I_FILE = "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M6 3h8l5 5v13H6zM14 3v5h5'/></svg>"

    def fmt(n):
        return f"{int(round(n)):,}".replace(",", ".")

    def table(d, delta=None, best=False):
        head = "".join(f"<th>{c}</th>" for c in d.columns)
        body = ""
        for i, (_, r) in enumerate(d.iterrows()):
            cells = ""
            for c in d.columns:
                v = r[c]
                if c == delta:
                    cells += "<td>–</td>" if pd.isna(v) else f"<td><span class='{'up' if v >= 0 else 'dn'}'>{'▲' if v >= 0 else '▼'} {abs(v):.1f}%</span></td>".replace(".", ",")
                elif isinstance(v, (int, np.integer)):
                    cells += f"<td>{fmt(v)}</td>"
                elif isinstance(v, (float, np.floating)):
                    cells += f"<td>{v:.2f}</td>".replace(".", ",")
                else:
                    cells += f"<td>{v}</td>"
            body += f"<tr class='{'best' if best and i == 0 else ''}'>{cells}</tr>"
        return f"<table class='tbl'><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"

    def header(title):
        demo = "<span class='badge'>Data contoh</span>" if st.session_state.get("is_demo") else ""
        st.markdown(f"<div class='top'><h1>{title}</h1>{demo}</div>", unsafe_allow_html=True)

    def card_head(title, sub=""):
        st.markdown(f"<div class='card-title'>{title}</div><div class='card-sub'>{sub}</div>", unsafe_allow_html=True)

    def seg(name, default=1):
        cur = st.session_state.setdefault(name, default)
        cols = st.columns([1, 1, 1, 3])
        for c, o in zip(cols, [1, 2, 3]):
            if c.button(f"{o} tahun", key=f"seg-{'on' if cur == o else 'off'}-{name}-{o}", use_container_width=True):
                st.session_state[name] = o
                st.rerun()
        return st.session_state[name]

    @st.cache_data
    def run_forecast(values: tuple, h: int):
        return fc.forecast(list(values), h)

    def uploads():
        if "uploads" not in st.session_state:  # contoh awal; nanti dari tabel Supabase
            st.session_state["uploads"] = [
                ("Data_Kesiswaan_2025-2026.xlsx", "Operator", "2025/2026", "ok", "Berhasil", "12 Okt 2026, 09.14"),
                ("Data_Kesiswaan_2025-2026_v1.xlsx", "Operator", "2025/2026", "rj", "Ditolak", "12 Okt 2026, 09.02"),
                ("Data_Kesiswaan_2024-2025.xlsx", "Operator", "2024/2025", "ok", "Berhasil", "3 Agu 2026, 14.40"),
                ("Data_Kesiswaan_2023-2024.xlsx", "Operator", "2023/2024", "wt", "Menunggu validasi", "3 Agu 2026, 14.31")]
        return st.session_state["uploads"]

    # ---------- sidebar ----------
    PAGES = [("Dashboard", "Dashboard", ":material/dashboard:"), ("Peramalan", "Peramalan", ":material/trending_up:")]
    if role == "Operator":
        PAGES.append(("Unggah", "Unggah Data", ":material/upload:"))
    PAGES += [("Kelas", "Rekap Kelas", ":material/groups:"), ("Laporan", "Laporan", ":material/description:")]
    page = st.session_state.setdefault("page", "Dashboard")
    if page not in [p[0] for p in PAGES]:
        page = "Dashboard"

    aktif = df[df["status"] == "Aktif"]
    tot = aktif.groupby("tahun_ajaran")["jumlah"].sum().sort_index()
    years, vals = list(tot.index), [int(v) for v in tot.values]

    with st.sidebar:
        st.markdown("<div class='logo'><i>🎓</i>MTs Al-Falahiyyah</div>", unsafe_allow_html=True)
        for pid, label, icon in PAGES:
            if st.button(label, icon=icon, key=f"nav-{'on' if page == pid else 'off'}-{pid}", use_container_width=True):
                st.session_state["page"] = pid
                st.rerun()
        st.markdown("<div style='height:max(20px, calc(100vh - 720px))'></div>", unsafe_allow_html=True)
        n = len(years)
        segs = "".join("<i></i>" if k < n else "<i class='o'></i>" for k in range(max(10, n)))
        st.markdown(f"<div class='sbcard'>Data tersimpan<small>{n} tahun ajaran</small><div class='seg' aria-hidden='true'>{segs}</div></div>"
                    f"<div class='me'><span class='av'>{role[0]}</span><div>{role}<small>MTs Al-Falahiyyah</small></div></div>", unsafe_allow_html=True)
        if st.button("Keluar", icon=":material/logout:", key="logout", use_container_width=True):
            auth.logout()

    if len(vals) < 6:
        st.warning("Peramalan membutuhkan minimal 6 tahun ajaran data. Unggah data yang lebih lengkap.")
        st.stop()
    latest, prev = vals[-1], vals[-2]
    pct = (latest - prev) / prev * 100

    # ---------- Dashboard ----------
    if page == "Dashboard":
        header("Dashboard")
        best, pred, _ = run_forecast(tuple(vals), 1)
        nxt = fc.next_years(years[-1], 1)[0]
        gk = aktif[aktif.tahun_ajaran == years[-1]].groupby("jenis_kelamin")["jumlah"].sum()
        L, P = int(gk.get("L", 0)), int(gk.get("P", 0))
        up = pct >= 0
        pct_s = f"{abs(pct):.1f}".replace(".", ",")
        stats = ("<div class='stats'>"
                 f"<div class='sc'><span class='ic' style='background:#E3F5EA;color:#1F7A5C'>{I_TREND}</span><b>{fmt(latest)}</b><span class='l'>Peserta didik {years[-1]}</span>"
                 f"<div class='dl {'up' if up else 'dn'}'>{I_UP if up else I_DOWN}{pct_s}% <span>dari tahun lalu</span></div></div>"
                 + f"<div class='sc'><span class='ic' style='background:#EAF6D9;color:#4E8A1F'>{I_SPARK}</span><b>{fmt(pred[0])}</b><span class='l'>Prediksi {nxt}</span><div class='dl'><span>Model terbaik: {best}</span></div></div>"
                 + f"<div class='sc'><span class='ic' style='background:#E1EFF5;color:#25708F'>{I_USERS}</span><b>{L} : {P}</b><span class='l'>Laki-laki : Perempuan</span><div class='dl'><span>{L / (L + P) * 100:.0f}% laki-laki</span></div></div></div>")
        with st.container(key="hero"):
            left, right = st.columns([1.55, 1], gap="medium")
            with left:
                st.markdown(f"<div class='hl'><h2>Selamat {SAPA}, {role}!</h2><p>Pantau perkembangan peserta didik dan rencanakan kelas untuk tahun ajaran berikutnya.</p></div>{stats}", unsafe_allow_html=True)
            with right:
                with st.container(key="card-chart"):
                    card_head("Perkembangan Siswa", f"{len(years)} tahun ajaran dan proyeksi")
                    h = seg("hz")
                    _, p, _ = run_forecast(tuple(vals), h)
                    st.markdown("<div class='lg'><span><i></i>Aktual</span><span><i class='f'></i>Prediksi</span></div>", unsafe_allow_html=True)
                    st.plotly_chart(viz.bar_chart(years, vals, fc.next_years(years[-1], h), list(p)), use_container_width=True, theme=None)
        st.markdown(f"<div class='th'><h3>Riwayat Unggah Data</h3><span class='pillb'>{TODAY}</span></div>", unsafe_allow_html=True)
        rows = "".join(f"<tr><td><div class='fn'><i>{I_FILE}</i>{f}</div></td><td>{u}</td><td>{t}</td><td><span class='chip {c}'>{s}</span></td><td>{w}</td></tr>" for f, u, t, c, s, w in uploads()[:6])
        with st.container(key="card-hist"):
            st.markdown(f"<table class='tbl left'><thead><tr><th>Nama berkas</th><th>Diunggah oleh</th><th>Tahun ajaran</th><th>Status</th><th>Waktu</th></tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)

    # ---------- Peramalan ----------
    elif page == "Peramalan":
        header("Peramalan")
        c1, c2 = st.columns([2.2, 1], gap="medium")
        with c1:
            with st.container(key="card-fc"):
                card_head("Proyeksi jumlah peserta didik", "Memakai model dengan galat terendah")
                h = seg("hz-p", 3)
                best, pred, metrics = run_forecast(tuple(vals), h)
                st.plotly_chart(viz.trend_chart(years, vals, fc.next_years(years[-1], h), list(pred)), use_container_width=True, theme=None)
        with c2:
            with st.container(key="card-res"):
                card_head("Hasil prediksi", f"Model: {best}")
                st.markdown(table(pd.DataFrame({"Tahun ajaran": fc.next_years(years[-1], h), "Prediksi": pred.round(0).astype(int)})), unsafe_allow_html=True)
        with st.container(key="card-metrics"):
            card_head("Perbandingan model", "Dua tahun ajaran terakhir dipakai sebagai data uji. Baris hijau adalah model terbaik (MAPE terendah).")
            st.markdown(table(metrics, best=True), unsafe_allow_html=True)
            st.markdown(f"<div class='note'>MAPE di bawah 10% tergolong sangat baik. Model terbaik saat ini: <b>{best}</b> (MAPE {metrics.iloc[0]['MAPE (%)']:.2f}%).</div>", unsafe_allow_html=True)

    # ---------- Unggah Data (Operator) ----------
    elif page == "Unggah":
        header("Unggah Data")
        with st.container(key="card-upload"):
            card_head("Unggah berkas", "Gunakan templat agar kolom sesuai. Berkas yang salah format akan ditolak beserta alasannya.")
            st.download_button("Unduh templat", data.template_xlsx(), "Template_Data_Kesiswaan.xlsx", icon=":material/download:")
            up = st.file_uploader("Berkas Excel (.xlsx)", type=["xlsx"])
            if up:
                new = pd.read_excel(up)
                errs = validation.validate(new)
                sig = (up.name, up.size)
                if st.session_state.get("last_up") != sig:  # catat sekali per berkas
                    st.session_state["last_up"] = sig
                    ta = "–" if errs else f"{new['tahun_ajaran'].min()} – {new['tahun_ajaran'].max()}"
                    uploads().insert(0, (up.name, role, ta, "rj" if errs else "ok", "Ditolak" if errs else "Berhasil", STAMP))
                if errs:
                    st.error("Berkas ditolak. Perbaiki hal berikut lalu unggah lagi:")
                    for e in errs[:20]:
                        st.write("• " + e)
                else:
                    st.success(f"{len(new)} baris lolos validasi.")
                    st.dataframe(new.head(20), hide_index=True)
                    if st.button("Simpan data"):
                        st.session_state["data"], st.session_state["is_demo"] = new, False  # TODO: simpan ke Supabase
                        st.rerun()

    # ---------- Rekap Kelas & Laporan ----------
    else:
        pv = aktif.pivot_table(index="tahun_ajaran", columns="tingkat", values="jumlah", aggfunc="sum").reindex(columns=data.TINGKAT).fillna(0).astype(int)
        rk = pv.reset_index()
        rk["Total"] = pv.sum(axis=1).values
        rk.columns = ["Tahun ajaran"] + [f"Kelas {t}" for t in data.TINGKAT] + ["Total"]
        if page == "Kelas":
            header("Rekap Kelas")
            with st.container(key="card-kelas"):
                card_head("Jumlah peserta didik per tingkat", "Siswa berstatus aktif per tahun ajaran")
                st.markdown(table(rk.iloc[::-1]), unsafe_allow_html=True)
        else:
            header("Laporan")
            with st.container(key="card-laporan"):
                card_head("Unduh rekap data", "Rekap per tingkat dalam format Excel")
                buf = BytesIO()
                rk.to_excel(buf, index=False, sheet_name="Per Tingkat")
                st.download_button("Unduh rekap (Excel)", buf.getvalue(), "Rekap_Kesiswaan.xlsx", icon=":material/download:")
