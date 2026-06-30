import av
import time
import cv2
import streamlit as st
from deepface import DeepFace
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
from db_utils import simpan_riwayat, ambil_terakhir

st.set_page_config(page_title="Deteksi Emosi", page_icon="🙂", layout="centered")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
    .hero {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        padding: 2.2rem 1.5rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.35);
    }
    .hero h1 { color: white; font-size: 2.1rem; margin: 0; font-weight: 800; }
    .hero p { color: rgba(255,255,255,0.85); margin-top: 0.4rem; font-size: 0.95rem; }
    div.stButton > button {
        border-radius: 12px;
        font-weight: 700;
        padding: 0.65rem 0;
        border: none;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover { transform: translateY(-2px); }
    .emotion-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid #4f46e5;
        border-radius: 16px;
        padding: 1.2rem;
        text-align: center;
        margin-top: 1rem;
    }
    .emotion-label {
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #818cf8, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .last-saved {
        background: #0f172a;
        border-left: 4px solid #22c55e;
        padding: 0.7rem 1rem;
        border-radius: 8px;
        color: #d1d5db;
        font-size: 0.9rem;
        margin-top: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🙂 Deteksi Emosi Wajah Real-Time</h1>
    <p>OpenCV + DeepFace · Live Camera Emotion Recognition</p>
</div>
""", unsafe_allow_html=True)

st.page_link("pages/1_Riwayat.py", label="📜 Lihat Halaman Riwayat", icon="➡️")

EMOJI_MAP = {
    "happy": "😄", "sad": "😢", "angry": "😠", "surprise": "😲",
    "fear": "😨", "disgust": "🤢", "neutral": "😐",
}

if "emosi_terkini" not in st.session_state:
    st.session_state.emosi_terkini = None


class EmotionProcessor(VideoProcessorBase):
    def __init__(self):
        self.last_check = 0
        self.interval = 1.5  # detik antar analisis, biar gak berat
        self.last_emotion = "neutral"

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        now = time.time()

        if now - self.last_check > self.interval:
            self.last_check = now
            try:
                hasil = DeepFace.analyze(img, actions=["emotion"], enforce_detection=False)
                self.last_emotion = hasil[0]["dominant_emotion"]
                st.session_state.emosi_terkini = self.last_emotion
            except Exception:
                pass

        cv2.putText(
            img,
            f"Emosi: {self.last_emotion}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        return av.VideoFrame.from_ndarray(img, format="bgr24")


RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

ctx = webrtc_streamer(
    key="deteksi-emosi",
    video_processor_factory=EmotionProcessor,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
)

emotion_placeholder = st.empty()
saved_placeholder = st.empty()


def render_emotion(emosi: str):
    emoji = EMOJI_MAP.get(emosi.lower(), "🤔")
    emotion_placeholder.markdown(f"""
    <div class="emotion-card">
        <div style="font-size:2.2rem;">{emoji}</div>
        <div class="emotion-label">{emosi.capitalize()}</div>
    </div>
    """, unsafe_allow_html=True)


if st.session_state.emosi_terkini:
    render_emotion(st.session_state.emosi_terkini)
else:
    st.info("Izinkan akses kamera di browser, lalu tunggu beberapa detik untuk deteksi pertama.")

submit = st.button("💾 Submit Hasil", width="stretch")

if submit:
    if st.session_state.emosi_terkini:
        waktu = simpan_riwayat(st.session_state.emosi_terkini)
        st.toast(f"Tersimpan: {st.session_state.emosi_terkini} pada {waktu}", icon="✅")
    else:
        st.toast("Belum ada emosi terdeteksi.", icon="⚠️")

terakhir = ambil_terakhir()
if terakhir:
    emosi_terakhir, waktu_terakhir = terakhir
    saved_placeholder.markdown(
        f"<div class='last-saved'>🕒 Terakhir disimpan: <b>{emosi_terakhir}</b> pada <b>{waktu_terakhir}</b></div>",
        unsafe_allow_html=True
    )
