import streamlit as st
import pandas as pd
from io import BytesIO
import uuid
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

# ================== KONFIGURASI ==================
st.set_page_config(page_title="Aplikasi Akuntansi", layout="wide")

# ================== SESSION STATE ==================
if "data" not in st.session_state:
    st.session_state.data = []

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

# ================== MASTER JENIS AKUN ==================
JENIS_AKUN = ["Aset", "Kewajiban", "Modal", "Pendapatan", "Beban"]

# ================== SIDEBAR MENU ==================
menu = st.sidebar.selectbox(
    "📂 Menu",
    [
        "Jurnal Umum",
        "Buku Besar",
        "Laba Rugi",
        "Neraca",
        "Lihat Semua",
        "Simpan ke Excel"
    ]
)

# ================== HOME + JURNAL UMUM ==================
if menu == "Jurnal Umum":
    st.title("📊 Aplikasi Akuntansi Sederhana")
   
    st.subheader("Input Jurnal Umum")

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
        simpan = st.form_submit_button("Simpan")

        if simpan:
            if akun_debit == "" or akun_kredit == "" or jumlah <= 0:
                st.error("Data tidak valid")
            else:
                trx_id = str(uuid.uuid4())
                st.session_state.data.extend([
                    {
                        "ID": trx_id,
                        "Tanggal": tanggal,
                        "Akun": akun_debit,
                        "Jenis Akun": jenis_debit,
                        "Debit": jumlah,
                        "Kredit": 0
                    },
                    {
                        "ID": trx_id,
                        "Tanggal": tanggal,
                        "Akun": akun_kredit,
                        "Jenis Akun": jenis_kredit,
                        "Debit": 0,
                        "Kredit": jumlah
                    }
                ])
                st.success("Transaksi tersimpan")

    df = pd.DataFrame(st.session_state.data)
    st.subheader("Jurnal Umum")
    st.dataframe(df, use_container_width=True)

# ================== BUKU BESAR ==================
elif menu == "Buku Besar":
    st.title("Buku Besar")
    df = pd.DataFrame(st.session_state.data)

    if df.empty:
        st.warning("Belum ada data")
    else:
        buku_besar = df.groupby(
            ["Jenis Akun", "Akun"]
        )[["Debit", "Kredit"]].sum().reset_index()
        st.dataframe(buku_besar, use_container_width=True)

# ================== LABA RUGI ==================
elif menu == "Laba Rugi":
    st.title("Laporan Laba Rugi")
    df = pd.DataFrame(st.session_state.data)

    if df.empty:
        st.warning("Belum ada data")
    else:
        bb = df.groupby(
            ["Jenis Akun", "Akun"]
        )[["Debit", "Kredit"]].sum().reset_index()

        pendapatan = bb[bb["Jenis Akun"] == "Pendapatan"]
        beban = bb[bb["Jenis Akun"] == "Beban"]

        total_pendapatan = pendapatan["Kredit"].sum()
        total_beban = beban["Debit"].sum()
        laba = total_pendapatan - total_beban

        col1, col2, col3 = st.columns(3)
        col1.metric("Pendapatan", f"Rp {total_pendapatan:,.0f}")
        col2.metric("Beban", f"Rp {total_beban:,.0f}")
        col3.metric("Laba Bersih", f"Rp {laba:,.0f}")

# ================== NERACA ==================
elif menu == "Neraca":
    st.title("Neraca")
    df = pd.DataFrame(st.session_state.data)

    if df.empty:
        st.warning("Belum ada data")
    else:
        bb = df.groupby(
            ["Jenis Akun", "Akun"]
        )[["Debit", "Kredit"]].sum().reset_index()

        aset = bb[bb["Jenis Akun"] == "Aset"]["Debit"].sum()
        kewajiban = bb[bb["Jenis Akun"] == "Kewajiban"]["Kredit"].sum()
        modal = bb[bb["Jenis Akun"] == "Modal"]["Kredit"].sum()

        pendapatan = bb[bb["Jenis Akun"] == "Pendapatan"]["Kredit"].sum()
        beban = bb[bb["Jenis Akun"] == "Beban"]["Debit"].sum()
        laba = pendapatan - beban

        modal_akhir = modal + laba

        col1, col2 = st.columns(2)
        col1.metric("Total Aset", f"Rp {aset:,.0f}")
        col2.metric("Kewajiban + Modal", f"Rp {(kewajiban + modal_akhir):,.0f}")

# ================== LIHAT SEMUA ==================
elif menu == "Lihat Semua":
    st.title("Semua Laporan")
    df = pd.DataFrame(st.session_state.data)
    st.dataframe(df, use_container_width=True)

# ================== SIMPAN EXCEL ==================
elif menu == "Simpan ke Excel":
    st.title("Simpan ke Excel")

    df = pd.DataFrame(st.session_state.data)

    if df.empty:
        st.warning("Belum ada data")
    else:
        bb = df.groupby(
            ["Jenis Akun", "Akun"]
        )[["Debit", "Kredit"]].sum().reset_index()

        pendapatan = bb[bb["Jenis Akun"] == "Pendapatan"]["Kredit"].sum()
        beban = bb[bb["Jenis Akun"] == "Beban"]["Debit"].sum()
        laba = pendapatan - beban

        laba_rugi = pd.DataFrame({
            "Keterangan": ["Pendapatan", "Beban", "Laba Bersih"],
            "Jumlah": [pendapatan, beban, laba]
        })

        aset = bb[bb["Jenis Akun"] == "Aset"]["Debit"].sum()
        kewajiban = bb[bb["Jenis Akun"] == "Kewajiban"]["Kredit"].sum()
        modal = bb[bb["Jenis Akun"] == "Modal"]["Kredit"].sum()

        neraca = pd.DataFrame({
            "Keterangan": ["Aset", "Kewajiban", "Modal Akhir"],
            "Jumlah": [aset, kewajiban, modal + laba]
        })

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, "Jurnal Umum", index=False)
            bb.to_excel(writer, "Buku Besar", index=False)
            laba_rugi.to_excel(writer, "Laba Rugi", index=False)
            neraca.to_excel(writer, "Neraca", index=False)

        output.seek(0)
        st.download_button(
            "Download Excel",
            data=output,
            file_name="laporan_akuntansi.xlsx"
        )
