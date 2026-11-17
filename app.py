from datetime import date

import pandas as pd
import streamlit as st

from src import auth, data, forecasting as fc, styles, validation
from src import visualization as viz

st.set_page_config(page_title="Dashboard MTs Al-Falahiyyah", page_icon="🎓", layout="wide")
st.markdown(styles.CSS, unsafe_allow_html=True)
role = auth.require_login()
df = data.load()

pages = ["Dashboard", "Peramalan"] + (["Unggah Data"] if role == "Operator" else [])
with st.sidebar:
    st.markdown("<div class='brand'>🎓 MTs Al-Falahiyyah</div>", unsafe_allow_html=True)
    page = st.radio("Menu", pages, label_visibility="collapsed")
    st.markdown("<div style='height:40vh'></div>", unsafe_allow_html=True)
    st.caption(f"Masuk sebagai {role}")
    if st.button("Keluar"):
        auth.logout()

@st.cache_data
def run_forecast(values: tuple, h: int):
    return fc.forecast(list(values), h)

aktif = df[df["status"] == "Aktif"]
tot = aktif.groupby("tahun_ajaran")["jumlah"].sum().sort_index()
years, vals = list(tot.index), [int(v) for v in tot.values]
latest, prev = vals[-1], vals[-2]
pct = (latest - prev) / prev * 100

def header(title):
    st.markdown(f"<div class='page-title'>{title}</div><div class='page-sub'>{date.today():%d-%m-%Y}"
                f"{' · menampilkan data contoh' if st.session_state.get('is_demo') else ''}</div>", unsafe_allow_html=True)

# ---------------- Dashboard ----------------
if page == "Dashboard":
    header("Dashboard")
    best, pred, metrics = run_forecast(tuple(vals), 1)
    nxt = fc.next_years(years[-1], 1)[0]
    neg = pct < 0
    kpis = "<div class='kpi-row'>" + \
        viz.kpi("dark", f"Peserta didik {years[-1]}", f"{latest:,}".replace(",", "."), f"{latest - prev:+d} dari tahun ajaran lalu", viz.sparkline(vals, "#A5D17A")) + \
        viz.kpi("light", f"Prediksi {nxt}", f"{pred[0]:.0f}", f"Model: {best}", viz.sparkline(vals + [pred[0]], "#2F5D50")) + \
        viz.kpi("black", "Perubahan tahunan", f"{pct:+.1f}%", "Menurun" if neg else "Meningkat", viz.sparkline(vals, viz.RED if neg else "#A5D17A")) + "</div>"
    left, right = st.columns([2.6, 1.15], gap="medium")
    with left:
        st.markdown(kpis, unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div class='card-title'>Perkembangan jumlah peserta didik</div>", unsafe_allow_html=True)
            h = st.segmented_control("Proyeksi", [1, 2, 3], default=1, format_func=lambda x: f"{x} tahun", label_visibility="collapsed") or 1
            _, p, _ = run_forecast(tuple(vals), h)
            st.plotly_chart(viz.trend_chart(years, vals, fc.next_years(years[-1], h), list(p)), use_container_width=True)
        with st.container(border=True):
            st.markdown("<div class='card-title'>Rekap per tahun ajaran</div>", unsafe_allow_html=True)
            g = aktif.pivot_table(index="tahun_ajaran", columns="jenis_kelamin", values="jumlah", aggfunc="sum")
            rekap = pd.DataFrame({"Tahun ajaran": g.index, "Laki-laki": g["L"].values, "Perempuan": g["P"].values, "Total": tot.values})
            rekap["Perubahan (%)"] = rekap["Total"].pct_change().mul(100).round(1)
            st.dataframe(rekap.iloc[::-1], hide_index=True, use_container_width=True)
    with right:
        with st.container(border=True):
            st.markdown(f"<div class='card-title'>Sebaran per tingkat · {years[-1]}</div>", unsafe_allow_html=True)
            tk = aktif[aktif.tahun_ajaran == years[-1]].groupby("tingkat")["jumlah"].sum().reindex(data.TINGKAT)
            html = "".join(f"<div class='row'><span>Kelas {t}</span><b>{int(v)}</b></div><div class='bar'><i style='width:{v / tk.max() * 100:.0f}%'></i></div>" for t, v in tk.items())
            st.markdown(html, unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div class='card-title'>Komposisi jenis kelamin</div>", unsafe_allow_html=True)
            gk = aktif[aktif.tahun_ajaran == years[-1]].groupby("jenis_kelamin")["jumlah"].sum()
            st.plotly_chart(viz.donut(["Laki-laki", "Perempuan"], [gk["L"], gk["P"]], f"{latest} siswa"), use_container_width=True)
            st.markdown(f"<div class='legend'><span><i class='dot' style='background:#2F5D50'></i>Laki-laki</span><b>{gk['L'] / latest * 100:.0f}%</b></div>"
                        f"<div class='legend'><span><i class='dot' style='background:#A5D17A'></i>Perempuan</span><b>{gk['P'] / latest * 100:.0f}%</b></div>", unsafe_allow_html=True)

# ---------------- Peramalan ----------------
elif page == "Peramalan":
    header("Peramalan")
    h = st.slider("Proyeksi (tahun ajaran)", 1, 3, 3)
    best, pred, metrics = run_forecast(tuple(vals), h)
    c1, c2 = st.columns([2, 1], gap="medium")
    with c1, st.container(border=True):
        st.markdown(f"<div class='card-title'>Prediksi dengan model terbaik: {best}</div>", unsafe_allow_html=True)
        st.plotly_chart(viz.trend_chart(years, vals, fc.next_years(years[-1], h), list(pred)), use_container_width=True)
    with c2, st.container(border=True):
        st.markdown("<div class='card-title'>Hasil prediksi</div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({"Tahun ajaran": fc.next_years(years[-1], h), "Prediksi": pred.round(0).astype(int)}), hide_index=True, use_container_width=True)
    with st.container(border=True):
        st.markdown("<div class='card-title'>Perbandingan model (2 tahun terakhir sebagai data uji)</div>", unsafe_allow_html=True)
        st.dataframe(metrics.round(2), hide_index=True, use_container_width=True)

# ---------------- Unggah Data (Operator) ----------------
else:
    header("Unggah data")
    with st.container(border=True):
        st.download_button("Unduh templat", data.template_xlsx(), "Template_Data_Kesiswaan.xlsx")
        up = st.file_uploader("Berkas Excel sesuai templat", type=["xlsx"])
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
