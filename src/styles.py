CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root {
  --navy:#102A43; --navy-2:#173B5E; --blue:#28639A; --blue-soft:#EAF2FA;
  --teal:#168A83; --ink:#172B4D; --muted:#687B91; --line:#E5EBF2;
  --surface:#FFFFFF; --canvas:#F5F7FA;
}
html, body, .stApp, [class*="css"] {font-family:'Plus Jakarta Sans',system-ui,sans-serif;}
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"] {background:var(--canvas);color:var(--ink);}
[data-testid="stToolbar"],[data-testid="stDecoration"],footer,#MainMenu {display:none!important;}
header[data-testid="stHeader"] {height:0!important;min-height:0!important;background:transparent!important;visibility:hidden!important;}
.block-container {max-width:1480px;padding:2.15rem 2.4rem 3rem!important;}
[data-testid="stMainBlockContainer"] {padding-top:1.8rem!important;}

/* Sidebar: fixed and compact */
[data-testid="stSidebar"][aria-expanded="true"] {width:282px!important;min-width:282px!important;max-width:282px!important;}
[data-testid="stSidebar"] > div:first-child {width:282px!important;background:linear-gradient(160deg,#102A43 0%,#173B5E 100%)!important;}
[data-testid="stSidebarContent"] {padding:1.55rem 1.05rem 1.2rem!important;background:transparent!important;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {color:#D8E5F2;}
.logo {display:flex;align-items:center;gap:11px;font-weight:800;font-size:15px;line-height:1.25;color:#fff;padding:4px 5px 25px;letter-spacing:-.25px;}
.logo i {width:40px;height:40px;border-radius:12px;background:#fff;color:var(--navy);display:grid;place-items:center;font-style:normal;font-size:21px;box-shadow:0 5px 16px rgba(0,0,0,.13);}
.sbcard {border:1px solid rgba(255,255,255,.14);border-radius:14px;padding:13px;background:rgba(255,255,255,.065);color:#fff;font-size:12px;font-weight:700;}
.sbcard small {display:block;color:#B9CDE0;font-weight:500;margin-top:4px;}
.seg {display:flex;gap:4px;margin:12px 0 1px;}.seg i {flex:1;height:6px;border-radius:5px;background:#54C2B3;}.seg i.o {background:rgba(255,255,255,.18);}
.me {display:flex;align-items:center;gap:10px;padding:15px 5px 7px;color:#fff;font-size:12px;font-weight:700;}
.me small {display:block;color:#B9CDE0;font-weight:500;font-size:10px;margin-top:3px;}
.av {width:35px;height:35px;border-radius:11px;background:#D8EAFB;color:#163D65;font-weight:800;display:grid;place-items:center;flex:none;}
[class*="st-key-nav-"] button,.st-key-logout button {justify-content:flex-start;background:transparent!important;color:#D8E5F2!important;border:1px solid transparent!important;padding:.63rem .78rem;border-radius:10px;font-size:13px;font-weight:600;min-height:42px;}
[class*="st-key-nav-"] button:hover,.st-key-logout button:hover {background:rgba(255,255,255,.09)!important;color:#fff!important;}
[class*="st-key-nav-on-"] button,[class*="st-key-nav-on-"] button:hover {background:rgba(255,255,255,.15)!important;border-color:rgba(255,255,255,.12)!important;color:#fff!important;}
.st-key-logout button {margin-top:4px;}

/* Shared controls */
.stButton>button,.stDownloadButton>button {background:var(--blue);color:#fff;border:0;border-radius:10px;font-weight:650;padding:.58rem 1rem;box-shadow:none;}
.stButton>button:hover,.stDownloadButton>button:hover {background:#1D4F7D;color:#fff;}
.stButton>button *, .stDownloadButton>button * {color:inherit!important;}
[data-testid="stWidgetLabel"] p {color:var(--ink)!important;font-weight:650;font-size:12px;}
[data-baseweb="input"],[data-baseweb="base-input"] {background:#fff!important;border-radius:10px;}
[data-baseweb="input"] {border:1px solid #D9E2EC!important;}
[data-baseweb="input"]:focus-within {border-color:var(--blue)!important;box-shadow:0 0 0 3px rgba(40,99,154,.12);}
input {color:var(--ink)!important;}
[data-testid="stFileUploaderDropzone"] {background:#F9FBFE;border:1px dashed #AFC3D9;border-radius:12px;}
[data-testid="stFileUploaderDropzone"] * {color:#52647A;}
[data-testid="stForm"] {border:0;padding:0;}
[data-testid="stFormSubmitButton"] button {background:var(--blue);color:#fff;border:0;border-radius:10px;font-weight:750;padding:.72rem 1rem;min-height:46px;}
[data-testid="stFormSubmitButton"] button:hover {background:#1D4F7D;color:#fff;}

/* Page title */
.top {display:flex;align-items:center;justify-content:space-between;gap:12px;margin:0 0 19px;}
.top h1 {margin:0;font-size:27px;line-height:1.2;font-weight:800;color:var(--navy);letter-spacing:-.8px;}
.badge {background:#FFF4DF;color:#8A5A00;border:1px solid #F3DDAE;border-radius:999px;padding:6px 12px;font-size:10px;font-weight:750;}

/* Dashboard overview */
.st-key-hero {background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:19px;box-shadow:0 5px 22px rgba(16,42,67,.035);}
[class*="st-key-card-"] {background:var(--surface);border:1px solid var(--line);border-radius:15px;padding:15px 16px 11px;box-shadow:0 3px 15px rgba(16,42,67,.025);}
.hl h2 {margin:3px 0 7px;font-size:23px;font-weight:800;color:var(--navy);letter-spacing:-.7px;}
.hl p {margin:0 0 17px;color:var(--muted);font-size:12px;max-width:500px;line-height:1.7;}
.stats {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;}
.sc {background:#F8FAFD;border:1px solid #E9EEF5;border-radius:13px;padding:12px;display:flex;flex-direction:column;min-height:160px;min-width:0;}
.ic {width:34px;height:34px;border-radius:10px;display:grid;place-items:center;}
.ic svg,.dl svg {fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;}
.ic svg {width:18px;height:18px;}
.sc b {font-size:clamp(21px,2vw,28px);line-height:1.15;font-weight:800;margin-top:14px;letter-spacing:-.7px;color:var(--navy);white-space:nowrap;}
.sc .l {color:#52647A;font-size:11px;margin-top:5px;line-height:1.45;}
.dl {margin-top:auto;padding-top:11px;display:flex;align-items:center;gap:5px;font-weight:750;font-size:10px;flex-wrap:wrap;}
.dl svg {width:13px;height:13px;}.dl span {color:var(--muted);font-weight:500;}.up {color:#16805D;}.dn {color:#C2413A;}
.card-title {font-weight:750;font-size:14px;color:var(--navy);margin:0;letter-spacing:-.2px;}
.card-sub {font-size:10px;color:var(--muted);margin:4px 0 10px;line-height:1.5;}
.lg {display:flex;gap:14px;font-size:10px;color:#52647A;margin:5px 0 0;}.lg i {display:inline-block;width:8px;height:8px;border-radius:3px;margin-right:5px;background:var(--blue);}.lg i.f {background:#D6E7F8;border:1px solid #6C9BCB;}
/* Period radio buttons */
[data-testid="stRadio"] > div {gap:7px!important;flex-wrap:wrap!important;}
[data-testid="stRadio"] label {background:#F7F9FC;border:1px solid #E2E9F1;border-radius:9px;padding:5px 11px!important;min-height:32px;}
[data-testid="stRadio"] label:has(input:checked) {background:#EAF2FA;border-color:#A9C5E1;}
[data-testid="stRadio"] label p {font-size:11px!important;font-weight:650!important;color:#315A7E!important;}
[data-testid="stRadio"] [data-testid="stWidgetLabel"] {display:none;}

/* Tables */
.th {display:flex;justify-content:space-between;align-items:center;gap:10px;margin:23px 0 11px;}
.th h3 {margin:0;font-size:16px;font-weight:750;color:var(--navy);}
.pillb {border:1px solid var(--line);background:#fff;border-radius:9px;padding:6px 10px;font-size:10px;font-weight:650;color:#52647A;}
.st-key-card-hist {padding:0;overflow-x:auto;}
.tbl {width:100%;border-collapse:collapse;font-size:11px;color:var(--ink);}
.tbl th {text-align:right;font-weight:750;color:#52647A;font-size:9px;text-transform:uppercase;letter-spacing:.4px;padding:12px 14px;background:#F5F8FC;white-space:nowrap;}
.tbl td {text-align:right;padding:12px 14px;border-bottom:1px solid #EDF1F6;white-space:nowrap;}
.tbl th:first-child,.tbl td:first-child {text-align:left;}.tbl.left th,.tbl.left td {text-align:left;}.tbl tr:last-child td {border-bottom:0;}.tbl tr.best td {background:#EFF8F5;font-weight:700;}
.fn {display:flex;align-items:center;gap:9px;font-weight:650;}.fn i {width:28px;height:28px;border-radius:8px;background:#EAF2FB;color:var(--blue);display:grid;place-items:center;}.fn svg {width:14px;height:14px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;}
.chip {display:inline-flex;align-items:center;gap:6px;padding:4px 8px;border-radius:999px;font-size:9px;font-weight:700;}.chip::before {content:"";width:6px;height:6px;border-radius:50%;background:currentColor;}.ok {background:#E6F5EE;color:#16734B;}.wt {background:#FFF3D8;color:#8A5A00;}.rj {background:#FDEBEA;color:#B33B35;}.note {font-size:10px;color:var(--muted);margin-top:9px;line-height:1.55;}

/* Login page */
.login-page-label {font-size:10px;letter-spacing:1.8px;font-weight:800;color:#8293A7;margin:0 0 16px 3px;}
.st-key-login-panel {background:#fff;border:1px solid var(--line);border-radius:20px;padding:clamp(22px,3vw,42px);box-shadow:0 10px 35px rgba(16,42,67,.055);min-height:610px;display:flex;flex-direction:column;justify-content:center;}
.login-welcome {margin-bottom:23px;}.login-eyebrow {font-size:9px;letter-spacing:1.5px;color:var(--blue);font-weight:800;}
.login-welcome h1 {font-size:clamp(27px,3vw,37px);line-height:1.17;letter-spacing:-1.3px;color:var(--navy);font-weight:800;margin:12px 0 10px;}
.login-welcome p {font-size:12px;line-height:1.7;color:var(--muted);max-width:350px;margin:0;}
.demo-hint {display:flex;flex-direction:column;gap:5px;background:#F3F7FB;border:1px solid #E2EAF2;border-radius:11px;padding:12px 14px;font-size:10px;color:#42617E;margin-top:15px;}
.demo-hint b {font-size:11px;color:var(--navy);margin-bottom:2px;}.demo-hint code {background:#E5EDF5;padding:2px 5px;border-radius:4px;color:#244D73;}
.login-security {font-size:9px;color:#91A0B1;margin-top:22px;padding-top:14px;border-top:1px solid #EEF1F5;}
.login-visual {position:relative;overflow:hidden;min-height:610px;height:100%;border-radius:20px;padding:30px 32px 23px;color:#fff;background:radial-gradient(circle at 82% 16%,rgba(87,151,202,.25),transparent 31%),linear-gradient(145deg,#102A43 0%,#173B5E 62%,#1B4B70 100%);display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 12px 34px rgba(16,42,67,.13);}
.login-visual:after {content:"";position:absolute;width:330px;height:330px;border:1px solid rgba(255,255,255,.09);border-radius:50%;right:-170px;top:-150px;box-shadow:0 0 0 35px rgba(255,255,255,.025),0 0 0 70px rgba(255,255,255,.018);pointer-events:none;}
.login-brand {display:flex;align-items:center;gap:11px;position:relative;z-index:1;}.brand-mark {width:38px;height:38px;border-radius:12px;background:#fff;color:var(--navy);display:grid;place-items:center;font-size:22px;}.login-brand b {display:block;font-size:13px;}.login-brand small {display:block;color:#AFC5D9;font-size:8px;letter-spacing:1.4px;margin-top:3px;}
.visual-content {position:relative;z-index:1;margin:36px 0 28px;}.visual-kicker {font-size:9px;letter-spacing:1.8px;font-weight:800;color:#9CC4E5;display:flex;align-items:center;gap:8px;}.visual-kicker span {width:7px;height:7px;border-radius:50%;background:#61C6B4;box-shadow:0 0 0 4px rgba(97,198,180,.13);}
.login-visual h2 {font-size:clamp(27px,3vw,39px);line-height:1.16;letter-spacing:-1.2px;color:#fff;font-weight:800;margin:17px 0 12px;}.login-visual h2 em {font-style:normal;color:#A8D7D1;}.login-visual p {font-size:11px;line-height:1.75;color:#C3D5E5;max-width:390px;margin:0 0 22px;}
.visual-preview {max-width:430px;border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.08);backdrop-filter:blur(8px);border-radius:13px;padding:14px 16px 12px;}.preview-head {display:flex;justify-content:space-between;gap:8px;color:#D9E7F2;font-size:9px;}.preview-live {font-size:8px;color:#A9D8CD;letter-spacing:1px;}.preview-number {font-size:14px;font-weight:750;margin-top:12px;color:#fff;}.preview-number small {font-size:9px;color:#B8CBDC;font-weight:500;margin-left:6px;}.preview-bars {height:76px;display:flex;align-items:end;gap:8px;border-bottom:1px solid rgba(255,255,255,.17);padding:0 3px; margin-top:8px;}.preview-bars i {display:block;flex:1;border-radius:5px 5px 0 0;background:linear-gradient(180deg,#8CCBC0,#4B9B9A);opacity:.9;}.preview-years {display:flex;justify-content:space-between;color:#AFC5D9;font-size:8px;padding-top:7px;}.visual-foot {display:flex;justify-content:space-between;gap:10px;color:#9DB5CA;font-size:8px;letter-spacing:1px;position:relative;z-index:1;}

/* Responsive */
@media (max-width:1200px) {.block-container{padding:1.5rem 1.5rem 2.5rem!important;}.stats{grid-template-columns:1fr;}.sc{min-height:130px;}}
@media (max-width:900px) {.st-key-login-panel,.login-visual{min-height:520px;}.login-visual{padding:25px;}}
@media (max-width:700px) {.block-container{padding:.9rem .8rem 1.5rem!important;}.top h1{font-size:23px;}.st-key-hero{padding:12px;}.hl h2{font-size:21px;}.stats{grid-template-columns:repeat(2,minmax(0,1fr));}.sc{min-height:145px;padding:10px;}.login-visual{min-height:490px;margin-top:14px;padding:23px;}.st-key-login-panel{min-height:0;padding:22px;}}
</style>
"""
