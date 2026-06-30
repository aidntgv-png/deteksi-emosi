import streamlit as st
import pandas as pd
from db_utils import ambil_riwayat

st.set_page_config(page_title="Riwayat Deteksi Emosi", page_icon="📜", layout="centered")

st.markdown("""
<style>
    .hero {
        background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 50%, #8b5cf6 100%);
        padding: 2rem 1.5rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.35);
    }
    .hero h1 { color: white; font-size: 1.9rem; margin: 0; font-weight: 800; }
    .hero p { color: rgba(255,255,255,0.85); margin-top: 0.4rem; font-size: 0.95rem; }
    .riwayat-card {
        background: #111827;
        border: 1px solid #374151;
        border-left: 5px solid #6366f1;
        border-radius: 14px;
        padding: 0.9rem 1.2rem;
        margin-bottom: 0.6rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .riwayat-emosi { font-weight: 700; font-size: 1.05rem; color: #f1f5f9; }
    .riwayat-waktu { color: #9ca3af; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>📜 Riwayat Deteksi Emosi</h1>
    <p>Daftar waktu dan hasil emosi yang pernah disubmit</p>
</div>
""", unsafe_allow_html=True)

st.page_link("app_streamlit.py", label="⬅️ Kembali ke Deteksi", icon="🔙")

EMOJI_MAP = {
    "happy": "😄", "sad": "😢", "angry": "😠", "surprise": "😲",
    "fear": "😨", "disgust": "🤢", "neutral": "😐",
}

rows = ambil_riwayat()

if not rows:
    st.info("Belum ada riwayat. Submit hasil deteksi dulu di halaman utama.")
else:
    df = pd.DataFrame(rows, columns=["Emosi", "Waktu"])

    # Ringkasan statistik kecil
    col1, col2 = st.columns(2)
    col1.metric("Total Submit", len(df))
    col2.metric("Emosi Terbanyak", df["Emosi"].mode()[0].capitalize())

    st.markdown("#### Riwayat Lengkap")
    for emosi, waktu in rows:
        emoji = EMOJI_MAP.get(emosi.lower(), "🤔")
        st.markdown(f"""
        <div class="riwayat-card">
            <div class="riwayat-emosi">{emoji} {emosi.capitalize()}</div>
            <div class="riwayat-waktu">🕒 {waktu}</div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📋 Lihat sebagai tabel"):
        st.dataframe(df, width="stretch", hide_index=True)
