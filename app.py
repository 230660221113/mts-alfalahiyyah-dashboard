import html
import io
import os
import urllib.parse

import pandas as pd
import streamlit as st

import charts
import ui
from data_store import (
    get_alumni_summary, get_log_unggah, get_rekap_siswa_aktif, get_settings, get_supabase,
    init_demo_state, is_supabase_configured, save_setting, upsert_alumni_3nf, upsert_siswa_aktif_3nf,
)
from forecasting import run_auto_forecast
from validation import validate_alumni_df, validate_siswa_aktif_df

MIN_TAHUN = 6
esc = html.escape
st.set_page_config(page_title="Dashboard Kesiswaan — MTs Al-Falahiyyah", page_icon="🎓", layout="wide")
st.markdown(ui.CSS, unsafe_allow_html=True)


def template_bytes(name: str) -> bytes:
    with open(os.path.join(os.path.dirname(__file__), "templates", name), "rb") as f:
        return f.read()


@st.cache_data(show_spinner=False)
def forecast(df_json: str, h: int, kap: int, rasio: int) -> dict:
    return run_auto_forecast(pd.read_json(io.StringIO(df_json)), h, kap, rasio)


# ============================== LOGIN ==============================
HERO = f"""<div class='hero'>
  <div style='font-weight:800'>🎓 MTs Al-Falahiyyah</div>
  <div>
    <div class='mini'><div class='l'>Peserta didik</div><div class='n'>Tren per tahun ajaran</div>{charts.sparkline([3, 4, 4, 6, 7, 9, 8, 11], "#1F7A5C")}</div>
    <div class='mini b'><div class='l'>Prediksi</div><div class='n'>Tahun ajaran berikutnya</div>{charts.sparkline([3, 4, 5, 5, 7, 8, 10, 12], "#7FB84E")}</div>
  </div>
  <div><h2>Pantau dan prediksi jumlah peserta didik dalam satu dashboard</h2>
  <p>Rencanakan kelas dan guru untuk tahun ajaran berikutnya.</p></div></div>"""


def do_login(email: str, password: str):
    email = email.strip().lower()
    if not email or not password:
        st.error("Isi email dan kata sandi.")
        return
    sb = get_supabase()
    if not sb:  # mode demo (tanpa Supabase)
        init_demo_state()
        u = st.session_state["demo_users"].get(email)
        if u and u["password"] == password and u.get("aktif", True):
            st.session_state["user"] = {"id": "demo-user", "email": email, "nama": u["nama"], "jabatan": u["jabatan"], "role": u["role"]}
            st.rerun()
        st.error("Email atau kata sandi tidak sesuai.")
        return
    try:
        uid = sb.auth.sign_in_with_password({"email": email, "password": password}).user.id
    except Exception:
        st.error("Email atau kata sandi tidak sesuai.")
        return
    try:
        prof = sb.table("profiles").select("*").eq("id", uid).single().execute().data
    except Exception:
        prof = None
    if not prof or not prof.get("aktif", True):
        sb.auth.sign_out()
        st.error("Akun belum aktif atau profilnya belum diatur. Hubungi operator.")
        return
    st.session_state["user"] = {"id": uid, "email": email, "nama": prof.get("nama") or email,
                                "jabatan": prof.get("jabatan") or "Staf Madrasah", "role": prof.get("role", "kepala_sekolah")}
    st.rerun()


def render_login():
    s = get_settings()
    wa = "".join(ch for ch in s.get("wa_operator", "") if ch.isdigit())
    pesan = urllib.parse.quote(f"Assalamu'alaikum Operator {s.get('nama_madrasah', 'MTs Al-Falahiyyah')}, saya lupa kata sandi akun dashboard. Mohon bantuan reset.")
    left, right = st.columns([1, 1.1], gap="large")
    with left:
        st.markdown("<div style='height:14vh'></div><div class='login-title'>Selamat datang</div>"
                    "<div class='login-sub'>Masuk untuk melihat dashboard kesiswaan.</div>", unsafe_allow_html=True)
        with st.form("login"):
            email = st.text_input("Email", placeholder="nama@alfalahiyyah.sch.id")
            pw = st.text_input("Kata sandi", type="password", placeholder="Masukkan kata sandi")
            ok = st.form_submit_button("Masuk", use_container_width=True)
        if ok:
            do_login(email, pw)
        if wa:
            st.markdown(f"<div class='login-sub' style='margin-top:12px'>Lupa kata sandi? <a href='https://wa.me/{wa}?text={pesan}' target='_blank'>Hubungi operator via WhatsApp</a></div>", unsafe_allow_html=True)
        if not is_supabase_configured():
            st.markdown("<div class='demo-hint'><b>Mode demo</b><br>operator@alfalahiyyah.sch.id / operator123<br>kepsek@alfalahiyyah.sch.id / kepsek123</div>", unsafe_allow_html=True)
    with right:
        st.markdown(HERO, unsafe_allow_html=True)


# ============================== HALAMAN ==============================
def empty_state(is_op: bool):
    with st.container(key="card-kosong"):
        ui.card_head("Belum ada data peserta didik",
                     "Unggah Data Siswa Aktif lewat menu Unggah Data." if is_op else "Data belum tersedia. Hubungi operator madrasah.")


def page_dashboard(df, settings, is_op, nama):
    demo = not is_supabase_configured()
    ui.header("Dashboard", demo)
    if df.empty:
        return empty_state(is_op)
    kap, rasio = int(settings.get("kapasitas_rombel", 32)), int(settings.get("rasio_guru_siswa", 20))
    years, vals = list(df["tahun_ajaran"]), [int(v) for v in df["total_aktif"]]
    total, prev = vals[-1], (vals[-2] if len(vals) > 1 else vals[-1])
    diff, pct = total - prev, (total - prev) / prev * 100 if prev else 0
    can = len(df) >= MIN_TAHUN
    foot, cls = ui.delta_foot(diff, pct)
    c1 = ui.stat(ui.I_TREND, "#E3F5EA", "#1F7A5C", ui.fmt(total), f"Siswa aktif {years[-1]}", foot, cls)

    if is_op:
        n_alumni, _ = get_alumni_summary()
        log = get_log_unggah()
        if log.empty:
            upd = "Belum ada unggahan"
        else:
            t = pd.to_datetime(log.iloc[0]["created_at"], utc=True).tz_convert("Asia/Jakarta")
            upd = f"{t.day} {ui.BULAN[t.month - 1][:3]} {t.year}"
        cards = [c1, ui.stat(ui.I_CAP, "#E1EFF5", "#25708F", ui.fmt(n_alumni), "Alumni terdata", "<span>Terpisah dari siswa aktif</span>"),
                 ui.stat(ui.I_CLOCK, "#EAF6D9", "#4E8A1F", f"{len(df)} tahun", "Tahun ajaran tercatat",
                         f"<span>Pembaruan terakhir: {upd}</span>")]
        sub = "Pantau kelengkapan data dan perkembangan peserta didik."
    else:
        if can:
            f = forecast(df.to_json(), 1, kap, rasio)["forecast_df"].iloc[0]
            c2 = ui.stat(ui.I_SPARK, "#EAF6D9", "#4E8A1F", ui.fmt(f["Proyeksi_Siswa_Aktif"]), f"Prediksi {f['Tahun_Ajaran']}", f"<span>{int(f['Selisih']):+d} dari tahun ini</span>")
            c3 = ui.stat(ui.I_BUILD, "#E1EFF5", "#25708F", f"{int(f['Kebutuhan_Rombel'])} rombel", f"Kebutuhan {f['Tahun_Ajaran']}", f"<span>± {int(f['Kebutuhan_Guru'])} guru</span>")
        else:
            c2 = ui.stat(ui.I_SPARK, "#EAF6D9", "#4E8A1F", "–", "Prediksi tahun depan", f"<span>Butuh min. {MIN_TAHUN} tahun ajaran data</span>")
            c3 = ui.stat(ui.I_BUILD, "#E1EFF5", "#25708F", "–", "Kebutuhan rombel", "<span>Menunggu data</span>")
        cards = [c1, c2, c3]
        sub = "Lihat perkiraan jumlah siswa, kelas, dan guru untuk tahun ajaran berikutnya."

    with st.container(key="hero"):
        left, right = st.columns([1.55, 1], gap="medium")
        with left:
            st.markdown(f"<div class='hl'><h2>Selamat {ui.sapa()}, {esc(nama)}!</h2><p>{sub}</p></div><div class='stats'>{''.join(cards)}</div>", unsafe_allow_html=True)
        with right:
            with st.container(key="card-chart"):
                ui.card_head("Perkembangan Siswa", f"{len(df)} tahun ajaran" + (" dan proyeksi" if can else ""))
                fy = fv = None
                if can:
                    h = ui.seg("hz")
                    fd = forecast(df.to_json(), h, kap, rasio)["forecast_df"]
                    fy, fv = list(fd["Tahun_Ajaran"]), list(fd["Proyeksi_Siswa_Aktif"])
                    st.markdown("<div class='lg'><span><i></i>Aktual</span><span><i class='f'></i>Prediksi</span></div>", unsafe_allow_html=True)
                st.plotly_chart(charts.bar_chart(years, vals, fy, fv), use_container_width=True, theme=None)
    if not can:
        st.info(f"Peramalan aktif setelah minimal {MIN_TAHUN} tahun ajaran data. Saat ini baru {len(df)}.")

    if is_op:
        st.markdown("<div class='th'><h3>Riwayat Unggah Data</h3></div>", unsafe_allow_html=True)
        with st.container(key="card-hist"):
            if log.empty:
                st.markdown("<div class='note' style='padding:16px'>Belum ada unggahan.</div>", unsafe_allow_html=True)
            else:
                t = pd.to_datetime(log["created_at"], utc=True).dt.tz_convert("Asia/Jakarta")
                rows = "".join(f"<tr><td><div class='fn'><i>{ui.I_FILE}</i>{esc(str(r.nama_file))}</div></td><td>{esc(str(r.jenis_unggah))}</td>"
                               f"<td>{int(r.jumlah_baris)}</td><td>{x.day} {ui.BULAN[x.month - 1][:3]} {x.year}, {x:%H.%M}</td></tr>" for r, x in zip(log.itertuples(), t))
                st.markdown(f"<table class='tbl left'><thead><tr><th>Nama berkas</th><th>Jenis</th><th>Baris</th><th>Waktu (WIB)</th></tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='th'><h3>Rekap per Tahun Ajaran</h3></div>", unsafe_allow_html=True)
        with st.container(key="card-hist"):
            rk = pd.DataFrame({"Tahun ajaran": df["tahun_ajaran"], "Kelas VII": df["kelas_vii"].astype(int), "Kelas VIII": df["kelas_viii"].astype(int),
                               "Kelas IX": df["kelas_ix"].astype(int), "Total": df["total_aktif"].astype(int)})
            rk["Perubahan"] = rk["Total"].pct_change().mul(100)
            st.markdown(ui.table(rk.iloc[::-1], delta="Perubahan"), unsafe_allow_html=True)


def page_proyeksi(df, settings):
    ui.header("Proyeksi", not is_supabase_configured())
    if df.empty or len(df) < MIN_TAHUN:
        with st.container(key="card-kosong"):
            ui.card_head("Data belum cukup", f"Proyeksi membutuhkan minimal {MIN_TAHUN} tahun ajaran. Saat ini tercatat {len(df)}.")
        return
    kap, rasio = int(settings.get("kapasitas_rombel", 32)), int(settings.get("rasio_guru_siswa", 20))
    years, vals = list(df["tahun_ajaran"]), [int(v) for v in df["total_aktif"]]
    with st.container(key="card-fc"):
        ui.card_head("Perkiraan jumlah peserta didik", "Pilih berapa tahun ajaran ke depan")
        h = ui.seg("hz-p", 2)
        fd = forecast(df.to_json(), h, kap, rasio)["forecast_df"]
        st.plotly_chart(charts.trend_chart(years, vals, list(fd["Tahun_Ajaran"]), list(fd["Proyeksi_Siswa_Aktif"])), use_container_width=True, theme=None)
        z = fd.iloc[-1]
        st.markdown(f"<div class='note'>Tahun ajaran <b>{z['Tahun_Ajaran']}</b> diperkirakan <b>{int(z['Proyeksi_Siswa_Aktif'])} siswa</b>, "
                    f"membutuhkan sekitar <b>{int(z['Kebutuhan_Rombel'])} rombel</b> dan <b>{int(z['Kebutuhan_Guru'])} guru</b>.</div>", unsafe_allow_html=True)
    with st.container(key="card-need"):
        ui.card_head("Kebutuhan kelas dan guru", f"Kapasitas {kap} siswa per rombel, rasio {rasio} siswa per guru")
        t = fd[["Tahun_Ajaran", "Proyeksi_Siswa_Aktif", "Est_Kelas_VII", "Est_Kelas_VIII", "Est_Kelas_IX", "Kebutuhan_Rombel", "Kebutuhan_Guru"]]
        t.columns = ["Tahun ajaran", "Proyeksi siswa", "Kelas VII", "Kelas VIII", "Kelas IX", "Rombel", "Guru"]
        st.markdown(ui.table(t), unsafe_allow_html=True)


def page_laporan(df, settings):
    ui.header("Laporan", not is_supabase_configured())
    with st.container(key="card-lap"):
        ui.card_head("Unduh rekap", "Rekap per tahun ajaran dan proyeksi dalam format Excel")
        if df.empty:
            st.markdown("<div class='note'>Belum ada data.</div>", unsafe_allow_html=True)
            return
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            df[["tahun_ajaran", "kelas_vii", "kelas_viii", "kelas_ix", "total_aktif", "total_laki", "total_perempuan"]].rename(columns={
                "tahun_ajaran": "Tahun ajaran", "kelas_vii": "Kelas VII", "kelas_viii": "Kelas VIII", "kelas_ix": "Kelas IX",
                "total_aktif": "Total", "total_laki": "Laki-laki", "total_perempuan": "Perempuan"}).to_excel(w, index=False, sheet_name="Rekap")
            if len(df) >= MIN_TAHUN:
                forecast(df.to_json(), 3, int(settings.get("kapasitas_rombel", 32)), int(settings.get("rasio_guru_siswa", 20)))["forecast_df"].to_excel(w, index=False, sheet_name="Proyeksi")
        st.download_button("Unduh rekap (Excel)", buf.getvalue(), "Rekap_Kesiswaan.xlsx", icon=":material/download:")


def page_unggah(user):
    ui.header("Unggah Data", not is_supabase_configured())
    with st.container(key="card-tpl"):
        ui.card_head("1. Unduh templat", "Isi templat tanpa mengubah nama kolom. NIK dan NISN diketik sebagai teks, tanpa titik atau spasi.")
        c1, c2 = st.columns(2)
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        c1.download_button("Templat Siswa Aktif", template_bytes("Template_Data_Siswa_Aktif.xlsx"), "Template_Data_Siswa_Aktif.xlsx", mime, icon=":material/download:", use_container_width=True)
        c2.download_button("Templat Alumni", template_bytes("Template_Data_Alumni.xlsx"), "Template_Data_Alumni.xlsx", mime, icon=":material/download:", use_container_width=True)
    with st.container(key="card-up"):
        ui.card_head("2. Unggah berkas", "Data diperiksa dulu. Berkas yang salah tidak disimpan.")
        t1, t2 = st.tabs(["Siswa aktif", "Alumni"])
        for tab, key, validate, saver, label in [(t1, "aktif", validate_siswa_aktif_df, upsert_siswa_aktif_3nf, "siswa aktif"),
                                                 (t2, "alumni", validate_alumni_df, upsert_alumni_3nf, "alumni")]:
            with tab:
                up = st.file_uploader(f"Berkas Excel {label} (.xlsx)", type=["xlsx"], key=f"up_{key}")
                if up is None:
                    continue
                ok, warnings, clean = validate(pd.read_excel(up, dtype=str))
                if not ok:
                    st.error(f"{len(warnings)} masalah ditemukan. Perbaiki di Excel lalu unggah ulang.")
                    st.dataframe(pd.DataFrame({"Masalah": warnings}), hide_index=True, use_container_width=True)
                else:
                    st.success(f"{len(clean)} baris {label} lolos pemeriksaan.")
                    st.dataframe(clean.head(10), hide_index=True, use_container_width=True)
                    if st.button(f"Simpan data {label}", key=f"save_{key}"):
                        saver(clean, up.name, user.get("id"))
                        st.success("Data tersimpan.")
                        st.rerun()


def page_admin(user, settings):
    ui.header("Pengguna & Pengaturan", not is_supabase_configured())
    sb = get_supabase()
    t1, t2 = st.tabs(["Akun", "Madrasah"])
    with t1, st.container(key="card-akun"):
        ui.card_head("Akun pengguna", "Akun baru dibuat lewat dashboard Supabase (Authentication → Users → Add user).")
        if sb:
            try:
                rows = sb.table("profiles").select("nama, username, jabatan, role, aktif").execute().data or []
            except Exception:
                rows = []
                st.warning("Daftar pengguna tidak dapat dimuat.")
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
            with st.form("f_reset"):
                em = st.text_input("Kirim tautan reset kata sandi ke email")
                if st.form_submit_button("Kirim tautan reset") and em:
                    try:
                        sb.auth.reset_password_for_email(em.strip().lower())
                        st.success("Tautan reset dikirim.")
                    except Exception:
                        st.error("Gagal mengirim tautan reset.")
            with st.form("f_aktif"):
                names = [r["username"] for r in rows if r.get("username")]
                target = st.selectbox("Akun", names) if names else None
                aktif = st.checkbox("Akun aktif", value=True)
                if st.form_submit_button("Simpan status") and target:
                    if target == user["email"].split("@")[0]:
                        st.error("Anda tidak dapat menonaktifkan akun sendiri.")
                    else:
                        sb.table("profiles").update({"aktif": aktif}).eq("username", target).execute()
                        st.success("Status akun diperbarui.")
                        st.rerun()
        else:
            init_demo_state()
            st.dataframe(pd.DataFrame([{"Email": k, "Nama": v["nama"], "Peran": v["role"]} for k, v in st.session_state["demo_users"].items()]), hide_index=True)
    with t2, st.container(key="card-set"), st.form("f_set"):
        ui.card_head("Pengaturan madrasah", "Dipakai untuk menghitung kebutuhan rombel dan guru")
        nama_m = st.text_input("Nama madrasah", value=settings.get("nama_madrasah", "MTs Al-Falahiyyah"))
        wa = st.text_input("WhatsApp operator (628xxx)", value=settings.get("wa_operator", ""))
        c1, c2 = st.columns(2)
        kap = c1.number_input("Kapasitas siswa per rombel", 15, 45, int(settings.get("kapasitas_rombel", 32)))
        ras = c2.number_input("Rasio siswa per guru", 10, 40, int(settings.get("rasio_guru_siswa", 20)))
        if st.form_submit_button("Simpan pengaturan"):
            for k, v in [("nama_madrasah", nama_m.strip()), ("wa_operator", "".join(c for c in wa if c.isdigit())), ("kapasitas_rombel", kap), ("rasio_guru_siswa", ras)]:
                save_setting(k, str(v))
            st.success("Pengaturan tersimpan.")
            st.rerun()


# ============================== RANGKA ==============================
def main():
    if "user" not in st.session_state:
        return render_login()
    user = st.session_state["user"]
    is_op = user["role"] == "operator"
    settings = get_settings()
    df = get_rekap_siswa_aktif()

    pages = [("home", "Dashboard", ":material/dashboard:"), ("fc", "Proyeksi", ":material/trending_up:")]
    pages += [("up", "Unggah Data", ":material/upload:"), ("adm", "Pengguna & Pengaturan", ":material/settings:")] if is_op else [("lap", "Laporan", ":material/description:")]
    page = st.session_state.setdefault("page", "home")
    if page not in [p[0] for p in pages]:
        page = "home"

    with st.sidebar:
        st.markdown(f"<div class='logo'><i>🎓</i>{esc(settings.get('nama_madrasah', 'MTs Al-Falahiyyah'))}</div>", unsafe_allow_html=True)
        for pid, label, icon in pages:
            if st.button(label, icon=icon, key=f"nav-{'on' if page == pid else 'off'}-{pid}", use_container_width=True):
                st.session_state["page"] = pid
                st.rerun()
        st.markdown("<div style='height:max(20px, calc(100vh - 720px))'></div>", unsafe_allow_html=True)
        n = len(df)
        segs = "".join("<i></i>" if k < n else "<i class='o'></i>" for k in range(max(10, n)))
        st.markdown(f"<div class='sbcard'>Data tersimpan<small>{n} tahun ajaran</small><div class='seg' aria-hidden='true'>{segs}</div></div>"
                    f"<div class='me'><span class='av'>{esc(user['nama'][:1].upper())}</span><div>{esc(user['nama'])}<small>{esc(user['jabatan'])}</small></div></div>", unsafe_allow_html=True)
        if st.button("Keluar", icon=":material/logout:", key="logout", use_container_width=True):
            sb = get_supabase()
            if sb:
                try:
                    sb.auth.sign_out()
                except Exception:
                    pass
            st.session_state.clear()
            st.rerun()

    if page == "home":
        page_dashboard(df, settings, is_op, user["nama"])
    elif page == "fc":
        page_proyeksi(df, settings)
    elif page == "up" and is_op:
        page_unggah(user)
    elif page == "adm" and is_op:
        page_admin(user, settings)
    elif page == "lap":
        page_laporan(df, settings)


main()
