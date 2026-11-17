"""Modul desain & komponen UI modern untuk Dashboard Analitik Kesiswaan."""
from __future__ import annotations

import streamlit as st


def inject_global_css() -> None:
    """Menyuntikkan CSS kustom untuk tampilan modern, card KPI, banner hero, dan tipografi."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Latar belakang utama lembut */
        .stApp {
            background-color: #F4F7FB;
        }

        /* Padding container utama */
        .block-container {
            padding-top: 1.75rem !important;
            padding-bottom: 2.5rem !important;
            max-width: 1280px;
        }

        /* Styling Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0D2B4E 0%, #143D6B 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }
        [data-testid="stSidebar"] * {
            color: #F1F5F9 !important;
        }
        [data-testid="stSidebar"] .stButton > button {
            background-color: rgba(255, 255, 255, 0.12) !important;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
            color: #FFFFFF !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background-color: rgba(255, 255, 255, 0.22) !important;
            border-color: #FFFFFF !important;
        }
        [data-testid="stSidebarNav"] a {
            border-radius: 10px !important;
            margin: 2px 8px !important;
            padding: 8px 12px !important;
            transition: background 0.2s ease;
        }
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background-color: rgba(255, 255, 255, 0.18) !important;
            font-weight: 700 !important;
        }

        /* Hero Banner Header */
        .hero-banner {
            background: linear-gradient(135deg, #0F4C81 0%, #1B6CA8 60%, #1687A7 100%);
            padding: 1.6rem 2rem;
            border-radius: 16px;
            color: #FFFFFF;
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 25px -5px rgba(15, 76, 129, 0.22);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }
        .hero-banner h1 {
            margin: 0;
            font-size: 1.65rem;
            font-weight: 800;
            color: #FFFFFF !important;
            letter-spacing: -0.02em;
        }
        .hero-banner p {
            margin: 0.35rem 0 0 0;
            font-size: 0.92rem;
            color: rgba(255, 255, 255, 0.88) !important;
        }
        .hero-badge {
            background: rgba(255, 255, 255, 0.16);
            backdrop-filter: blur(6px);
            border: 1px solid rgba(255, 255, 255, 0.28);
            padding: 0.45rem 0.95rem;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 600;
            color: #FFFFFF;
            white-space: nowrap;
        }

        /* Kartu KPI Modern */
        .kpi-card {
            background: #FFFFFF;
            border-radius: 14px;
            padding: 1.2rem 1.35rem;
            border: 1px solid #E2E8F0;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
            transition: transform 0.18s ease, box-shadow 0.18s ease;
            height: 100%;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
        }
        .kpi-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.55rem;
        }
        .kpi-label {
            font-size: 0.82rem;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }
        .kpi-icon {
            width: 34px;
            height: 34px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.05rem;
            font-weight: 700;
        }
        .kpi-value {
            font-size: 1.85rem;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.15;
            margin-bottom: 0.45rem;
        }
        .kpi-sub {
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 2px 8px;
            border-radius: 6px;
        }
        .badge-up {
            background-color: #DCFCE7;
            color: #15803D;
        }
        .badge-down {
            background-color: #FEE2E2;
            color: #B91C1C;
        }
        .badge-neutral {
            background-color: #F1F5F9;
            color: #475569;
        }

        /* Section Card Wrapper (st.container(border=True)) */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border-radius: 16px !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.035) !important;
            padding: 0.35rem 0.5rem !important;
        }

        /* Judul Kartu Grafik */
        .chart-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 0.1rem;
        }
        .chart-subtitle {
            font-size: 0.82rem;
            color: #64748B;
            margin-bottom: 0.85rem;
        }

        /* Tombol Utama */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #0F4C81 0%, #1B6CA8 100%) !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 0.55rem 1.2rem !important;
            box-shadow: 0 4px 10px rgba(15, 76, 129, 0.25) !important;
        }
        .stButton > button[kind="primary"]:hover {
            opacity: 0.94;
        }

        /* Sidebar User Card */
        .sidebar-profile {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.16);
            border-radius: 12px;
            padding: 0.85rem 1rem;
            margin-bottom: 0.75rem;
        }
        .sidebar-school {
            font-size: 0.95rem;
            font-weight: 700;
            color: #FFFFFF !important;
            margin-bottom: 2px;
        }
        .sidebar-role {
            font-size: 0.78rem;
            color: #CBD5E1 !important;
        }

        /* Login Card */
        .login-header {
            text-align: center;
            margin-bottom: 1.25rem;
        }
        .login-logo {
            width: 56px;
            height: 56px;
            margin: 0 auto 0.75rem auto;
            background: linear-gradient(135deg, #0F4C81, #1687A7);
            color: #FFFFFF;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.6rem;
            box-shadow: 0 8px 18px rgba(15, 76, 129, 0.25);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str, subtitle: str, badge_text: str = "") -> None:
    """Merender banner header dengan gradasi profesional di bagian atas halaman."""
    badge_html = f'<div class="hero-badge">{badge_text}</div>' if badge_text else ""
    st.markdown(
        f"""
        <div class="hero-banner">
            <div>
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(
    label: str,
    value: str,
    subtext: str,
    badge_type: str = "neutral",
    icon: str = "📊",
    icon_bg: str = "#E0F2FE",
    icon_color: str = "#0369A1",
) -> None:
    """Merender kartu metrik KPI dengan ikon, angka besar, dan pil status."""
    badge_cls = {
        "up": "badge-up",
        "down": "badge-down",
        "neutral": "badge-neutral",
    }.get(badge_type, "badge-neutral")

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-label">{label}</span>
                <div class="kpi-icon" style="background:{icon_bg}; color:{icon_color};">{icon}</div>
            </div>
            <div class="kpi-value">{value}</div>
            <span class="kpi-sub {badge_cls}">{subtext}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
