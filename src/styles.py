CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Plus Jakarta Sans', system-ui, sans-serif; }
.stApp { background: #EEF1EE; }
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { padding: 1.4rem 2rem 2rem; max-width: 1400px; }

/* kartu */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: #fff; border: 1px solid #E3E8E4 !important; border-radius: 18px; padding: .35rem .5rem;
}
.card-title { font-weight: 700; font-size: 1.02rem; color: #1F2A27; margin: .1rem 0 .4rem; }
.page-title { font-size: 1.7rem; font-weight: 800; color: #1F2A27; margin: 0; }
.page-sub { color: #8A9792; font-size: .82rem; margin-bottom: 1rem; }

/* kartu KPI */
.kpi-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 14px; }
.kpi { border-radius: 16px; padding: 16px 18px; color: #fff; position: relative; min-height: 118px; }
.kpi.dark { background: #2F5D50; } .kpi.light { background: #A5D17A; color: #1F3A2E; } .kpi.black { background: #2B2F2E; }
.kpi .t { font-size: .85rem; font-weight: 600; opacity: .95; }
.kpi .v { font-size: 1.7rem; font-weight: 800; margin: 8px 0 2px; border-left: 3px solid currentColor; padding-left: 10px; line-height: 1.1; }
.kpi .d { font-size: .74rem; font-weight: 600; padding-left: 13px; opacity: .9; }
.kpi svg { position: absolute; right: 14px; bottom: 16px; width: 92px; height: 34px; }

/* daftar sebaran */
.row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; font-size: .86rem; color: #5F6D68; }
.row b { color: #1F2A27; font-size: .95rem; }
.bar { height: 6px; border-radius: 4px; background: #E3EBE5; margin-top: 4px; }
.bar i { display: block; height: 100%; border-radius: 4px; background: #2F5D50; }
.legend { display:flex; justify-content:space-between; font-size:.84rem; padding:4px 0; color:#5F6D68; }
.dot { display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:8px; }

/* sidebar */
[data-testid="stSidebar"] { background: #fff; border-right: 1px solid #E3E8E4; }
[data-testid="stSidebar"] .brand { font-weight: 800; font-size: 1.05rem; color: #2F5D50; margin-bottom: 1.2rem; }
[data-testid="stSidebar"] label[data-baseweb="radio"] {
  width: 100%; padding: 10px 14px; border-radius: 10px; margin-bottom: 4px; color: #5F6D68; font-weight: 600; cursor: pointer;
}
[data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child { display: none; }
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) { background: #2F5D50; color: #fff; }
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) * { color: #fff; }
.stButton > button, .stDownloadButton > button {
  background: #2F5D50; color: #fff; border: 0; border-radius: 10px; font-weight: 600; padding: .45rem 1.1rem;
}
.stButton > button:hover, .stDownloadButton > button:hover { background: #244A40; color: #fff; }
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible { outline: 3px solid #A5D17A; }

/* input & label selalu terbaca, apa pun mode browser */
[data-testid="stWidgetLabel"] p { color: #1F2A27 !important; font-weight: 600; font-size: .85rem; }
[data-baseweb="input"], [data-baseweb="base-input"] { background: #fff !important; border-radius: 10px; }
[data-baseweb="input"] { border: 1px solid #D5DDD8 !important; }
[data-baseweb="input"]:focus-within { border-color: #2F5D50 !important; box-shadow: 0 0 0 3px rgba(47,93,80,.18); }
input { color: #1F2A27 !important; }

/* halaman masuk */
[data-testid="stForm"] { border: 0; padding: 0; }
[data-testid="stFormSubmitButton"] button { background: #2F5D50; color: #fff; border: 0; border-radius: 10px; font-weight: 700; padding: .6rem 1rem; }
[data-testid="stFormSubmitButton"] button:hover { background: #244A40; color: #fff; }
.login-title { font-size: 1.9rem; font-weight: 800; color: #1F2A27; margin: 0 0 .3rem; }
.login-sub { color: #6B7A75; font-size: .92rem; margin-bottom: 1.4rem; }
.demo-hint { background: #EEF5EA; border: 1px solid #D5E6C8; border-radius: 12px; padding: 10px 14px; font-size: .8rem; color: #3C5A33; margin-top: 14px; }
.hero { background: linear-gradient(160deg, #2F5D50 0%, #1B3A31 100%); border-radius: 24px; padding: 36px; color: #fff;
        min-height: 82vh; display: flex; flex-direction: column; justify-content: space-between; }
.hero h2 { font-size: 1.7rem; font-weight: 800; line-height: 1.25; margin: 0 0 .5rem; color: #fff; }
.hero p { color: #CFE3D8; font-size: .92rem; margin: 0; }
.mini { background: #fff; color: #1F2A27; border-radius: 16px; padding: 16px 18px; margin-bottom: 14px; box-shadow: 0 10px 30px rgba(0,0,0,.18); position: relative; }
.mini.b { margin-left: 44px; }
.mini .l { font-size: .78rem; color: #6B7A75; font-weight: 600; }
.mini .n { font-size: 1.5rem; font-weight: 800; }
.mini svg { position: absolute; right: 16px; bottom: 14px; width: 92px; height: 34px; }
.hero .note { font-size: .72rem; color: #A9C7B8; }
@media (max-width: 900px) { .kpi-row { grid-template-columns: 1fr; } }
</style>
"""
