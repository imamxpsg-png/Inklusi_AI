import streamlit as st
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import os
import random
import urllib.parse

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

# INJEKSI CSS KUSTOM: TEMA LIGHT MODERN & FIX SINKRONISASI TOMBOL BERANDA
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
    
    /* FIX WARNA TOMBOL AGAR TERANG DAN JELAS KONTRAST DI HP */
    div[data-testid="stVerticalBlock"] div.stButton > button {
        background-color: #F1F5F9 !important; 
        color: #0F172A !important;            
        border: 1px solid #CBD5E1 !important;  
        border-radius: 12px !important;       
        font-weight: 700 !important;          
        font-size: 15px !important;
        height: auto !important;
        width: 100% !important;
    }
    div[data-testid="stVerticalBlock"] div.stButton > button:hover {
        background-color: #E2E8F0 !important;
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
            
            # Mengubah Nama Tab Utama Menjadi Galeri Foto Dokumentasi
            tab_galeri, tab_maps, tab_cuaca = st.tabs(["📸 Galeri Foto Dokumentasi", "🗺️ Peta Live GPS", "🌤️ Kondisi Cuaca"])
            
            with tab_galeri:
                # Tautan URL gambar ilustrasi beresolusi tinggi dari server cloud publik 
                # (Sangat ringan, 100% anti-crash, dan responsif digeser pakai jari di HP)
                foto1_url = "https://msftstories.thesourcemediaassets.com/sites/677/2024/09/COVER.png"
                foto2_url = "https://www.idn.id/wp-content/uploads/2025/06/Featured-Image-Artikel-rbt-1024x640.jpg"
                foto3_url = "https://course-net.com/wp-content/uploads/2025/03/7199787_30495_11zon.webp"
                
                # Merender komponen slider/carousel foto interaktif murni menggunakan HTML/CSS/JS Swiper
                st.components.v1.html(f"""
                    <div id="photo_carousel" style="position: relative; width: 100%; height: 230px; border-radius: 12px; overflow: hidden; background-color: #000; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
                        
                        <!-- Track Wadah Foto -->
                        <div id="carousel_track" style="display: flex; width: 300%; height: 100%; transition: transform 0.4s ease-in-out;">
                            <img src="{foto1_url}" style="width: 33.333%; height: 100%; object-fit: cover;">
                            <img src="{foto2_url}" style="width: 33.333%; height: 100%; object-fit: cover;">
                            <img src="{foto3_url}" style="width: 33.333%; height: 100%; object-fit: cover;">
                        </div>

                        <!-- Tombol Navigasi Panah Kiri -->
                        <button onclick="moveSlide(-1)" style="position: absolute; top: 50%; left: 10px; transform: translateY(-50%); background: rgba(0,0,0,0.5); color: white; border: none; font-size: 18px; padding: 8px 12px; border-radius: 50%; cursor: pointer; z-index: 10;">❮</button>
                        
                        <!-- Tombol Navigasi Panah Kanan -->
                        <button onclick="moveSlide(1)" style="position: absolute; top: 50%; right: 10px; transform: translateY(-50%); background: rgba(0,0,0,0.5); color: white; border: none; font-size: 18px; padding: 8px 12px; border-radius: 50%; cursor: pointer; z-index: 10;">❯</button>

                        <!-- Tanda Titik Halaman Bawah (Dots Indicator) -->
                        <div style="position: absolute; bottom: 10px; left: 50%; transform: translateX(-50%); display: flex; gap: 8px; z-index: 10;">
                            <span class="dot" onclick="setSlide(0)" style="height: 10px; width: 10px; background-color: #bbb; border-radius: 50%; display: inline-block; cursor: pointer; transition: 0.3s;"></span>
                            <span class="dot" onclick="setSlide(1)" style="height: 10px; width: 10px; background-color: #bbb; border-radius: 50%; display: inline-block; cursor: pointer; transition: 0.3s;"></span>
                            <span class="dot" onclick="setSlide(2)" style="height: 10px; width: 10px; background-color: #bbb; border-radius: 50%; display: inline-block; cursor: pointer; transition: 0.3s;"></span>
                        </div>
                    </div>

                    <script>
                        var currentIdx = 0;
                        var track = document.getElementById('carousel_track');
                        var dots = document.getElementsByClassName('dot');
                        
                        function updateCarousel() {{
                            track.style.transform = 'translateX(' + (-currentIdx * 33.333) + '%)';
                            for (var i = 0; i < dots.length; i++) {{
                                dots[i].style.backgroundColor = (i === currentIdx) ? '#1E3A8A' : '#bbb';
                            }}
                        }}

                        function moveSlide(direction) {{
                            currentIdx += direction;
                            if (currentIdx > 2) currentIdx = 0;
                            if (currentIdx < 0) currentIdx = 2;
                            updateCarousel();
                        }}

                        function setSlide(idx) {{
                            currentIdx = idx;
                            updateCarousel();
                        }}

                        // Pendeteksi usapan jari tangan (Swipe Touch Gestures) untuk HP/Smartphone
                        var startX = 0;
                        var container = document.getElementById('photo_carousel');
                        
                        container.addEventListener('touchstart', function(e) {{
                            startX = e.touches[0].clientX;
                        }}, false);
                        
                        container.addEventListener('touchend', function(e) {{
                            var endX = e.changedTouches[0].clientX;
                            var diffX = startX - endX;
                            if (Math.abs(diffX) > 50) {{
                                if (diffX > 0) moveSlide(1);  // Geser ke kiri -> slide maju
                                else moveSlide(-1);           // Geser ke kanan -> slide mundur
                            }}
                        }}, false);

                        updateCarousel(); // Jalankan inisialisasi awal warna dots
                    </script>
                """, height=240)
            
            with tab_maps:
                st.map({"lat": [-7.3305], "lon": [110.5084]}, zoom=14, use_container_width=True)
                st.caption("📍 Lokasi Terdeteksi: Dukuh, Kota Salatiga, Jawa Tengah.")
                
            with tab_cuaca:
                c_col1, c_col2 = st.columns(2)
                with c_col1: st.metric(label="🌡️ Temperatur Udara", value="24°C", delta="Cerah")
                with c_col2: st.metric(label="💧 Kelembapan Sekitar", value="78%", delta="Angin 14 km/jam")
        
    with v_col2:
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
