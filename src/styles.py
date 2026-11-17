CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root {
  --navy: #102A43;
  --blue: #1D4E89;
  --blue-soft: #EAF2FB;
  --teal: #168A83;
  --ink: #172B4D;
  --muted: #64748B;
  --line: #E4EAF2;
  --surface: #FFFFFF;
  --canvas: #F4F7FB;
}
html, body, .stApp, [class*="css"] { font-family: 'Plus Jakarta Sans', system-ui, sans-serif; }
.stApp, [data-testid="stAppViewContainer"] { background: var(--canvas); color: var(--ink); }
[data-testid="stMain"] { background: var(--canvas); }
[data-testid="stToolbar"], [data-testid="stDecoration"], footer, #MainMenu { display: none !important; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding: 1.8rem 2rem 2.5rem; max-width: 1500px; }

/* Sidebar */
[data-testid="stSidebar"] { background: linear-gradient(165deg, #102A43 0%, #163D65 100%); border-right: 0; min-width: 260px; }
[data-testid="stSidebar"] > div, [data-testid="stSidebarContent"] { background: transparent !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #D8E5F2; }
.logo { display:flex; align-items:center; gap:12px; font-weight:800; font-size:16px; line-height:1.25; color:#fff; padding:8px 8px 28px; letter-spacing:-.2px; }
.logo i { width:42px; height:42px; border-radius:13px; background:#fff; color:var(--navy); display:grid; place-items:center; font-style:normal; font-size:22px; box-shadow:0 5px 16px rgba(0,0,0,.14); }
.sbcard { border:1px solid rgba(255,255,255,.15); border-radius:15px; padding:14px; background:rgba(255,255,255,.07); color:#fff; font-size:13px; font-weight:700; }
.sbcard small { display:block; color:#B9CDE0; font-weight:500; margin-top:4px; }
.seg { display:flex; gap:4px; margin:13px 0 1px; }
.seg i { flex:1; height:7px; border-radius:5px; background:#54C2B3; }
.seg i.o { background:rgba(255,255,255,.18); }
.me { display:flex; align-items:center; gap:11px; padding:17px 7px 7px; color:#fff; font-size:13px; font-weight:700; }
.me small { display:block; color:#B9CDE0; font-weight:500; font-size:11px; margin-top:3px; }
.av { width:38px; height:38px; border-radius:12px; background:#D8EAFB; color:#163D65; font-weight:800; display:grid; place-items:center; flex:none; }

/* Navigation and controls */
[class*="st-key-nav-"] button, .st-key-logout button { justify-content:flex-start; background:transparent !important; color:#D8E5F2 !important; border:1px solid transparent !important; padding:.72rem .9rem; border-radius:11px; font-size:14px; font-weight:600; }
[class*="st-key-nav-"] button:hover, .st-key-logout button:hover { background:rgba(255,255,255,.09) !important; color:#fff !important; }
[class*="st-key-nav-on-"] button, [class*="st-key-nav-on-"] button:hover { background:rgba(255,255,255,.16) !important; border-color:rgba(255,255,255,.12) !important; color:#fff !important; }
.stButton > button, .stDownloadButton > button { background:var(--blue); color:#fff; border:0; border-radius:10px; font-weight:650; padding:.55rem 1rem; box-shadow:none; }
.stButton > button:hover, .stDownloadButton > button:hover { background:#163D65; color:#fff; }
.stButton > button *, .stDownloadButton > button * { color:inherit !important; }
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible { outline:3px solid #9CC4ED; }
[class*="st-key-seg-"] button { background:#fff; color:#52647A; border:1px solid var(--line); border-radius:9px; padding:.25rem .65rem; min-height:0; font-size:.8rem; }
[class*="st-key-seg-"] button:hover { background:var(--blue-soft); color:var(--navy); }
[class*="st-key-seg-on-"] button, [class*="st-key-seg-on-"] button:hover { background:var(--blue); color:#fff; border-color:var(--blue); }

/* Page heading */
.top { display:flex; align-items:center; justify-content:space-between; gap:12px; margin:0 0 20px; }
.top h1 { margin:0; font-size:28px; line-height:1.2; font-weight:800; color:var(--navy); letter-spacing:-.7px; }
.badge { background:#FFF3D8; color:#8A5A00; border:1px solid #F4DDA8; border-radius:999px; padding:6px 12px; font-size:11px; font-weight:750; }

/* Main dashboard hero and KPI cards */
.st-key-hero { background:var(--surface); border:1px solid var(--line); border-radius:20px; padding:20px; box-shadow:0 5px 22px rgba(16,42,67,.045); }
[class*="st-key-card-"] { background:var(--surface); border:1px solid var(--line); border-radius:17px; padding:16px 18px 12px; box-shadow:0 4px 18px rgba(16,42,67,.035); }
.hl h2 { margin:4px 0 6px; font-size:25px; font-weight:800; color:var(--navy); letter-spacing:-.6px; }
.hl p { margin:0 0 20px; color:var(--muted); font-size:13px; max-width:470px; line-height:1.65; }
.stats { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:11px; }
.sc { background:#F8FAFD; border:1px solid #E9EEF5; border-radius:14px; padding:14px; display:flex; flex-direction:column; min-height:175px; }
.ic { width:37px; height:37px; border-radius:11px; display:grid; place-items:center; }
.ic svg, .dl svg { fill:none; stroke:currentColor; stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round; }
.ic svg { width:19px; height:19px; }
.sc b { font-size:29px; line-height:1.15; font-weight:800; margin-top:15px; letter-spacing:-.7px; color:var(--navy); }
.sc .l { color:#52647A; font-size:12px; margin-top:5px; line-height:1.4; }
.dl { margin-top:auto; padding-top:12px; display:flex; align-items:center; gap:5px; font-weight:750; font-size:11px; }
.dl svg { width:14px; height:14px; }
.dl span { color:var(--muted); font-weight:500; }
.up { color:#16805D; } .dn { color:#C2413A; }
.card-title { font-weight:750; font-size:15px; color:var(--navy); margin:0; letter-spacing:-.2px; }
.card-sub { font-size:11px; color:var(--muted); margin:4px 0 12px; line-height:1.5; }
.lg { display:flex; gap:15px; font-size:11px; color:#52647A; margin:5px 0 0; }
.lg i { display:inline-block; width:9px; height:9px; border-radius:3px; margin-right:6px; background:var(--blue); }
.lg i.f { background:#D6E7F8; border:1px solid #6C9BCB; }

/* History tables and status */
.th { display:flex; justify-content:space-between; align-items:center; gap:10px; margin:24px 0 12px; }
.th h3 { margin:0; font-size:17px; font-weight:750; color:var(--navy); }
.pillb { border:1px solid var(--line); background:#fff; border-radius:9px; padding:7px 11px; font-size:11px; font-weight:650; color:#52647A; }
.st-key-card-hist { padding:0; overflow-x:auto; }
.tbl { width:100%; border-collapse:collapse; font-size:12px; color:var(--ink); }
.tbl th { text-align:right; font-weight:750; color:#52647A; font-size:10px; text-transform:uppercase; letter-spacing:.45px; padding:13px 16px; background:#F5F8FC; white-space:nowrap; }
.tbl td { text-align:right; padding:13px 16px; border-bottom:1px solid #EDF1F6; white-space:nowrap; }
.tbl th:first-child, .tbl td:first-child { text-align:left; }
.tbl.left th, .tbl.left td { text-align:left; }
.tbl tr:last-child td { border-bottom:0; }
.tbl tr.best td { background:#EFF8F5; font-weight:700; }
.fn { display:flex; align-items:center; gap:10px; font-weight:650; }
.fn i { width:30px; height:30px; border-radius:9px; background:#EAF2FB; color:var(--blue); display:grid; place-items:center; }
.fn svg { width:15px; height:15px; fill:none; stroke:currentColor; stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round; }
.chip { display:inline-flex; align-items:center; gap:6px; padding:4px 9px; border-radius:999px; font-size:10px; font-weight:700; }
.chip::before { content:""; width:6px; height:6px; border-radius:50%; background:currentColor; }
.ok { background:#E6F5EE; color:#16734B; } .wt { background:#FFF3D8; color:#8A5A00; } .rj { background:#FDEBEA; color:#B33B35; }
.note { font-size:11px; color:var(--muted); margin-top:10px; line-height:1.55; }

/* Inputs, uploader and login */
[data-testid="stWidgetLabel"] p { color:var(--ink) !important; font-weight:650; font-size:12px; }
[data-baseweb="input"], [data-baseweb="base-input"] { background:#fff !important; border-radius:10px; }
[data-baseweb="input"] { border:1px solid #D9E2EC !important; }
[data-baseweb="input"]:focus-within { border-color:var(--blue) !important; box-shadow:0 0 0 3px rgba(29,78,137,.13); }
input { color:var(--ink) !important; }
[data-testid="stFileUploaderDropzone"] { background:#F9FBFE; border:1px dashed #AFC3D9; border-radius:12px; }
[data-testid="stFileUploaderDropzone"] * { color:#52647A; }
[data-testid="stForm"] { border:0; padding:0; }
[data-testid="stFormSubmitButton"] button { background:var(--blue); color:#fff; border:0; border-radius:10px; font-weight:750; padding:.65rem 1rem; }
[data-testid="stFormSubmitButton"] button:hover { background:#163D65; color:#fff; }
.login-title { font-size:1.9rem; font-weight:800; color:var(--navy); margin:0 0 .3rem; }
.login-sub { color:var(--muted); font-size:.9rem; margin-bottom:1.4rem; }
.demo-hint { background:#EDF5FC; border:1px solid #D4E4F3; border-radius:12px; padding:11px 14px; font-size:.78rem; color:#294E70; margin-top:14px; }
.hero { background:radial-gradient(120% 55% at 0% 100%, rgba(73,143,201,.35), transparent 62%), #102A43; border-radius:22px; padding:34px; color:#fff; min-height:82vh; display:flex; flex-direction:column; justify-content:space-between; }
.hero h2 { font-size:1.7rem; font-weight:800; line-height:1.25; margin:0 0 .5rem; color:#fff; }
.hero p { color:#D5E4F2; font-size:.9rem; margin:0; }
.mini { background:#fff; color:var(--navy); border-radius:15px; padding:15px 17px; margin-bottom:13px; box-shadow:0 10px 28px rgba(0,0,0,.16); position:relative; }
.mini.b { margin-left:40px; }
.mini .l { font-size:.75rem; color:var(--muted); font-weight:600; }
.mini .n { font-size:1.25rem; font-weight:800; }
.mini svg { position:absolute; right:15px; bottom:13px; width:88px; height:32px; }
.hero .note { font-size:.7rem; color:#B7CDE0; }
@media (max-width: 1100px) { .stats { grid-template-columns:1fr; } .sc { min-height:145px; } }
@media (max-width: 700px) { .block-container { padding:.9rem .8rem 1.5rem; } .top h1 { font-size:23px; } .st-key-hero { padding:13px; } .hl h2 { font-size:21px; } }
</style>
"""
