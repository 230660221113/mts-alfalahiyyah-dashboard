import streamlit as st

from data.repository import get_repo
from data.transform import per_class, yearly_totals
from ui import charts


def render() -> None:
    st.header("Dashboard Kesiswaan")
    df = get_repo().fetch_all()
    if df.empty:
        st.info("Belum ada data. Operator dapat mengunggah data pada menu **Unggah Data**.")
        return

    tot = yearly_totals(df)
    last = tot.iloc[-1]
    prev = tot.iloc[-2] if len(tot) > 1 else None
    delta = int(last["total"] - prev["total"]) if prev is not None else None
    growth = (tot["total"].pct_change().mean() * 100) if len(tot) > 1 else None

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Total siswa {last['tahun_ajaran']}", f"{int(last['total']):,}", delta)
    c2.metric("Laki-laki", f"{int(last['laki_laki']):,}")
    c3.metric("Perempuan", f"{int(last['perempuan']):,}")
    c4.metric("Rata-rata pertumbuhan/tahun", f"{growth:+.1f}%" if growth is not None else "-")

    left, right = st.columns(2)
    with left:
        st.subheader("Tren total siswa")
        st.altair_chart(charts.trend_line(tot), use_container_width=True)
    with right:
        st.subheader("Komposisi per kelas")
        st.altair_chart(charts.class_bars(per_class(df)), use_container_width=True)

    st.subheader("Komposisi jenis kelamin")
    st.altair_chart(charts.gender_bars(tot), use_container_width=True)

    with st.expander("Lihat tabel data"):
        st.dataframe(tot.drop(columns="mulai"), hide_index=True, use_container_width=True)


render()
