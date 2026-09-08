import streamlit as st
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import os
import random
import urllib.parse
import base64  # Library pembantu untuk membaca video lokal tanpa error sandbox

# IMPOR FUNGSI MODULAR INTERNAL & PEMBANTU UI
from interface_helper import render_top_dashboard_widgets, render_sidebar_status  
from obrolan_helper import render_live_chat         
from asisten_helper import render_asisten_ai        
from menu_helper import render_dashboard_menu  

# =====================================================================
# 1. KONFIGURASI HALAMAN UTAMA STREAMLIT (MOBILE FRIENDLY)
# =====================================================================
st.set_page_config(
    page_title="Hermes Autonomous Hands-Free Assistant", 
    page_icon="♿", 
    layout="wide"
)

# INJEKSI CSS KUSTOM: TEMA LIGHT MODERN & PENGUNCI WARNA TOMBOL BERANDA
st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        color: #0F172A;
    }
    
    /* BINGKAI KOTAK FITUR UTUH DI HALAMAN BARU */
    .card-asisten {
        background-color: #F0FDF4 !important; padding: 24px; border-radius: 20px;
        border: 2px solid #BBF7D0 !important; margin-bottom: 20px;
    }
    .card-sos {
        background-color: #FFF5F5 !important; padding: 24px; border-radius: 20px;
        border: 2px solid #FEB2B2 !important; margin-bottom: 20px;
    }
    .card-obrolan {
        background-color: #F0FDFA !important; padding: 24px; border-radius: 20px;
        border: 1px solid #99F6E4 !important; margin-bottom: 20px;
    }
    .card-dokumen {
        background-color: #FAF5FF !important; padding: 24px; border-radius: 20px;
        border: 1px solid #E9D5FF !important; margin-bottom: 20px;
    }
    
    /* ===================================================================== */
    /* FIX EMERGENSI: MEMAKSA TOMBOL BERANDA MENJADI TERANG DAN TULISAN HITAM */
    /* ===================================================================== */
    div[data-testid="stVerticalBlock"] div.stButton > button {
        background-color: #F1F5F9 !important; /* Latar belakang abu-abu terang */
        color: #0F172A !important;            /* Warna teks hitam pekat agar kontras */
        border: 1px solid #CBD5E1 !important;  /* Garis tepi tipis agar rapi */
        border-radius: 12px !important;       /* Kotak melengkung modern */
        font-weight: 700 !important;          /* Tulisan dipertebal */
        font-size: 15px !important;
        height: auto !important;
        width: 100% !important;
    }
    div[data-testid="stVerticalBlock"] div.stButton > button:hover {
        background-color: #E2E8F0 !important; /* Efek hover saat disentuh jari */
        color: #000000 !important;
    }
    
    .main-title { color: #1E3A8A; font-family: 'Inter', sans-serif; font-weight: 800; font-size: 26px; letter-spacing: -0.5px; margin-bottom: 0px; }
    .sub-title { color: #64748B; font-weight: 500; font-size: 14px; margin-top: 4px; }
    p, span, label, th, td, .stMarkdown { color: #1E293B !important; font-family: 'Inter', sans-serif; }
    h3 { font-weight: 700 !important; margin-bottom: 8px !important; }
    div[data-testid="stForm"] { background-color: transparent !important; border: none !important; padding: 0 !important; }
    </style>
""", unsafe_allow_html=True)

# INSIALISASI STATE NAVIGASI & MEMORI PERMANEN
if "current_page" not in st.session_state: st.session_state.current_page = "menu_utama"
if "nomor_wali" not in st.session_state: st.session_state.nomor_wali = ""

# MEKANISME ROTASI API KEY GEMINI
api_keys_pool = [os.getenv("GEMINI_API_KEY"), os.getenv("GEMINI_KEY_2")]
active_keys = [key for key in api_keys_pool if key]

from google import genai
def get_gemini_client():
    if not active_keys: return None
    return genai.Client(api_key=random.choice(active_keys))
client = get_gemini_client()

# BACKGROUND SCHEDULER ALARM
@st.cache_resource
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.start()
    return scheduler
sched = start_scheduler()

# KELOMPOK POSISI ATAS: JUDUL UTAMA TERLEBIH DAHULU
st.markdown("<h1 class='main-title'>🎙️ Hermes Universal Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Asisten Disabilitas Otonom Berbasis Bingkai Kotak Ringkas Per Fitur</p>", unsafe_allow_html=True)
st.write("---")
# =====================================================================
# TATA LETAK BARIS MEDIA PAS DI BAWAH TULISAN JUDUL (BERDAMPINGAN)
# =====================================================================
if st.session_state.current_page == "menu_utama":
    v_col1, v_col2 = st.columns(2)
    
    with v_col1:
        with st.container(border=True):
            st.markdown("<b style='font-size: 13px; color: #1E3A8A;'>📺 PUSAT MEDIA INTERAKTIF (DAPAT DIGESER)</b>", unsafe_allow_html=True)
            
            # Membuat Tab Geser Internal
            tab_video, tab_maps, tab_cuaca = st.tabs(["🎥 Video Dokumentasi", "🗺️ Peta Live GPS", "🌤️ Kondisi Cuaca"])
            
            with tab_video:
                video1_path = os.path.join(os.path.dirname(__file__), "video.mp4")
                video2_path = os.path.join(os.path.dirname(__file__), "video_inklusi2.mp4")
                
                # Mengonversi kedua berkas video lokal Anda menjadi format data Base64 aman hulu
                if os.path.exists(video1_path) and os.path.exists(video2_path):
                    with open(video1_path, "rb") as f1:
                        v1_data = base64.b64encode(f1.read()).decode("utf-8")
                    with open(video2_path, "rb") as f2:
                        v2_data = base64.b64encode(f2.read()).decode("utf-8")
                        
                    # Merender HTML5 video player kustom ukuran penuh pas bingkai
                    st.components.v1.html(f"""
                        <video id="hermes_player" width="100%" height="230" controls autoplay muted style="border-radius:12px; background-color:#000; object-fit: cover; width: 100%; height: 230px;">
                            <source id="video_source" src="data:video/mp4;base64,{v1_data}" type="video/mp4">
                            Browser Anda tidak mendukung tag video ini.
                        </video>

                        <script>
                            var videoPlayer = document.getElementById('hermes_player');
                            var videoSource = document.getElementById('video_source');
                            
                            var playlist = [
                                "data:video/mp4;base64,{v1_data}",
                                "data:video/mp4;base64,{v2_data}"
                            ];
                            var currentVideoIndex = 0;

                            videoPlayer.onended = function() {{
                                currentVideoIndex++;
                                if (currentVideoIndex >= playlist.length) {{
                                    currentVideoIndex = 0;
                                }}
                                videoSource.src = playlist[currentVideoIndex];
                                videoPlayer.load();
                                videoPlayer.play();
                            }};
                        </script>
                    """, height=240)
                else:
                    st.info("💡 Pastikan file 'video.mp4' dan 'video_inklusi2.mp4' sudah berada di folder proyek.")
            
            with tab_maps:
                # Menampilkan Peta Lokasi Live GPS di Salatiga
                lokasi_salatiga = {"lat": [-7.3305], "lon": [110.5084]}
                st.map(lokasi_salatiga, zoom=14, use_container_width=True)
                st.caption("📍 Lokasi Terdeteksi: Dukuh, Kota Salatiga, Jawa Tengah.")
                
            with tab_cuaca:
                c_col1, c_col2 = st.columns(2)
                with c_col1:
                    st.metric(label="🌡️ Temperatur Udara", value="24°C", delta="Cerah")
                with c_col2:
                    st.metric(label="💧 Kelembapan Sekitar", value="78%", delta="Angin 14 km/jam")
        
    with v_col2:
        # Menampilkan widget info status gawai di sebelah kanan media slider Anda
        render_top_dashboard_widgets()
    st.write("---")

# =====================================================================
# 3. ROUTER NAVIGASI DASHBOARD HALAMAN BARU
# =====================================================================
if st.session_state.current_page == "menu_utama":
    render_dashboard_menu()

elif st.session_state.current_page == "asisten_ai":
    if st.button("⬅️ KEMBALI KE DASHBOARD UTAMA", use_container_width=True): st.session_state.current_page = "menu_utama"; st.rerun()
    render_asisten_ai(client, sched, mode="asisten")

elif st.session_state.current_page == "modul_sos":
    if st.button("⬅️ KEMBALI KE DASHBOARD UTAMA", use_container_width=True): st.session_state.current_page = "menu_utama"; st.rerun()
    from sos_helper import render_sos_menu
    render_sos_menu()

elif st.session_state.current_page == "terjemahan_live":
    if st.button("⬅️ KEMBALI KE DASHBOARD UTAMA", use_container_width=True): st.session_state.current_page = "menu_utama"; st.rerun()
    render_live_chat(client)

elif st.session_state.current_page == "dokumen_materi":
    if st.button("⬅️ KEMBALI KE DASHBOARD UTAMA", use_container_width=True): st.session_state.current_page = "menu_utama"; st.rerun()
    render_sidebar_status(active_keys, client, mode="dokumen")
