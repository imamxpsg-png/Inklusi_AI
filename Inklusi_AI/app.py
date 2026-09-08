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

# INJEKSI CSS KUSTOM: TEMA LIGHT MODERN & EFEK INTERAKTIF GAMBAR BERJALAN
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
    
    /* STYLE KUSTOM UNTUK BANNER GAMBAR BERJALAN INTERAKTIF */
    .running-banner-container {
        width: 100%;
        overflow: hidden;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 10px 0;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    
    .running-track {
        display: flex;
        width: max-content;
        animation: marqueeScroll 25s linear infinite;
    }
    
    .running-track:hover {
        animation-play-state: paused;
    }
    
    .interactive-img {
        height: 80px;
        margin: 0 40px;
        object-fit: contain;
        transition: transform 0.3s ease, filter 0.3s ease;
        border-radius: 8px;
    }
    
    .interactive-img:hover {
        transform: scale(1.15); 
        filter: drop-shadow(0 0 12px rgba(30, 58, 138, 0.4)); 
    }
    
    @keyframes marqueeScroll {
        0% { transform: translateX(0%); }
        100% { transform: translateX(-50%); }
    }
    
    .main-title { color: #1E3A8A; font-family: 'Inter', sans-serif; font-weight: 800; font-size: 26px; letter-spacing: -0.5px; margin-bottom: 0px; }
    .sub-title { color: #64748B; font-weight: 500; font-size: 14px; margin-top: 4px; }
    .status-text-bar { font-size: 13px; font-weight: 600; color: #475569; margin-top: 8px; background: #FFFFFF; padding: 8px 14px; border-radius: 10px; border: 1px solid #E2E8F0; display: inline-block; }
    p, span, label, th, td, .stMarkdown { color: #1E293B !important; font-family: 'Inter', sans-serif; }
    h3 { font-weight: 700 !important; margin-bottom: 8px !important; }
    div[data-testid="stForm"] { background-color: transparent !important; border: none !important; padding: 0 !important; }
    </style>
""", unsafe_allow_html=True)

# INSIALISASI STATE NAVIGASI & MEMORI PERMANEN
if "current_page" not in st.session_state: st.session_state.current_page = "menu_utama"
if "nomor_wali" not in st.session_state: st.session_state.nomor_wali = ""
if "list_alarm" not in st.session_state: st.session_state.list_alarm = []
if "alarm_terpicu" not in st.session_state: st.session_state.alarm_terpicu = {}

# KOORDINAT DEFAULT GPS
if "user_lat" not in st.session_state: st.session_state.user_lat = -7.3305
if "user_lon" not in st.session_state: st.session_state.user_lon = 110.5084

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

# Perhitungan waktu WIB
waktu_utc = datetime.datetime.utcnow()
waktu_wib = waktu_utc + datetime.timedelta(hours=7)
waktu_sekarang_str = waktu_wib.strftime("%H:%M")

st.markdown(f"<div class='status-text-bar'>⏰ {waktu_sekarang_str} WIB | 🌤️ Status: Sistem Online Siaga</div>", unsafe_allow_html=True)
st.write("---")
# =====================================================================
# BANNER LOGO UNIVERSITAS BERJALAN & INTERAKTIF (DIPISAH DI ATAS MEDIA)
# =====================================================================
if st.session_state.current_page == "menu_utama":
    # FIX: Menggunakan Direct CDN Image Link yang valid, aman, dan anti-blokir untuk banner atas
    logo_unsw_url = "https://unsplash.com"
    
    st.markdown(f"""
        <div class="running-banner-container">
            <div class="running-track">
                <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTdKjzrg_RSda0TzIKe9EA3yGkgFP4vlJ_YZX5K1EunpA&s" class="interactive-img">
                <img src="{logo_unsw_url}" class="interactive-img">
                <img src="{logo_unsw_url}" class="interactive-img">
                <img src="{logo_unsw_url}" class="interactive-img">
                <img src="{logo_unsw_url}" class="interactive-img">
                <img src="{logo_unsw_url}" class="interactive-img">
            </div>
        </div>
    """, unsafe_allow_html=True)

# =====================================================================
# TATA LETAK BARIS MEDIA PENUH (SISTEM SATU KOLOM LUAS)
# =====================================================================
if st.session_state.current_page == "menu_utama":
    
    # Jembatan Geolocation GPS HP Real-time
    st.components.v1.html("""
        <script>
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                var lat = position.coords.latitude;
                var lon = position.coords.longitude;
                window.parent.postMessage({
                    type: 'streamlit:set_component_value',
                    value: "GPS_UPDATE:" + lat + "," + lon
                }, '*');
            });
        }
        </script>
    """, height=0)

    html_event_gps = st.session_state.get("py_bridge_receiver", "")
    if html_event_gps and "GPS_UPDATE:" in html_event_gps:
        try:
            koordinat_raw = html_event_gps.replace("GPS_UPDATE:", "").split(",")
            st.session_state.user_lat = float(koordinat_raw[0])
            st.session_state.user_lon = float(koordinat_raw[1])
        except: pass

    with st.container(border=True):
        st.markdown("<b style='font-size: 13px; color: #1E3A8A;'>📺 PUSAT MEDIA INTERAKTIF & MULTI-ALARM DAFTAR</b>", unsafe_allow_html=True)
        
        tab_galeri, tab_alarm, tab_maps, tab_cuaca = st.tabs(["📸 Galeri 5 Foto Kotak", "⏰ Multi-Alarm Kustom", "🗺️ Peta Live GPS", "🌤️ Kondisi Cuaca"])
        
        with tab_galeri:
            # Jajaran 5 Foto untuk Galeri Kotak di bawah (Sengaja dibedakan agar bervariasi dengan banner atas)
            foto1 = "https://unsplash.com"  # Robot AI
            foto2 = "https://unsplash.com"  # Kolaborasi Pembelajaran
            foto3 = "https://unsplash.com"  # Dashboard Web UI
            foto4 = "https://unsplash.com"  # Diskusi Mahasiswa
            foto5 = "https://unsplash.com"  # Cloud Computing
            
            # Merender Galeri Kotak Persegi Sempurna (Square Aspect Ratio 1:1) dengan navigasi halus
            st.components.v1.html(f"""
                <div id="box_carousel" style="position: relative; max-width: 300px; margin: 0 auto; aspect-ratio: 1 / 1; border-radius: 16px; overflow: hidden; background-color: #1a1a1a; box-shadow: 0 8px 20px rgba(0,0,0,0.2); border: 2px solid #E2E8F0;">
                    
                    <!-- Track Wadah Multi-Foto (Kapasitas 5 Slide) -->
                    <div id="carousel_track" style="display: flex; width: 500%; height: 100%; transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1);">
                        <img src="{foto1}" style="width: 20%; height: 100%; object-fit: cover;">
                        <img src="{foto2}" style="width: 20%; height: 100%; object-fit: cover;">
                        <img src="{foto3}" style="width: 20%; height: 100%; object-fit: cover;">
                        <img src="{foto4}" style="width: 20%; height: 100%; object-fit: cover;">
                        <img src="{foto5}" style="width: 20%; height: 100%; object-fit: cover;">
                    </div>

                    <!-- Tombol Navigasi Kiri-Kanan Bulat Elegan -->
                    <button onclick="moveSlide(-1)" style="position: absolute; top: 50%; left: 10px; transform: translateY(-50%); background: rgba(0,0,0,0.6); color: white; border: none; font-size: 16px; width: 34px; height: 34px; border-radius: 50%; cursor: pointer; z-index: 10; display: flex; align-items: center; justify-content: center; outline:none;">❮</button>
                    <button onclick="moveSlide(1)" style="position: absolute; top: 50%; right: 10px; transform: translateY(-50%); background: rgba(0,0,0,0.6); color: white; border: none; font-size: 16px; width: 34px; height: 34px; border-radius: 50%; cursor: pointer; z-index: 10; display: flex; align-items: center; justify-content: center; outline:none;">❯</button>

                    <!-- Indikator 5 Titik Halaman Bawah (Dots) -->
                    <div style="position: absolute; bottom: 12px; left: 50%; transform: translateX(-50%); display: flex; gap: 6px; z-index: 10;">
                        <span class="dot" onclick="setSlide(0)" style="height: 8px; width: 8px; background-color: rgba(255,255,255,0.4); border-radius: 50%; display: inline-block; cursor: pointer; transition: 0.3s;"></span>
                        <span class="dot" onclick="setSlide(1)" style="height: 8px; width: 8px; background-color: rgba(255,255,255,0.4); border-radius: 50%; display: inline-block; cursor: pointer; transition: 0.3s;"></span>
                        <span class="dot" onclick="setSlide(2)" style="height: 8px; width: 8px; background-color: rgba(255,255,255,0.4); border-radius: 50%; display: inline-block; cursor: pointer; transition: 0.3s;"></span>
                        <span class="dot" onclick="setSlide(3)" style="height: 8px; width: 8px; background-color: rgba(255,255,255,0.4); border-radius: 50%; display: inline-block; cursor: pointer; transition: 0.3s;"></span>
                        <span class="dot" onclick="setSlide(4)" style="height: 8px; width: 8px; background-color: rgba(255,255,255,0.4); border-radius: 50%; display: inline-block; cursor: pointer; transition: 0.3s;"></span>
                    </div>
                </div>

                <script>
                    var currentIdx = 0; 
                    var track = document.getElementById('carousel_track');
                    var dots = document.getElementsByClassName('dot');
                    
                    function updateCarousel() {{
                        track.style.transform = 'translateX(' + (-currentIdx * 20) + '%)';
                        for (var i = 0; i < dots.length; i++) {{
                            dots[i].style.backgroundColor = (i === currentIdx) ? '#FFFFFF' : 'rgba(255,255,255,0.4)';
                            dots[i].style.width = (i === currentIdx) ? '16px' : '8px';
                            dots[i].style.borderRadius = (i === currentIdx) ? '4px' : '50%';
                        }}
                    }}

                    function moveSlide(dir) {{
                        currentIdx += dir;
                        if (currentIdx > 4) currentIdx = 0;
                        if (currentIdx < 0) currentIdx = 4;
                        updateCarousel();
                    }}

                    function setSlide(idx) {{
                        currentIdx = idx;
                        updateCarousel();
                    }}

                    var startX = 0;
                    document.getElementById('box_carousel').addEventListener('touchstart', function(e) {{
                        startX = e.touches.clientX;
                    }}, false);
                    document.getElementById('box_carousel').addEventListener('touchend', function(e) {{
                        var diffX = startX - e.changedTouches.clientX;
                        if (Math.abs(diffX) > 40) {{
                            if (diffX > 0) moveSlide(1); else moveSlide(-1);
                        }}
                    }}, false);

                    updateCarousel();
                </script>
            """, height=330)
        with tab_alarm:
            st.markdown("<b style='font-size:14px; color:#1E3A8A;'>⏰ Tambah Jadwal Alarm Baru:</b>", unsafe_allow_html=True)
            col_a1, col_a2 = st.columns(2)
            with col_a1: jam_pilihan = st.selectbox("Pilih Jam:", [f"{i:02d}" for i in range(24)], index=waktu_wib.hour, key="sb_jam_multi")
            with col_a2: menit_pilihan = st.selectbox("Pilih Menit:", [f"{i:02d}" for i in range(60)], index=waktu_wib.minute, key="sb_menit_multi")
                
            teks_suara_kustom = st.text_input("Ketik Kalimat Perintah Ucapan Google untuk Alarm Ini:", placeholder="Contoh: Ayo bangun bos, waktunya minum obat siang.", key="ti_teks_multi")
            
            if st.button("➕ MASUKKAN KE DAFTAR ALARM SAYA", use_container_width=True):
                waktu_baru = f"{jam_pilihan}:{menit_pilihan}"
                st.session_state.list_alarm.append({"waktu": waktu_baru, "teks": teks_suara_kustom if teks_suara_kustom else "Waktu alarm Anda telah tiba."})
                st.success(f"✓ Berhasil menambahkan alarm baru untuk pukul {waktu_baru} WIB!")
                st.rerun()
                
            if st.session_state.list_alarm:
                st.write("---")
                st.markdown("<b style='font-size:13px; color:#475569;'>📋 Daftar Alarm Anda:</b>", unsafe_allow_html=True)
                for idx, item in enumerate(st.session_state.list_alarm):
                    col_t1, col_t2, col_t3 = st.columns(3)
                    with col_t1: st.markdown(f"⏰ **{item['waktu']} WIB**")
                    with col_t2: st.markdown(f"🗣️ *\"{item['teks']}\"*")
                    with col_t3:
                        if st.button("❌ Hapus", key=f"del_alarm_{idx}"): st.session_state.list_alarm.pop(idx); st.rerun()
            
            for item in st.session_state.list_alarm:
                if waktu_sekarang_str == item['waktu']:
                    identitas_kunci = f"{item['waktu']}_{item['teks']}"
                    if st.session_state.alarm_terpicu.get(identitas_kunci) != waktu_sekarang_str:
                        st.markdown(f"<div style='background-color:#FFF5F5; padding:16px; border-radius:14px; border:2px solid #FEB2B2; margin-top:10px;'><h3>⏰ [ALARM BERBUNYI]</h3><p>🗣️ Google: \"<b>{item['teks']}</b>\"</p></div>", unsafe_allow_html=True)
                        import modules as mod
                        st.audio(mod.text_to_speech(item['teks'], f"alarm_{item['waktu']}.mp3"), autoplay=True)
                        st.session_state.alarm_terpicu[identitas_kunci] = waktu_sekarang_str
        
        with tab_maps:
            st.map({"lat": [st.session_state.user_lat], "lon": [st.session_state.user_lon]}, zoom=15, use_container_width=True)
            st.caption("📍 Peta Interaktif GPS: Menyesuaikan lokasi real-time gawai Anda saat ini.")
            
        with tab_cuaca:
            c_col1, c_col2 = st.columns(2)
            with c_col1: st.metric(label="🌡️ Temperatur Udara Salatiga", value="24°C", delta="Cerah Berawan")
            with c_col2: st.metric(label="💧 Kelembapan Sekitar", value="78%", delta="Angin 14 km/jam")
            
    st.write("---")

# =====================================================================
# 3. ROUTER NAVIGASI DASHBOARD HALAMAN BARU
# =====================================================================
if st.session_state.current_page == "menu_utama":
    render_dashboard_menu()
elif st.session_state.current_page == "asisten_ai":
    if st.button("⬅️ KEMBALI KE DASHBOARD UTAMA", use_container_width=True, key="back_asisten"): st.session_state.current_page = "menu_utama"; st.rerun()
    render_asisten_ai(client, sched, mode="asisten")
elif st.session_state.current_page == "modul_sos":
    if st.button("⬅️ KEMBALI KE DASHBOARD UTAMA", use_container_width=True, key="back_sos"): st.session_state.current_page = "menu_utama"; st.rerun()
    from sos_helper import render_sos_menu
    render_sos_menu()
elif st.session_state.current_page == "terjemahan_live":
    if st.button("⬅️ KEMBALI KE DASHBOARD UTAMA", use_container_width=True, key="back_chat"): st.session_state.current_page = "menu_utama"; st.rerun()
    render_live_chat(client)
elif st.session_state.current_page == "dokumen_materi":
    if st.button("⬅️ KEMBALI KE DASHBOARD UTAMA", use_container_width=True, key="back_doc"): st.session_state.current_page = "menu_utama"; st.rerun()
    render_sidebar_status(active_keys, client, mode="dokumen")
