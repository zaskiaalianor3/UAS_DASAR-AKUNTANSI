import streamlit as st
import pandas as pd
from io import BytesIO
import uuid

# ================== KONFIGURASI ==================
st.set_page_config(page_title="Aplikasi Akuntansi", layout="wide")

# ================== SESSION ==================
if "data" not in st.session_state:
    st.session_state.data = []

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

# ================== LIST JENIS AKUN ==================
JENIS_AKUN = ["Aset", "Kewajiban", "Modal", "Pendapatan", "Beban"]

# ================== SIDEBAR ==================
menu = st.sidebar.selectbox(
    "📂 Menu",
    [
        "🏠 Home",
        "📘 Jurnal Umum",
        "📑 Lihat Semua",
        "💾 Simpan ke Excel"
    ]
)

# ================== HOME ==================
if menu == "🏠 Home":
    st.markdown(
        """
        <div style="
            display:flex;
            justify-content:center;
            align-items:center;
            height:80vh;
            flex-direction:column;
            text-align:center;
        ">
            <div style="display:flex; gap:40px; align-items:center;">
                <img src="assets/logo_kampus.png" width="120">
                <img src="assets/logo_siumk.png" width="120">
            </div>

            <h1 style="margin-top:30px; font-weight:700;">
                SISTEM INFORMASI AKUNTANSI
            </h1>

            <h3 style="margin-top:10px; color:gray;">
                Aplikasi Akuntansi Sederhana Berbasis Streamlit
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )


# ================== JURNAL UMUM ==================
elif menu == "📘 Jurnal Umum":
    st.title("📘 Jurnal Umum")

    with st.form("form_jurnal"):
        tanggal = st.date_input("Tanggal")

        col1, col2 = st.columns(2)
        with col1:
            akun_debit = st.text_input("Akun Debit")
            jenis_debit = st.selectbox("Jenis Akun Debit", JENIS_AKUN)
        with col2:
            akun_kredit = st.text_input("Akun Kredit")
            jenis_kredit = st.selectbox("Jenis Akun Kredit", JENIS_AKUN)

        jumlah = st.number_input("Jumlah", min_value=0.0)
        simpan = st.form_submit_button("Simpan Transaksi")

        if simpan:
            if akun_debit == "" or akun_kredit == "":
                st.error("Nama akun tidak boleh kosong")
            elif jumlah <= 0:
                st.error("Jumlah harus lebih dari 0")
            else:
                trx_id = str(uuid.uuid4())

                st.session_state.data.append({
                    "ID": trx_id,
                    "Tanggal": tanggal,
                    "Akun": akun_debit,
                    "Jenis Akun": jenis_debit,
                    "Debit": jumlah,
                    "Kredit": 0
                })
                st.session_state.data.append({
                    "ID": trx_id,
                    "Tanggal": tanggal,
                    "Akun": akun_kredit,
                    "Jenis Akun": jenis_kredit,
                    "Debit": 0,
                    "Kredit": jumlah
                })

                st.success("Transaksi berhasil disimpan (SEIMBANG)")

    df = pd.DataFrame(st.session_state.data)

    st.subheader("📋 Data Jurnal")
    if not df.empty:
        st.dataframe(df, use_container_width=True)

        st.subheader("✏️ Kelola Transaksi")
        pilih_id = st.selectbox("Pilih ID Transaksi", df["ID"].unique())

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Hapus"):
                st.session_state.data = [
                    d for d in st.session_state.data if d["ID"] != pilih_id
                ]
                st.success("Transaksi dihapus")
                st.experimental_rerun()

        with col2:
            if st.button("Edit"):
                st.session_state.edit_id = pilih_id
                st.experimental_rerun()
    else:
        st.info("Belum ada transaksi")

# ================== EDIT ==================
if st.session_state.edit_id:
    st.subheader("Edit Transaksi")

    df_edit = pd.DataFrame(st.session_state.data)
    trx = df_edit[df_edit["ID"] == st.session_state.edit_id]

    debit_row = trx[trx["Debit"] > 0].iloc[0]
    kredit_row = trx[trx["Kredit"] > 0].iloc[0]

    with st.form("form_edit"):
        tanggal_baru = st.date_input("Tanggal", debit_row["Tanggal"])

        col1, col2 = st.columns(2)
        with col1:
            akun_debit_baru = st.text_input("Akun Debit", debit_row["Akun"])
            jenis_debit_baru = st.selectbox("Jenis Akun Debit", JENIS_AKUN, index=JENIS_AKUN.index(debit_row["Jenis Akun"]))
        with col2:
            akun_kredit_baru = st.text_input("Akun Kredit", kredit_row["Akun"])
            jenis_kredit_baru = st.selectbox("Jenis Akun Kredit", JENIS_AKUN, index=JENIS_AKUN.index(kredit_row["Jenis Akun"]))

        jumlah_baru = st.number_input("Jumlah", value=float(debit_row["Debit"]))
        update = st.form_submit_button("🔄 Update")

        if update:
            st.session_state.data = [
                d for d in st.session_state.data if d["ID"] != st.session_state.edit_id
            ]

            st.session_state.data.append({
                "ID": st.session_state.edit_id,
                "Tanggal": tanggal_baru,
                "Akun": akun_debit_baru,
                "Jenis Akun": jenis_debit_baru,
                "Debit": jumlah_baru,
                "Kredit": 0
            })
            st.session_state.data.append({
                "ID": st.session_state.edit_id,
                "Tanggal": tanggal_baru,
                "Akun": akun_kredit_baru,
                "Jenis Akun": jenis_kredit_baru,
                "Debit": 0,
                "Kredit": jumlah_baru
            })

            st.session_state.edit_id = None
            st.success("Transaksi berhasil diperbarui")
            st.experimental_rerun()

# ================== LIHAT SEMUA ==================
elif menu == "Lihat Semua":
    st.title("Semua Laporan")

    df = pd.DataFrame(st.session_state.data)

    if df.empty:
        st.warning("Belum ada data")
    else:
        st.subheader("📘 Jurnal Umum")
        st.dataframe(df, use_container_width=True)

        st.subheader("📗 Buku Besar (per Akun)")
        buku_besar = df.groupby(["Jenis Akun", "Akun"])[["Debit", "Kredit"]].sum().reset_index()
        st.dataframe(buku_besar, use_container_width=True)

# ================== SIMPAN EXCEL ==================
elif menu == "Simpan ke Excel":
    st.title("Simpan ke Excel")

    df = pd.DataFrame(st.session_state.data)

    if df.empty:
        st.warning("Belum ada data")
    else:
        buku_besar = df.groupby(["Jenis Akun", "Akun"])[["Debit", "Kredit"]].sum().reset_index()

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Jurnal Umum", index=False)
            buku_besar.to_excel(writer, sheet_name="Buku Besar", index=False)

        output.seek(0)

        st.download_button(
            "Download Excel",
            data=output,
            file_name="laporan_akuntansi.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
