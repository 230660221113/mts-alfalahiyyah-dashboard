CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, .stApp, [class*="css"] { font-family: 'Plus Jakarta Sans', system-ui, sans-serif; }
.stApp, [data-testid="stAppViewContainer"] { background: #0C241E; color: #14221D; }
[data-testid="stMain"] { background: #F4F7F5; border-radius: 24px; margin: 6px; min-height: calc(100vh - 12px); }
[data-testid="stToolbar"], [data-testid="stDecoration"], footer, #MainMenu { display: none !important; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding: 1.4rem 1.6rem 2rem; max-width: 1400px; }

/* sidebar gelap */
[data-testid="stSidebar"] { background: radial-gradient(120% 55% at 0% 100%, rgba(52,160,120,.42), transparent 62%), #0C241E; border-right: 0; min-width: 264px; }
[data-testid="stSidebar"] > div, [data-testid="stSidebarContent"] { background: transparent !important; }
.logo { display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 18px; color: #fff; padding: 0 8px 22px; }
.logo i { width: 36px; height: 36px; border-radius: 10px; background: #A5D17A; color: #0C241E; display: grid; place-items: center; font-style: normal; }
.sbcard { border: 1px solid rgba(255,255,255,.16); border-radius: 18px; padding: 16px; background: rgba(255,255,255,.07); color: #fff; font-size: 14px; font-weight: 600; }
.sbcard small { display: block; color: #A9C7B8; font-weight: 500; margin-top: 2px; }
.seg { display: flex; gap: 4px; margin: 14px 0 2px; }
.seg i { flex: 1; height: 22px; border-radius: 3px; background: #A5D17A; }
.seg i.o { background: rgba(255,255,255,.18); }
.me { display: flex; align-items: center; gap: 12px; padding: 16px 8px 6px; color: #fff; font-size: 14px; font-weight: 700; }
.me small { display: block; color: #A9C7B8; font-weight: 500; font-size: 12px; }
.av { width: 38px; height: 38px; border-radius: 50%; background: #A5D17A; color: #0C241E; font-weight: 800; display: grid; place-items: center; flex: none; }

/* tombol */
.stButton > button, .stDownloadButton > button { background: #1F7A5C; color: #fff; border: 0; border-radius: 10px; font-weight: 600; padding: .5rem 1.1rem; box-shadow: none; }
.stButton > button:hover, .stDownloadButton > button:hover { background: #17604A; color: #fff; }
.stButton > button *, .stDownloadButton > button * { color: inherit !important; }
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible { outline: 3px solid #A5D17A; }
[class*="st-key-nav-"] button, .st-key-logout button { justify-content: flex-start; background: transparent !important; color: #C9DAD3 !important; border: 1px solid transparent !important; padding: .7rem .9rem; border-radius: 12px; font-size: 15px; }
[class*="st-key-nav-"] button:hover, .st-key-logout button:hover { background: rgba(255,255,255,.08) !important; color: #fff !important; }
[class*="st-key-nav-on-"] button, [class*="st-key-nav-on-"] button:hover { background: rgba(255,255,255,.10) !important; border-color: rgba(255,255,255,.18) !important; color: #fff !important; }
[class*="st-key-seg-"] button { background: #fff; color: #4A5A53; border: 1px solid #DCE6E0; border-radius: 8px; padding: .22rem .6rem; min-height: 0; font-size: .8rem; }
[class*="st-key-seg-"] button:hover { background: #F0F4F2; color: #14221D; }
[class*="st-key-seg-on-"] button, [class*="st-key-seg-on-"] button:hover { background: #1F7A5C; color: #fff; border-color: #1F7A5C; }

/* judul halaman */
.top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.top h1 { margin: 0; font-size: 28px; font-weight: 800; color: #14221D; }
.badge { background: #FFF1D1; color: #7A5600; border-radius: 999px; padding: 5px 12px; font-size: 12px; font-weight: 700; }

/* panel sapaan dan kartu */
.st-key-hero { background: #E8EFEB; border: 1px solid #DCE6E0; border-radius: 22px; padding: 18px; }
[class*="st-key-card-"] { background: #fff; border: 1px solid #E1E8E4; border-radius: 18px; padding: 16px 18px 10px; }
.hl h2 { margin: 6px 0 4px; font-size: 26px; font-weight: 800; color: #14221D; }
.hl p { margin: 0 0 18px; color: #5E6E67; font-size: 14px; max-width: 440px; line-height: 1.5; }
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.sc { background: #fff; border: 1px solid #E1E8E4; border-radius: 18px; padding: 16px; display: flex; flex-direction: column; min-height: 206px; }
.ic { width: 40px; height: 40px; border-radius: 50%; display: grid; place-items: center; }
.ic svg, .dl svg { fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.ic svg { width: 20px; height: 20px; }
.sc b { font-size: 32px; font-weight: 800; margin-top: 16px; letter-spacing: -.5px; color: #14221D; }
.sc .l { color: #4A5A53; font-size: 14px; margin-top: 2px; }
.dl { margin-top: auto; display: flex; align-items: center; gap: 6px; font-weight: 700; font-size: 13px; }
.dl svg { width: 16px; height: 16px; }
.dl span { color: #5E6E67; font-weight: 500; }
.up { color: #1E7B4A; } .dn { color: #B3312A; }
.card-title { font-weight: 700; font-size: 1.05rem; color: #14221D; margin: 0; }
.card-sub { font-size: .8rem; color: #5E6E67; margin: 2px 0 10px; }
.lg { display: flex; gap: 16px; font-size: 12.5px; color: #4A5A53; margin: 4px 0 0; }
.lg i { display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 6px; background: #1F7A5C; }
.lg i.f { background: #DDEFC9; border: 1.5px solid #6FA83A; }

/* tabel riwayat dan rekap */
.th { display: flex; justify-content: space-between; align-items: center; margin: 22px 0 12px; }
.th h3 { margin: 0; font-size: 20px; font-weight: 700; color: #14221D; }
.pillb { border: 1px solid #E1E8E4; background: #fff; border-radius: 10px; padding: 8px 14px; font-size: 13px; font-weight: 600; color: #14221D; }
.st-key-card-hist { padding: 0; overflow-x: auto; }
.tbl { width: 100%; border-collapse: collapse; font-size: 14px; color: #14221D; }
.tbl th { text-align: right; font-weight: 700; color: #14221D; font-size: .82rem; padding: 14px 20px; background: #EDF2EF; }
.tbl td { text-align: right; padding: 13px 20px; border-bottom: 1px solid #EEF2EF; }
.tbl th:first-child, .tbl td:first-child { text-align: left; }
.tbl.left th, .tbl.left td { text-align: left; }
.tbl tr:last-child td { border-bottom: 0; }
.tbl tr.best td { background: #F2F8EE; font-weight: 700; }
.fn { display: flex; align-items: center; gap: 12px; font-weight: 600; }
.fn i { width: 32px; height: 32px; border-radius: 10px; background: #E3F0E9; color: #1F7A5C; display: grid; place-items: center; }
.fn svg { width: 16px; height: 16px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.chip { display: inline-flex; align-items: center; gap: 7px; padding: 4px 12px; border-radius: 999px; font-size: 12.5px; font-weight: 600; }
.chip::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.ok { background: #E3F5EA; color: #176B3F; } .wt { background: #FFF1D1; color: #7A5600; } .rj { background: #FDE3E1; color: #9E2A24; }
.note { font-size: .82rem; color: #5E6E67; margin-top: 10px; }

/* input */
[data-testid="stWidgetLabel"] p { color: #14221D !important; font-weight: 600; font-size: .85rem; }
[data-baseweb="input"], [data-baseweb="base-input"] { background: #fff !important; border-radius: 10px; }
[data-baseweb="input"] { border: 1px solid #D5DDD8 !important; }
[data-baseweb="input"]:focus-within { border-color: #1F7A5C !important; box-shadow: 0 0 0 3px rgba(31,122,92,.18); }
input { color: #14221D !important; }
[data-testid="stFileUploaderDropzone"] { background: #fff; border: 1px dashed #B9C6BF; border-radius: 12px; }
[data-testid="stFileUploaderDropzone"] * { color: #4A5A53; }

/* halaman masuk */
[data-testid="stForm"] { border: 0; padding: 0; }
[data-testid="stFormSubmitButton"] button { background: #1F7A5C; color: #fff; border: 0; border-radius: 10px; font-weight: 700; padding: .6rem 1rem; }
[data-testid="stFormSubmitButton"] button:hover { background: #17604A; color: #fff; }
.login-title { font-size: 1.9rem; font-weight: 800; color: #14221D; margin: 0 0 .3rem; }
.login-sub { color: #5E6E67; font-size: .92rem; margin-bottom: 1.4rem; }
.demo-hint { background: #EEF5EA; border: 1px solid #D5E6C8; border-radius: 12px; padding: 10px 14px; font-size: .8rem; color: #3C5A33; margin-top: 14px; }
.hero { background: radial-gradient(120% 55% at 0% 100%, rgba(52,160,120,.42), transparent 62%), #0C241E; border-radius: 24px; padding: 36px; color: #fff; min-height: 82vh; display: flex; flex-direction: column; justify-content: space-between; }
.hero h2 { font-size: 1.7rem; font-weight: 800; line-height: 1.25; margin: 0 0 .5rem; color: #fff; }
.hero p { color: #CFE3D8; font-size: .92rem; margin: 0; }
.mini { background: #fff; color: #14221D; border-radius: 16px; padding: 16px 18px; margin-bottom: 14px; box-shadow: 0 10px 30px rgba(0,0,0,.18); position: relative; }
.mini.b { margin-left: 44px; }
.mini .l { font-size: .78rem; color: #5E6E67; font-weight: 600; }
.mini .n { font-size: 1.3rem; font-weight: 800; }
.mini svg { position: absolute; right: 16px; bottom: 14px; width: 92px; height: 34px; }
.hero .note { font-size: .72rem; color: #A9C7B8; }
@media (max-width: 900px) { .stats { grid-template-columns: 1fr; } .block-container { padding: 1rem; } }
</style>
"""

from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import streamlit as st

BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

I_TREND = "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M3 17l6-6 4 4 8-8M15 7h6v6'/></svg>"
I_SPARK = "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M12 3l2 5.5L19.5 10 14 12l-2 5.5L10 12 4.5 10 10 8.5z'/></svg>"
I_USERS = "<svg viewBox='0 0 24 24' aria-hidden='true'><circle cx='9' cy='8' r='3.5'/><path d='M2.5 20c.6-3.6 3.2-5.5 6.5-5.5s5.9 1.9 6.5 5.5M16 4.5a3.5 3.5 0 010 7M18 14.8c1.8.7 3 2.3 3.5 5.2'/></svg>"
I_CAP = "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M2 9l10-5 10 5-10 5zM6 11.5V16c0 1.5 3 3 6 3s6-1.5 6-3v-4.5'/></svg>"
I_CLOCK = "<svg viewBox='0 0 24 24' aria-hidden='true'><circle cx='12' cy='12' r='9'/><path d='M12 7v5l3 2'/></svg>"
I_BUILD = "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M4 21V8l8-5 8 5v13M9 21v-6h6v6'/></svg>"
I_UP = "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M12 19V5M6 11l6-6 6 6'/></svg>"
I_DOWN = "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M12 5v14M6 13l6 6 6-6'/></svg>"
I_FILE = "<svg viewBox='0 0 24 24' aria-hidden='true'><path d='M6 3h8l5 5v13H6zM14 3v5h5'/></svg>"


def now_wib():
    return datetime.now(timezone(timedelta(hours=7)))


def sapa():
    h = now_wib().hour
    return "pagi" if h < 11 else "siang" if h < 15 else "sore" if h < 18 else "malam"


def today():
    n = now_wib()
    return f"{n.day} {BULAN[n.month - 1]} {n.year}"


def fmt(n):
    return f"{int(round(n)):,}".replace(",", ".")


def stat(icon, bg, fg, value, label, foot, cls=""):
    return (f"<div class='sc'><span class='ic' style='background:{bg};color:{fg}'>{icon}</span><b>{value}</b>"
            f"<span class='l'>{label}</span><div class='dl {cls}'>{foot}</div></div>")


def delta_foot(diff, pct):
    up = diff >= 0
    return (I_UP if up else I_DOWN) + f"{abs(pct):.1f}".replace(".", ",") + "% <span>dari tahun lalu</span>", "up" if up else "dn"


def header(title, demo=False):
    badge = "<span class='badge'>Data contoh</span>" if demo else ""
    st.markdown(f"<div class='top'><h1>{title}</h1>{badge}</div>", unsafe_allow_html=True)


def card_head(title, sub=""):
    st.markdown(f"<div class='card-title'>{title}</div><div class='card-sub'>{sub}</div>", unsafe_allow_html=True)


def table(d, delta=None, left=False):
    head = "".join(f"<th>{c}</th>" for c in d.columns)
    body = ""
    for _, r in d.iterrows():
        cells = ""
        for c in d.columns:
            v = r[c]
            if c == delta:
                cells += "<td>–</td>" if pd.isna(v) else (f"<td><span class='{'up' if v >= 0 else 'dn'}'>{'▲' if v >= 0 else '▼'} "
                                                          f"{abs(v):.1f}%</span></td>").replace(".", ",")
            elif isinstance(v, (int, np.integer)):
                cells += f"<td>{fmt(v)}</td>"
            else:
                cells += f"<td>{v}</td>"
        body += f"<tr>{cells}</tr>"
    return f"<table class='tbl{' left' if left else ''}'><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def seg(name, default=1):
    cur = st.session_state.setdefault(name, default)
    cols = st.columns([1, 1, 1, 3])
    for c, o in zip(cols, [1, 2, 3]):
        if c.button(f"{o} tahun", key=f"seg-{'on' if cur == o else 'off'}-{name}-{o}", use_container_width=True):
            st.session_state[name] = o
            st.rerun()
    return st.session_state[name]
