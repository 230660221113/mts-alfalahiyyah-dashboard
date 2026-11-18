import os
import urllib.parse
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_store import (
    get_alumni_summary,
    get_rekap_siswa_aktif,
    get_settings,
    get_supabase,
    init_demo_state,
    is_supabase_configured,
    save_setting,
    upsert_alumni_3nf,
    upsert_siswa_aktif_3nf,
)
from forecasting import run_auto_forecast
from validation import validate_alumni_df, validate_siswa_aktif_df

st.set_page_config(
    page_title="Sistem Analitik & Proyeksi Siswa — MTs Al-Falahiyyah",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Gaya antarmuka bersih, profesional, kontras tinggi, dan mudah dipahami
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #0F2942;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        box-shadow: 0 1px 3px rgba(15,41,66,0.06);
    }
    .kpi-label { font-size: 0.85rem; color: #475569; font-weight: 600; margin-bottom: 0.25rem; }
    .kpi-value { font-size: 1.75rem; color: #0F2942; font-weight: 700; line-height: 1.2; }
    .kpi-sub { font-size: 0.8rem; color: #64748B; margin-top: 0.25rem; }
    .wa-badge {
        display: inline-block;
        background-color: #16A34A;
        color: #FFFFFF !important;
        padding: 0.55rem 1.1rem;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.92rem;
        margin-top: 0.4rem;
    }
    .wa-badge:hover { background-color: #15803D; }
    </style>
    """,
    unsafe_allow_html=True,
)


def _get_template_bytes(filename: str) -> bytes:
    path = os.path.join(os.path.dirname(__file__), "templates", filename)
    with open(path, "rb") as f:
        return f.read()


def render_login():
    settings = get_settings()
    madrasah = settings.get("nama_madrasah", "MTs Al-Falahiyyah")
    wa_operator = "".join(ch for ch in settings.get("wa_operator", "6281234567890") if ch.isdigit())

    _, center, _ = st.columns([1.1, 1.3, 1.1])
    with center:
        st.markdown(f"## 🎓 {madrasah}")
        st.caption("Sistem Informasi Analitik & Proyeksi Jumlah Peserta Didik")

        tab_masuk, tab_lupa = st.tabs(["🔑 Masuk Sistem", "💬 Lupa Kata Sandi"])

        with tab_masuk:
            with st.form("form_login", clear_on_submit=False):
                email = st.text_input("Email Pengguna", placeholder="contoh: operator@alfalahiyyah.sch.id")
                password = st.text_input("Kata Sandi", type="password", placeholder="Masukkan kata sandi")
                submit = st.form_submit_button("Masuk ke Dashboard", use_container_width=True, type="primary")

            if submit:
                email_clean = email.strip().lower()
                if not email_clean or not password:
                    st.error("Harap isi email dan kata sandi.")
                    return

                sb = get_supabase()
                if sb:
                    try:
                        auth_res = sb.auth.sign_in_with_password({"email": email_clean, "password": password})
                        uid = auth_res.user.id
                        prof_res = sb.table("profiles").select("*").eq("id", uid).single().execute()
                        prof = prof_res.data
                        if not prof or not prof.get("aktif", True):
                            st.error("Akun tidak aktif atau profil peran belum diatur oleh Operator.")
                            return
                        st.session_state["user"] = {
                            "id": uid,
                            "email": email_clean,
                            "nama": prof.get("nama") or email_clean,
                            "jabatan": prof.get("jabatan") or "Staf Madrasah",
                            "role": prof.get("role", "kepala_sekolah"),
                        }
                        st.rerun()
                    except Exception:
                        st.error("Email atau kata sandi salah, atau akun belum dikonfirmasi oleh Operator.")
                else:
                    init_demo_state()
                    users = st.session_state["demo_users"]
                    u = users.get(email_clean)
                    if u and u["password"] == password and u.get("aktif", True):
                        st.session_state["user"] = {
                            "id": "demo-user",
                            "email": email_clean,
                            "nama": u["nama"],
                            "jabatan": u["jabatan"],
                            "role": u["role"],
                        }
                        st.rerun()
                    else:
                        st.error("Email atau kata sandi tidak sesuai.")

        with tab_lupa:
            st.info(
                "**Lupa Kata Sandi?**\n\n"
                "Demi keamanan data madrasah, pengaturan ulang (*reset*) kata sandi dilakukan langsung "
                "oleh **Operator Madrasah (Super Admin)**. Klik tombol di bawah untuk menghubungi Operator via WhatsApp:"
            )
            pesan_wa = urllib.parse.quote(
                f"Assalamu'alaikum Operator {madrasah}, saya lupa kata sandi akun Dashboard Siswa. Mohon bantuan untuk reset kata sandi saya."
            )
            wa_url = f"https://wa.me/{wa_operator}?text={pesan_wa}"
            st.markdown(
                f'<a class="wa-badge" href="{wa_url}" target="_blank">📲 Hubungi Operator via WhatsApp</a>',
                unsafe_allow_html=True,
            )


def render_dashboard_overview(df_rekap: pd.DataFrame, total_alumni: int, settings: dict):
    st.subheader("📊 Ringkasan Kondisi Peserta Didik")

    latest = df_rekap.iloc[-1]
    prev = df_rekap.iloc[-2] if len(df_rekap) > 1 else latest
    diff_aktif = int(latest["total_aktif"] - prev["total_aktif"])
    kapasitas = int(settings.get("kapasitas_rombel", 32))
    rombel_saat_ini = max(int(-(-latest["total_aktif"] // kapasitas)), 3)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Siswa Aktif ({latest["tahun_ajaran"]})</div>'
            f'<div class="kpi-value">{int(latest["total_aktif"])}</div>'
            f'<div class="kpi-sub">{diff_aktif:+d} dari tahun ajaran lalu</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Komposisi Kelas Aktif</div>'
            f'<div class="kpi-value">VII: {int(latest["kelas_vii"])} | VIII: {int(latest["kelas_viii"])} | IX: {int(latest["kelas_ix"])}</div>'
            f'<div class="kpi-sub">Tercatat aktif di EMIS</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Kebutuhan Rombel Saat Ini</div>'
            f'<div class="kpi-value">{rombel_saat_ini} Kelas</div>'
            f'<div class="kpi-sub">Kapasitas {kapasitas} siswa/rombel</div></div>',
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Total Alumni Terdata</div>'
            f'<div class="kpi-value">{total_alumni}</div>'
            f'<div class="kpi-sub">Terpisah dari hitungan siswa aktif</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("#### Tren Jumlah Siswa Aktif per Tahun Ajaran")
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Kelas VII", x=df_rekap["tahun_ajaran"], y=df_rekap["kelas_vii"], marker_color="#1D4ED8"))
    fig.add_trace(go.Bar(name="Kelas VIII", x=df_rekap["tahun_ajaran"], y=df_rekap["kelas_viii"], marker_color="#0EA5E9"))
    fig.add_trace(go.Bar(name="Kelas IX", x=df_rekap["tahun_ajaran"], y=df_rekap["kelas_ix"], marker_color="#38BDF8"))
    fig.add_trace(
        go.Scatter(
            name="Total Siswa Aktif",
            x=df_rekap["tahun_ajaran"],
            y=df_rekap["total_aktif"],
            mode="lines+markers+text",
            text=df_rekap["total_aktif"],
            textposition="top center",
            line=dict(color="#0F2942", width=3),
        )
    )
    fig.update_layout(
        barmode="stack",
        height=390,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_title="Jumlah Siswa",
        xaxis_title="Tahun Ajaran",
        plot_bgcolor="#FFFFFF",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_prediksi(df_rekap: pd.DataFrame, settings: dict):
    st.subheader("📈 Proyeksi Siswa & Kebutuhan Kelas / Guru")

    col_ctrl, _ = st.columns([1.4, 2.6])
    with col_ctrl:
        horizon = st.selectbox(
            "Pilih Rentang Proyeksi Tahun Ajaran Mendatang",
            options=[1, 2, 3],
            index=1,
            format_func=lambda x: f"{x} Tahun Ajaran Mendatang",
        )

    kapasitas = int(settings.get("kapasitas_rombel", 32))
    rasio_guru = int(settings.get("rasio_guru_siswa", 20))
    res = run_auto_forecast(df_rekap, horizon=horizon, kapasitas_rombel=kapasitas, rasio_guru=rasio_guru)
    df_fc = res["forecast_df"]

    # Grafik gabungan historis + proyeksi yang bersih & langsung terbaca
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            name="Data Historis (Siswa Aktif)",
            x=df_rekap["tahun_ajaran"],
            y=df_rekap["total_aktif"],
            mode="lines+markers+text",
            text=df_rekap["total_aktif"],
            textposition="top center",
            line=dict(color="#0F2942", width=3),
            marker=dict(size=8),
        )
    )

    bridge_x = [df_rekap["tahun_ajaran"].iloc[-1]] + df_fc["Tahun_Ajaran"].tolist()
    bridge_y = [int(df_rekap["total_aktif"].iloc[-1])] + df_fc["Proyeksi_Siswa_Aktif"].tolist()
    bridge_txt = [""] + [str(v) for v in df_fc["Proyeksi_Siswa_Aktif"].tolist()]

    fig.add_trace(
        go.Scatter(
            name="Proyeksi Mendatang",
            x=bridge_x,
            y=bridge_y,
            mode="lines+markers+text",
            text=bridge_txt,
            textposition="top center",
            line=dict(color="#D97706", width=3, dash="dash"),
            marker=dict(size=9, symbol="diamond"),
        )
    )
    fig.update_layout(
        height=380,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_title="Jumlah Siswa Aktif",
        xaxis_title="Tahun Ajaran",
        plot_bgcolor="#FFFFFF",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Estimasi Kebutuhan Ruang Kelas & Tenaga Pendidik")
    st.dataframe(
        df_fc.rename(
            columns={
                "Tahun_Ajaran": "Tahun Ajaran",
                "Proyeksi_Siswa_Aktif": "Proyeksi Siswa Aktif",
                "Est_Kelas_VII": "Est. Kelas VII",
                "Est_Kelas_VIII": "Est. Kelas VIII",
                "Est_Kelas_IX": "Est. Kelas IX",
                "Perubahan": "Selisih",
                "Kebutuhan_Rombel": "Kebutuhan Ruang Kelas (Rombel)",
                "Kebutuhan_Guru": "Estimasi Kebutuhan Guru",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def render_unggah_data(user: dict):
    st.subheader("📥 Unggah & Validasi Data EMIS (Siswa Aktif & Alumni)")

    # 1. Dua tombol unduh templat resmi sesuai Excel berjalan di madrasah
    st.markdown("#### 1. Unduh Templat Excel Resmi")
    c_t1, c_t2 = st.columns(2)
    with c_t1:
        st.download_button(
            label="⬇️ Unduh Templat Data Siswa Aktif (.xlsx)",
            data=_get_template_bytes("Template_Data_Siswa_Aktif.xlsx"),
            file_name="Template_Data_Siswa_Aktif.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with c_t2:
        st.download_button(
            label="⬇️ Unduh Templat Data Alumni (.xlsx)",
            data=_get_template_bytes("Template_Data_Alumni.xlsx"),
            file_name="Template_Data_Alumni.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    st.divider()
    st.markdown("#### 2. Unggah Berkas Excel Terisi")
    tab_aktif, tab_alumni = st.tabs(["👨‍🎓 Unggah Data Siswa Aktif", "🎓 Unggah Data Alumni (Lulusan)"])

    with tab_aktif:
        up_aktif = st.file_uploader(
            "Pilih file Excel Data Siswa Aktif (.xlsx)", type=["xlsx"], key="up_siswa_aktif"
        )
        if up_aktif is not None:
            df_raw = pd.read_excel(up_aktif, dtype=str)
            is_valid, warnings, df_clean = validate_siswa_aktif_df(df_raw)
            if not is_valid:
                st.error(f"Ditemukan {len(warnings)} ketidaksesuaian format data. Perbaiki baris berikut sebelum menyimpan:")
                for w in warnings[:25]:
                    st.warning(w)
            else:
                st.success(f"Validasi berhasil: {len(df_clean)} data siswa aktif siap disimpan (NIK & NISN bersih).")
                st.dataframe(df_clean.head(15), use_container_width=True, hide_index=True)
                if st.button("💾 Simpan Data Siswa Aktif ke Database", type="primary", key="btn_save_aktif"):
                    upsert_siswa_aktif_3nf(df_clean, up_aktif.name, user.get("id"))
                    st.success("Data siswa aktif berhasil tersimpan dan grafik proyeksi telah diperbarui.")
                    st.rerun()

    with tab_alumni:
        up_alumni = st.file_uploader(
            "Pilih file Excel Data Alumni (.xlsx)", type=["xlsx"], key="up_alumni"
        )
        if up_alumni is not None:
            df_raw_al = pd.read_excel(up_alumni, dtype=str)
            is_valid_al, warnings_al, df_clean_al = validate_alumni_df(df_raw_al)
            if not is_valid_al:
                st.error(f"Ditemukan {len(warnings_al)} ketidaksesuaian pada data Alumni:")
                for w in warnings_al[:25]:
                    st.warning(w)
            else:
                st.success(
                    f"Validasi berhasil: {len(df_clean_al)} data alumni valid. "
                    "Siswa pada daftar ini akan otomatis dipisahkan dari hitungan siswa aktif."
                )
                st.dataframe(df_clean_al.head(15), use_container_width=True, hide_index=True)
                if st.button("💾 Simpan Data Alumni ke Database", type="primary", key="btn_save_alumni"):
                    upsert_alumni_3nf(df_clean_al, up_alumni.name, user.get("id"))
                    st.success("Data alumni berhasil tersimpan dan status siswa diperbarui.")
                    st.rerun()


def render_manajemen_akun(user: dict, settings: dict):
    st.subheader("⚙️ Manajemen Pengguna & Pengaturan Madrasah")
    sb = get_supabase()

    tab_pengguna, tab_madrasah = st.tabs(["👥 Kelola Akun Kepala Sekolah & Reset Sandi", "🏫 Pengaturan Madrasah & Kontak WA"])

    with tab_pengguna:
        st.markdown("#### Daftar Pengguna Sistem")
        if sb:
            try:
                res = sb.table("profiles").select("id, username, nama, jabatan, role, aktif").execute()
                df_prof = pd.DataFrame(res.data or [])
                if not df_prof.empty:
                    st.dataframe(
                        df_prof[["nama", "username", "jabatan", "role", "aktif"]],
                        use_container_width=True,
                        hide_index=True,
                    )
            except Exception as e:
                st.warning(f"Gagal memuat daftar pengguna: {e}")

            st.markdown("#### Tambah Akun Kepala Sekolah Baru")
            with st.form("form_add_kepsek"):
                c1, c2 = st.columns(2)
                nama_baru = c1.text_input("Nama Lengkap", placeholder="Drs. H. Ahmad Fauzi, M.Pd.")
                jabatan_baru = c2.text_input("Jabatan", value="Kepala Madrasah")
                email_baru = c1.text_input("Email Login", placeholder="kepsek@alfalahiyyah.sch.id")
                pw_baru = c2.text_input("Kata Sandi Awal", type="password", placeholder="Minimal 6 karakter")
                submitted = st.form_submit_button("➕ Buat Akun Kepala Sekolah", type="primary")
                if submitted:
                    if len(pw_baru) < 6 or not email_baru:
                        st.error("Email wajib diisi dan kata sandi minimal 6 karakter.")
                    else:
                        try:
                            sb.auth.sign_up({
                                "email": email_baru.strip().lower(),
                                "password": pw_baru,
                                "options": {
                                    "data": {
                                        "nama": nama_baru or "Kepala Madrasah",
                                        "jabatan": jabatan_baru,
                                        "role": "kepala_sekolah",
                                    }
                                },
                            })
                            st.success(f"Akun {email_baru} berhasil ditambahkan dengan peran Kepala Sekolah.")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Gagal menambahkan akun: {ex}")

            st.markdown("#### Kirim Tautan Reset Kata Sandi Pengguna")
            with st.form("form_reset_pw"):
                target_email = st.text_input("Email Pengguna yang Lupa Kata Sandi", placeholder="kepsek@alfalahiyyah.sch.id")
                if st.form_submit_button("🔄 Kirim Reset Kata Sandi"):
                    if target_email:
                        try:
                            sb.auth.reset_password_for_email(target_email.strip().lower())
                            st.success(f"Instruksi pengaturan ulang kata sandi telah dikirim ke {target_email}.")
                        except Exception as ex:
                            st.error(f"Gagal mengirim reset kata sandi: {ex}")
        else:
            init_demo_state()
            users = st.session_state["demo_users"]
            st.table([{"Email": k, "Nama": v["nama"], "Peran": v["role"]} for k, v in users.items()])
            with st.form("demo_reset_form"):
                em = st.selectbox("Pilih Akun untuk Reset Kata Sandi", list(users.keys()))
                new_p = st.text_input("Kata Sandi Baru", type="password")
                if st.form_submit_button("Simpan Kata Sandi Baru", type="primary"):
                    if len(new_p) >= 6:
                        st.session_state["demo_users"][em]["password"] = new_p
                        st.success(f"Kata sandi untuk {em} berhasil diperbarui.")
                    else:
                        st.error("Kata sandi minimal 6 karakter.")

    with tab_madrasah:
        with st.form("form_settings"):
            nama_m = st.text_input("Nama Madrasah", value=settings.get("nama_madrasah", "MTs Al-Falahiyyah"))
            wa_op = st.text_input(
                "Nomor WhatsApp Operator (Format 628xxx untuk tombol Lupa Kata Sandi)",
                value=settings.get("wa_operator", "6281234567890"),
            )
            c1, c2 = st.columns(2)
            kap_r = c1.number_input("Kapasitas Maksimal Siswa per Rombel", min_value=15, max_value=45, value=int(settings.get("kapasitas_rombel", 32)))
            ras_g = c2.number_input("Rasio Ideal Siswa per Guru", min_value=10, max_value=40, value=int(settings.get("rasio_guru_siswa", 20)))
            if st.form_submit_button("💾 Simpan Pengaturan", type="primary"):
                save_setting("nama_madrasah", nama_m.strip())
                save_setting("wa_operator", "".join(ch for ch in wa_op if ch.isdigit()))
                save_setting("kapasitas_rombel", str(kap_r))
                save_setting("rasio_guru_siswa", str(ras_g))
                st.success("Pengaturan madrasah berhasil disimpan.")
                st.rerun()


def main():
    if "user" not in st.session_state:
        render_login()
        return

    user = st.session_state["user"]
    settings = get_settings()
    madrasah = settings.get("nama_madrasah", "MTs Al-Falahiyyah")
    is_operator = user.get("role") == "operator"

    with st.sidebar:
        st.markdown(f"### 🎓 {madrasah}")
        st.caption(f"**{user['nama']}**\n{user['jabatan']}")
        st.divider()

        menu_options = ["📊 Ringkasan Dashboard", "📈 Proyeksi Siswa & Kelas"]
        if is_operator:
            menu_options.extend(["📥 Unggah Data (Aktif & Alumni)", "⚙️ Pengguna & Pengaturan"])

        selected = st.radio("Menu Navigasi", menu_options, label_visibility="collapsed")
        st.divider()
        if st.button("🚪 Keluar", use_container_width=True):
            sb = get_supabase()
            if sb:
                try:
                    sb.auth.sign_out()
                except Exception:
                    pass
            del st.session_state["user"]
            st.rerun()

    df_rekap = get_rekap_siswa_aktif()
    total_alumni, _ = get_alumni_summary()

    if selected == "📊 Ringkasan Dashboard":
        render_dashboard_overview(df_rekap, total_alumni, settings)
    elif selected == "📈 Proyeksi Siswa & Kelas":
        render_prediksi(df_rekap, settings)
    elif selected == "📥 Unggah Data (Aktif & Alumni)" and is_operator:
        render_unggah_data(user)
    elif selected == "⚙️ Pengguna & Pengaturan" and is_operator:
        render_manajemen_akun(user, settings)


if __name__ == "__main__":
    main()
