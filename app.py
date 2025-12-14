import streamlit as st
import pandas as pd
from io import BytesIO

# ================== KONFIGURASI ==================
st.set_page_config(
    page_title="Aplikasi Akuntansi",
    layout="wide"
)

# ================== SESSION ==================
if "data" not in st.session_state:
    st.session_state.data = []

# ================== SIDEBAR MENU ==================
menu = st.sidebar.selectbox(
    "📂 Menu",
    [
        "🏠 Home",
        "📘 Jurnal Umum",
        "📗 Buku Besar",
        "📈 Laporan Laba Rugi",
        "📙 Neraca",
        "💾 Simpan ke Excel"
    ]
)

# ================== HOME ==================
if menu == "🏠 Home":
    st.title("📊 Aplikasi Akuntansi Sederhana")
    st.info("Gunakan menu di sidebar kiri untuk berpindah halaman")

    st.markdown("""
    ### 📝 Cara Menggunakan
    1. Input transaksi di **Jurnal Umum**
    2. Lihat rekap di **Buku Besar**
    3. Cek **Laba Rugi** dan **Neraca**
    4. Download laporan di **Simpan ke Excel**
    """)

# ================== JURNAL UMUM ==================
elif menu == "📘 Jurnal Umum":
    st.title("📘 Jurnal Umum")

    with st.form("form_jurnal"):
        tanggal = st.date_input("Tanggal")
        akun = st.text_input("Nama Akun")
        debit = st.number_input("Debit", min_value=0.0)
        kredit = st.number_input("Kredit", min_value=0.0)
        simpan = st.form_submit_button("Simpan")

        if simpan:
            if akun == "":
                st.error("Nama akun tidak boleh kosong")
            else:
                st.session_state.data.append({
                    "Tanggal": tanggal,
                    "Akun": akun,
                    "Debit": debit,
                    "Kredit": kredit
                })
                st.success("Transaksi berhasil disimpan")

    df = pd.DataFrame(st.session_state.data)

    st.subheader("📋 Data Jurnal")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Belum ada transaksi")

# ================== BUKU BESAR ==================
elif menu == "📗 Buku Besar":
    st.title("📗 Buku Besar")

    df = pd.DataFrame(st.session_state.data)

    if not df.empty:
        buku_besar = df.groupby("Akun")[["Debit", "Kredit"]].sum().reset_index()
        st.dataframe(buku_besar, use_container_width=True)
    else:
        st.info("Belum ada data")

# ================== LABA RUGI ==================
elif menu == "📈 Laporan Laba Rugi":
    st.title("📈 Laporan Laba Rugi")

    df = pd.DataFrame(st.session_state.data)

    if not df.empty:
        total_debit = df["Debit"].sum()
        total_kredit = df["Kredit"].sum()
        laba = total_kredit - total_debit

        c1, c2, c3 = st.columns(3)
        c1.metric("Pendapatan", f"Rp {total_kredit:,.0f}")
        c2.metric("Beban", f"Rp {total_debit:,.0f}")
        c3.metric("Laba / Rugi", f"Rp {laba:,.0f}")
    else:
        st.info("Belum ada data")

# ================== NERACA ==================
elif menu == "📙 Neraca":
    st.title("📙 Neraca")

    df = pd.DataFrame(st.session_state.data)

    if not df.empty:
        aset = df["Debit"].sum()
        kewajiban_modal = df["Kredit"].sum()

        neraca = pd.DataFrame({
            "Keterangan": ["Total Aset", "Total Kewajiban + Modal"],
            "Jumlah": [aset, kewajiban_modal]
        })

        st.table(neraca)
    else:
        st.info("Belum ada data")

# ================== SIMPAN EXCEL ==================
elif menu == "💾 Simpan ke Excel":
    st.title("💾 Simpan ke Excel")

    df = pd.DataFrame(st.session_state.data)

    if df.empty:
        st.warning("Belum ada data untuk disimpan")
    else:
        buku_besar = df.groupby("Akun")[["Debit", "Kredit"]].sum().reset_index()

        total_debit = df["Debit"].sum()
        total_kredit = df["Kredit"].sum()
        laba = total_kredit - total_debit

        laba_rugi = pd.DataFrame({
            "Keterangan": ["Pendapatan", "Beban", "Laba / Rugi"],
            "Jumlah": [total_kredit, total_debit, laba]
        })

        neraca = pd.DataFrame({
            "Keterangan": ["Total Aset", "Total Kewajiban + Modal"],
            "Jumlah": [total_debit, total_kredit]
        })

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Jurnal Umum", index=False)
            buku_besar.to_excel(writer, sheet_name="Buku Besar", index=False)
            laba_rugi.to_excel(writer, sheet_name="Laba Rugi", index=False)
            neraca.to_excel(writer, sheet_name="Neraca", index=False)

        output.seek(0)

        st.download_button(
            "📥 Download Laporan Excel",
            data=output,
            file_name="laporan_akuntansi.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
