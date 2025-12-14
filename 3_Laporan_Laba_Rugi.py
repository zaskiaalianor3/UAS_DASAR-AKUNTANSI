import streamlit as st
import pandas as pd

st.title("📈 Laporan Laba Rugi")

df = pd.DataFrame(st.session_state.get("data", []))

if not df.empty:
    total_debit = df["Debit"].sum()
    total_kredit = df["Kredit"].sum()
    laba = total_kredit - total_debit

    st.metric("Pendapatan", f"Rp {total_kredit:,.0f}")
    st.metric("Beban", f"Rp {total_debit:,.0f}")
    st.metric("Laba / Rugi", f"Rp {laba:,.0f}")
else:
    st.info("Belum ada data")