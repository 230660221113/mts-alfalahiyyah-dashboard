import streamlit as st

from core.config import school_name
from data.repository import get_repo
from data.transform import per_class, yearly_totals
from ui import charts
from ui.styles import render_hero, render_kpi_card


def render() -> None:
    df = get_repo().fetch_all()
    tot = yearly_totals(df)

    latest_ta = tot.iloc[-1]["tahun_ajaran"] if not tot.empty else "Belum Ada Data"
    render_hero(
        title="Dashboard Analitik Kesiswaan",
        subtitle=f"Visualisasi rekapitulasi historis, distribusi tingkat kelas, dan demografi peserta didik {school_name()}.",
        badge_text=f"📅 Tahun Ajaran Terkini: {latest_ta}",
    )

    if df.empty:
        st.info("Belum ada data kesiswaan. Operator dapat mengunggah berkas rekap melalui menu **Unggah Data**.")
        return

    last = tot.iloc[-1]
    prev = tot.iloc[-2] if len(tot) > 1 else None
    delta = int(last["total"] - prev["total"]) if prev is not None else None
    growth = (tot["total"].pct_change().mean() * 100) if len(tot) > 1 else None

    total_now = int(last["total"])
    laki_now = int(last["laki_laki"])
    perempuan_now = int(last["perempuan"])
    pct_l = (laki_now / total_now * 100) if total_now > 0 else 0
    pct_p = (perempuan_now / total_now * 100) if total_now > 0 else 0

    if delta is not None:
        delta_txt = f"{'▲' if delta >= 0 else '▼'} {delta:+d} siswa dari TA {prev['tahun_ajaran']}"
        delta_type = "up" if delta >= 0 else "down"
    else:
        delta_txt = "Tahun ajaran pertama"
        delta_type = "neutral"

    growth_val = f"{growth:+.1f}%" if growth is not None else "-"
    growth_sub = f"Rata-rata {len(tot)} tahun ajaran"
    growth_type = "up" if (growth is not None and growth >= 0) else "neutral"

    # Baris 1: 4 Kartu KPI Modern
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card(
            label=f"Total Siswa ({last['tahun_ajaran']})",
            value=f"{total_now:,}",
            subtext=delta_txt,
            badge_type=delta_type,
            icon="👥",
            icon_bg="#E0F2FE",
            icon_color="#0369A1",
        )
    with c2:
        render_kpi_card(
            label="Peserta Didik Laki-laki",
            value=f"{laki_now:,}",
            subtext=f"{pct_l:.1f}% dari total siswa",
            badge_type="neutral",
            icon="👦",
            icon_bg="#DBEAFE",
            icon_color="#1D4ED8",
        )
    with c3:
        render_kpi_card(
            label="Peserta Didik Perempuan",
            value=f"{perempuan_now:,}",
            subtext=f"{pct_p:.1f}% dari total siswa",
            badge_type="neutral",
            icon="👧",
            icon_bg="#D1FAE5",
            icon_color="#047857",
        )
    with c4:
        render_kpi_card(
            label="Pertumbuhan / Tahun",
            value=growth_val,
            subtext=growth_sub,
            badge_type=growth_type,
            icon="📈",
            icon_bg="#FEF3C7",
            icon_color="#B45309",
        )

    st.markdown("<div style='height: 1.1rem;'></div>", unsafe_allow_html=True)

    # Baris 2: Grafik Tren & Komposisi Kelas dalam Card
    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Tren Total Peserta Didik</div>', unsafe_allow_html=True)
            st.markdown('<div class="chart-subtitle">Perkembangan jumlah keseluruhan siswa aktif per tahun ajaran</div>', unsafe_allow_html=True)
            st.altair_chart(charts.trend_line(tot), use_container_width=True)

    with right:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Komposisi per Tingkat Kelas</div>', unsafe_allow_html=True)
            st.markdown('<div class="chart-subtitle">Distribusi siswa pada jenjang Kelas VII, VIII, dan IX</div>', unsafe_allow_html=True)
            st.altair_chart(charts.class_bars(per_class(df)), use_container_width=True)

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # Baris 3: Grafik Demografi Jenis Kelamin dalam Card
    with st.container(border=True):
        st.markdown('<div class="chart-title">Komposisi Berdasarkan Jenis Kelamin</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-subtitle">Perbandingan jumlah siswa laki-laki dan perempuan antar tahun ajaran</div>', unsafe_allow_html=True)
        st.altair_chart(charts.gender_bars(tot), use_container_width=True)

    with st.expander("📋 Lihat Ringkasan Tabel Data Historis"):
        display_df = tot.drop(columns="mulai").rename(
            columns={
                "tahun_ajaran": "Tahun Ajaran",
                "laki_laki": "Laki-laki",
                "perempuan": "Perempuan",
                "total": "Total Siswa",
            }
        )
        st.dataframe(display_df, hide_index=True, use_container_width=True)


render()
