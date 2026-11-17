from datetime import date

import numpy as np
import pandas as pd
import streamlit as st

from src import auth, data, forecasting as fc, styles, validation
from src import visualization as viz

st.set_page_config(page_title="Dashboard MTs Al-Falahiyyah", page_icon="🎓", layout="wide")
st.markdown(styles.CSS, unsafe_allow_html=True)
role = auth.require_login()
df = data.load()

BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
TODAY = f"{date.today().day} {BULAN[date.today().month - 1]} {date.today().year}"

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
                cells += "<td>–</td>" if pd.isna(v) else f"<td><span class='{'up' if v >= 0 else 'down'}'>{'▲' if v >= 0 else '▼'} {abs(v):.1f}%</span></td>".replace(".", ",")
            elif isinstance(v, (int, np.integer)):
                cells += f"<td>{fmt(v)}</td>"
            elif isinstance(v, (float, np.floating)):
                cells += f"<td>{v:.2f}</td>".replace(".", ",")
            else:
                cells += f"<td>{v}</td>"
        body += f"<tr class='{'best' if best and i == 0 else ''}'>{cells}</tr>"
    return f"<table class='tbl'><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"

def header(title, sub):
    demo = "<span class='badge'>Data contoh</span>" if st.session_state.get("is_demo") else ""
    st.markdown(f"<div class='topbar'><div><div class='page-title'>{title}</div><div class='page-sub'>{sub}</div></div>"
                f"<div class='chip'><span class='av'>{role[0]}</span>{role}{demo}</div></div>", unsafe_allow_html=True)

def card_head(title, sub=""):
    st.markdown(f"<div class='card-title'>{title}</div><div class='card-sub'>{sub}</div>", unsafe_allow_html=True)

def seg(name, default=1):
    cur = st.session_state.setdefault(name, default)
    cols = st.columns([1, 1, 1, 6])
    for c, o in zip(cols, [1, 2, 3]):
        if c.button(f"{o} tahun", key=f"seg-{'on' if cur == o else 'off'}-{name}-{o}", use_container_width=True):
            st.session_state[name] = o
            st.rerun()
    return st.session_state[name]

@st.cache_data
def run_forecast(values: tuple, h: int):
    return fc.forecast(list(values), h)

# ---------- sidebar ----------
PAGES = [("Dashboard", "Dashboard", ":material/dashboard:"), ("Peramalan", "Peramalan", ":material/query_stats:")]
if role == "Operator":
    PAGES.append(("Unggah", "Unggah data", ":material/upload_file:"))
page = st.session_state.setdefault("page", "Dashboard")
with st.sidebar:
    st.markdown("<div class='brand'><i>🎓</i>MTs Al-Falahiyyah</div>", unsafe_allow_html=True)
    for pid, label, icon in PAGES:
        if st.button(label, icon=icon, key=f"nav-{'on' if page == pid else 'off'}-{pid}", use_container_width=True):
            st.session_state["page"] = pid
            st.rerun()
    st.markdown("<div style='height:44vh'></div>", unsafe_allow_html=True)
    if st.button("Keluar", icon=":material/logout:", key="logout", use_container_width=True):
        auth.logout()

aktif = df[df["status"] == "Aktif"]
tot = aktif.groupby("tahun_ajaran")["jumlah"].sum().sort_index()
years, vals = list(tot.index), [int(v) for v in tot.values]
latest, prev = vals[-1], vals[-2]
pct = (latest - prev) / prev * 100

# ---------- Dashboard ----------
if page == "Dashboard":
    header("Dashboard", f"Ringkasan kesiswaan · {TODAY}")
    best, pred, _ = run_forecast(tuple(vals), 1)
    nxt = fc.next_years(years[-1], 1)[0]
    neg = pct < 0
    kpis = ("<div class='kpi-row'>"
            + viz.kpi("dark", f"Peserta didik {years[-1]}", fmt(latest), f"{latest - prev:+d} dari tahun ajaran lalu", viz.sparkline(vals, "#A5D17A"))
            + viz.kpi("light", f"Prediksi {nxt}", fmt(pred[0]), f"Model: {best}", viz.sparkline(vals + [pred[0]], "#2F5D50"))
            + viz.kpi("black", "Perubahan tahunan", f"{pct:+.1f}%".replace(".", ","), "Menurun dari tahun lalu" if neg else "Meningkat dari tahun lalu", viz.sparkline(vals, viz.RED if neg else "#A5D17A"))
            + "</div>")
    left, right = st.columns([2.7, 1.15], gap="medium")
    with left:
        st.markdown(kpis, unsafe_allow_html=True)
        with st.container(key="card-trend"):
            card_head("Perkembangan jumlah peserta didik", "Data aktual per tahun ajaran dan proyeksi ke depan")
            h = seg("hz")
            _, p, _ = run_forecast(tuple(vals), h)
            st.plotly_chart(viz.trend_chart(years, vals, fc.next_years(years[-1], h), list(p)), use_container_width=True, theme=None)
        with st.container(key="card-rekap"):
            card_head("Rekap per tahun ajaran")
            g = aktif.pivot_table(index="tahun_ajaran", columns="jenis_kelamin", values="jumlah", aggfunc="sum")
            rekap = pd.DataFrame({"Tahun ajaran": g.index, "Laki-laki": g["L"].values, "Perempuan": g["P"].values, "Total": tot.values})
            rekap["Perubahan"] = rekap["Total"].pct_change().mul(100)
            st.markdown(table(rekap.iloc[::-1], delta="Perubahan"), unsafe_allow_html=True)
    with right:
        with st.container(key="card-dist"):
            card_head("Sebaran per tingkat", f"Tahun ajaran {years[-1]}")
            tk = aktif[aktif.tahun_ajaran == years[-1]].groupby("tingkat")["jumlah"].sum().reindex(data.TINGKAT)
            st.markdown("".join(f"<div class='row'><span>Kelas {t}</span><b>{int(v)}</b></div><div class='bar'><i style='width:{v / tk.max() * 100:.0f}%'></i></div>" for t, v in tk.items()), unsafe_allow_html=True)
        with st.container(key="card-gender"):
            card_head("Komposisi jenis kelamin", f"Tahun ajaran {years[-1]}")
            gk = aktif[aktif.tahun_ajaran == years[-1]].groupby("jenis_kelamin")["jumlah"].sum()
            st.plotly_chart(viz.donut(["Laki-laki", "Perempuan"], [gk["L"], gk["P"]], fmt(latest)), use_container_width=True, theme=None)
            st.markdown(f"<div class='legend'><span><i class='dot' style='background:#2F5D50'></i>Laki-laki</span><b>{gk['L'] / latest * 100:.0f}%</b></div>"
                        f"<div class='legend'><span><i class='dot' style='background:#A5D17A'></i>Perempuan</span><b>{gk['P'] / latest * 100:.0f}%</b></div>", unsafe_allow_html=True)

# ---------- Peramalan ----------
elif page == "Peramalan":
    header("Peramalan", "Proyeksi jumlah peserta didik")
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

# ---------- Unggah data ----------
else:
    header("Unggah data", "Perbarui data kesiswaan dengan templat Excel")
    with st.container(key="card-upload"):
        card_head("Unggah berkas", "Gunakan templat agar kolom sesuai. Berkas yang salah format akan ditolak beserta alasannya.")
        st.download_button("Unduh templat", data.template_xlsx(), "Template_Data_Kesiswaan.xlsx", icon=":material/download:")
        up = st.file_uploader("Berkas Excel (.xlsx)", type=["xlsx"])
        if up:
            new = pd.read_excel(up)
            errs = validation.validate(new)
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
