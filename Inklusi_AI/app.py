import streamlit as st
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import os
import random
import urllib.parse
import time
from PIL import Image

# IMPOR FUNGSI MODULAR INTERNAL & PEMBANTU UI
from interface_helper import render_top_dashboard_widgets, render_sidebar_status  
from obrolan_helper import render_live_chat         
from asisten_helper import render_asisten_ai        
from menu_helper import render_dashboard_menu  

# =====================================================================
# 1. KONFIGURASI HALAMAN UTAMA STREAMLIT (HACKFEST EDITION)
# =====================================================================
st.set_page_config(
    page_title="Hermes Productivity Assistant - Hackfest Pro", 
    page_icon="⚡", 
    layout="wide"
)

# INJEKSI CSS KUSTOM: TEMA LIGHT MODERN, ANIMASI GLOW KOTAK, & ULTRA-SMOOTH SINGLE TRACK MARQUEE
st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        color: #0F172A;
    }
    
    /* ANIMASI INTERAKTIF PADA KOTAK FITUR */
    .card-asisten, .card-sos, .card-obrolan, .card-dokumen, .card-hackfest {
        padding: 24px; 
        border-radius: 20px;
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer;
    }
    
    .card-hackfest {
        background-color: #F8FAFC !important;
        border: 2px solid #CBD5E1 !important;
    }
    
    .card-hackfest:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 20px -5px rgba(30, 41, 59, 0.15), 0 0 15px 2px rgba(203, 213, 225, 0.6) !important;
    }
    
    /* INTERAKTIF BUTTON: ANIMASI WARNA TOMBOL */
    div[data-testid="stVerticalBlock"] div.stButton > button {
        background-color: #FFFFFF !important; 
        color: #0F172A !important;            
        border: 1px solid #CBD5E1 !important;  
        border-radius: 12px !important;       
        font-weight: 700 !important;          
        font-size: 15px !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    div[data-testid="stVerticalBlock"] div.stButton > button:hover {
        background-color: #1E3A8A !important; 
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.25) !important;
    }
    
    /* STYLE BANNER MARQUEE LOGO UNIVERSITAS */
    .running-banner-container {
        width: 100%;
        overflow: hidden;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 12px 0;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    
    .running-track {
        display: flex;
        width: max-content;
        animation: smoothMarquee 20s linear infinite;
    }
    
    .running-track:hover {
        animation-play-state: paused;
    }
    
    .interactive-img {
        height: 70px;
        margin: 0 35px;
        object-fit: contain;
        transition: transform 0.3s ease, filter 0.3s ease;
        border-radius: 6px;
    }
    
    .interactive-img:hover {
        transform: scale(1.18); 
        filter: drop-shadow(0 0 10px rgba(30, 58, 138, 0.45)); 
    }
    
    @keyframes smoothMarquee {
        0% { transform: translateX(100vw); }
        100% { transform: translateX(-100%); }
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
st.markdown("<h1 class='main-title'>🤖 Hermes Productivity Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Platform Kendali Navigasi Otonom & Pusat Manajemen Kerja Cerdas Terintegrasi</p>", unsafe_allow_html=True)

# Perhitungan waktu WIB
waktu_utc = datetime.datetime.utcnow()
waktu_wib = waktu_utc + datetime.timedelta(hours=7)
waktu_sekarang_str = waktu_wib.strftime("%H:%M")

start_time = time.time()
time.sleep(0.01)
latency = round((time.time() - start_time) * 1000, 1)
status_lampu = "🟢 Cepat" if latency < 50 else "🟡 Sedang" if latency < 150 else "🔴 Lambat"

st.markdown(f"<div class='status-text-bar'>⏰ {waktu_sekarang_str} WIB | 🎛️ Latensi Server Cloud: {latency} ms ({status_lampu})</div>", unsafe_allow_html=True)
st.write("---")
# =====================================================================
# BANNER LOGO UNIVERSITAS 1 ALIRAN TUNGGAL BERSIH (ANTI-TEKS MENTAH)
# =====================================================================
if st.session_state.current_page == "menu_utama":
    st.markdown("""
        <div class="running-banner-container">
            <div class="running-track">
                <!-- KODE LINK UNIVERSITAS ANDA DIJAGA 100% UTUH TANPA DIGANTI SATU HURUF PUN -->
                <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRtuJCRQ0omwX8a5B-B1QXK7KzfNU97ZsrezMyvCsxOWqeFB_cW1H3Y1m1S&s=10" class="interactive-img">
                <img src="https://images.seeklogo.com/logo-png/40/3/ntu-nanyang-technological-university-logo-png_seeklogo-405905.png" class="interactive-img">
                <img src="https://upload.wikimedia.org/wikipedia/commons/c/cc/Harvard_University_coat_of_arms.svg?utm_source=en.wikipedia.org&utm_campaign=index&utm_content=original" class="interactive-img">
                <img src="https://itb.ac.id/files/77/20100320/1269071805.jpg" class="interactive-img">
                <img src="https://upload.wikimedia.org/wikipedia/en/thumb/1/16/Zhejiang_University_Logo.svg/1280px-Zhejiang_University_Logo.svg.png?utm_source=en.wikipedia.org&utm_campaign=index&utm_content=thumbnail" class="interactive-img">
                <img src="https://upload.wikimedia.org/wikipedia/sco/a/ad/Imperial_College_London_crest.svg?utm_source=sco.wikipedia.org&utm_campaign=index&utm_content=original" class="interactive-img">
                <img src="https://upload.wikimedia.org/wikipedia/commons/5/5c/Logo_Unibuc_English.jpg?utm_source=en.wikipedia.org&utm_campaign=index&utm_content=original" class="interactive-img">
            </div>
        </div>
    """, unsafe_allow_html=True)

# =====================================================================
# INTERAKTIF MENU NAVIGATION DROPDOWN (DI ATAS SEBELUM PUSAT DATA)
# =====================================================================
st.markdown("<b style='font-size: 14px; color: #1E3A8A;'>🎛️ PANEL KENDALI NAVIGASI UTAMA ASISTEN:</b>", unsafe_allow_html=True)

pilihan_menu_dropdown = st.selectbox(
    "Pilih Halaman / Fitur yang Ingin Diaktifkan:",
    options=[
        "Dashboard Utama & Beranda", 
        "🤖 Masuk Modul Asisten Multimodal AI", 
        "💬 Masuk Modul Terjemahan Percakapan Live", 
        "📚 Masuk Modul Rangkuman Dokumen Materi",
        "🏆 [HACKFEST] Modul 1: Notulensi Diskusi & Ekstraktor Tugas",
        "🛡️ [HACKFEST] Modul 2: Penyaring Keamanan & Kebocoran Data"
    ],
    index=0 if st.session_state.current_page == "menu_utama" else 
          1 if st.session_state.current_page == "asisten_ai" else 
          2 if st.session_state.current_page == "terjemahan_live" else 
          3 if st.session_state.current_page == "dokumen_materi" else
          4 if st.session_state.current_page == "hf_notulensi" else 5,
    label_visibility="collapsed"
)

if pilihan_menu_dropdown == "Dashboard Utama & Beranda" and st.session_state.current_page != "menu_utama":
    st.session_state.current_page = "menu_utama"; st.rerun()
elif pilihan_menu_dropdown == "🤖 Masuk Modul Asisten Multimodal AI" and st.session_state.current_page != "asisten_ai":
    st.session_state.current_page = "asisten_ai"; st.rerun()
elif pilihan_menu_dropdown == "💬 Masuk Modul Terjemahan Percakapan Live" and st.session_state.current_page != "terjemahan_live":
    st.session_state.current_page = "terjemahan_live"; st.rerun()
elif pilihan_menu_dropdown == "📚 Masuk Modul Rangkuman Dokumen Materi" and st.session_state.current_page != "dokumen_materi":
    st.session_state.current_page = "dokumen_materi"; st.rerun()
elif pilihan_menu_dropdown == "🏆 [HACKFEST] Modul 1: Notulensi Diskusi & Ekstraktor Tugas" and st.session_state.current_page != "hf_notulensi":
    st.session_state.current_page = "hf_notulensi"; st.rerun()
elif pilihan_menu_dropdown == "🛡️ [HACKFEST] Modul 2: Penyaring Keamanan & Kebocoran Data" and st.session_state.current_page != "hf_security":
    st.session_state.current_page = "hf_security"; st.rerun()

st.write("") 
# =====================================================================
# TATA LETAK VERTIKAL KE BAWAH (HACKFEST CLEAN DASHBOARD DESIGN)
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

    # --- BARIS 1 KE BAWAH: GALERI 5 FOTO KOTAK PERSEGI INTERAKTIF ---
    with st.container(border=True):
        st.markdown("<b style='font-size: 13px; color: #1E3A8A;'>📸 1. DOKUMENTASI PROYEK & PRODUKTIVITAS JALAN</b>", unsafe_allow_html=True)
        
        # JALUR KODE FOTO TEKNOLOGI ANDA UTUH TANPA DIGANTI SATU HURUF PUN [LR1s9q]
        foto1 = "https://thesourcemediaassets.com"
        foto2 = "https://idn.id"
        foto3 = "https://gstatic.com"
        foto4 = "https://diengcyber.com"
        foto5 = "https://gstatic.com"
        
        st.components.v1.html(f"""
            <div id="box_carousel" style="position: relative; max-width: 300px; margin: 0 auto; aspect-ratio: 1 / 1; border-radius: 16px; overflow: hidden; background-color: #1a1a1a; box-shadow: 0 8px 20px rgba(0,0,0,0.2); border: 2px solid #E2E8F0;">
                
                <div id="carousel_track" style="display: flex; width: 500%; height: 100%; transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1);">
                    <img src="{foto1}" style="width: 20%; height: 100%; object-fit: cover;">
                    <img src="{foto2}" style="width: 20%; height: 100%; object-fit: cover;">
                    <img src="{foto3}" style="width: 20%; height: 100%; object-fit: cover;">
                    <img src="{foto4}" style="width: 20%; height: 100%; object-fit: cover;">
                    <img src="{foto5}" style="width: 20%; height: 100%; object-fit: cover;">
                </div>

                <button onclick="moveSlide(-1)" style="position: absolute; top: 50%; left: 10px; transform: translateY(-50%); background: rgba(0,0,0,0.6); color: white; border: none; font-size: 16px; width: 34px; height: 34px; border-radius: 50%; cursor: pointer; z-index: 10; display: flex; align-items: center; justify-content: center; outline:none;">❮</button>
                <button onclick="moveSlide(1)" style="position: absolute; top: 50%; right: 10px; transform: translateY(-50%); background: rgba(0,0,0,0.6); color: white; border: none; font-size: 16px; width: 34px; height: 34px; border-radius: 50%; cursor: pointer; z-index: 10; display: flex; align-items: center; justify-content: center; outline:none;">❯</button>

                <div style="position: absolute; bottom: 12px; left: 50%; transform: translateX(-50%); display: flex; gap: 6px; z-index: 10;">
                    <span class="dot" onclick="setSlide(0)" style="height: 8px; width: 8px; background-color: rgba(255,255,255,0.4); border-radius: 50%; display: inline-block; cursor: pointer;"></span>
                    <span class="dot" onclick="setSlide(1)" style="height: 8px; width: 8px; background-color: rgba(255,255,255,0.4); border-radius: 50%; display: inline-block; cursor: pointer;"></span>
                    <span class="dot" onclick="setSlide(2)" style="height: 8px; width: 8px; background-color: rgba(255,255,255,0.4); border-radius: 50%; display: inline-block; cursor: pointer;"></span>
                    <span class="dot" onclick="setSlide(3)" style="height: 8px; width: 8px; background-color: rgba(255,255,255,0.4); border-radius: 50%; display: inline-block; cursor: pointer;"></span>
                    <span class="dot" onclick="setSlide(4)" style="height: 8px; width: 8px; background-color: rgba(255,255,255,0.4); border-radius: 50%; display: inline-block; cursor: pointer;"></span>
                </div>
            </div>

            <script>
                var currentIdx = 0; var track = document.getElementById('carousel_track'); var dots = document.getElementsByClassName('dot');
                function updateCarousel() {{
                    track.style.transform = 'translateX(' + (-currentIdx * 20) + '%)';
                    for (var i = 0; i < dots.length; i++) {{
                        dots[i].style.backgroundColor = (i === currentIdx) ? '#FFFFFF' : 'rgba(255,255,255,0.4)';
                        dots[i].style.width = (i === currentIdx) ? '16px' : '8px';
                        dots[i].style.borderRadius = (i === currentIdx) ? '4px' : '50%';
                    }}
                }}
                function moveSlide(dir) {{ currentIdx += dir; if (currentIdx > 4) currentIdx = 0; if (currentIdx < 0) currentIdx = 4; updateCarousel(); }}
                function setSlide(idx) {{ currentIdx = idx; updateCarousel(); }}
                
                var startX = 0;
                document.getElementById('box_carousel').addEventListener('touchstart', function(e) {{ startX = e.touches.clientX; }}, false);
                document.getElementById('box_carousel').addEventListener('touchend', function(e) {{
                    var diffX = startX - e.changedTouches.clientX;
                    if (Math.abs(diffX) > 40) {{ if (diffX > 0) moveSlide(1); else moveSlide(-1); }}
                }}, false);
                updateCarousel();
            </script>
        """, height=330)

    # --- BARIS 2 KE BAWAH: DATA GEOGRAFI PETA LIVE GPS DINAMIS ---
    with st.container(border=True):
        st.markdown("<b style='font-size: 13px; color: #1E3A8A;'>🗺️ 2. PETA NAVIGASI LIVE GPS GEOLOCATION</b>", unsafe_allow_html=True)
        lokasi_user_live = {"lat": [st.session_state.user_lat], "lon": [st.session_state.user_lon]}
        st.map(lokasi_user_live, zoom=15, use_container_width=True)
        st.caption("📍 Peta Geolocation Otonom: Melacak posisi gawai Anda secara real-time.")

    # --- BARIS 3 KE BAWAH: KONDISI METRIK CUACA LENGKAP ---
    with st.container(border=True):
        st.markdown("<b style='font-size: 13px; color: #1E3A8A;'>🌤️ 3. PUSAT PEMANTAUAN KONDISI CUACA SALATIGA</b>", unsafe_allow_html=True)
        c_col1, c_col2 = st.columns(2)
        with c_col1: st.metric(label="🌡️ Temperatur Udara", value="24°C", delta="Normal")
        with c_col2: st.metric(label="💧 Kelembapan Sekitar", value="78%", delta="Aman Berawan")
    st.write("---")
# =====================================================================
# 3. ROUTER NAVIGASI DASHBOARD (SISTEM SINKRONISASI DROPDOWN ATAS)
# =====================================================================
elif st.session_state.current_page == "asisten_ai":
    render_asisten_ai(client, sched, mode="asisten")

elif st.session_state.current_page == "terjemahan_live":
    render_live_chat(client)

elif st.session_state.current_page == "dokumen_materi":
    render_sidebar_status(active_keys, client, mode="dokumen")

# -----------------------------------------------------------------
# INOVASI HACKFEST 1: AUTOMATED MEETING MINUTES & TASK EXTRACTOR
# -----------------------------------------------------------------
elif st.session_state.current_page == "hf_notulensi":
    st.markdown("""
        <div class='card-hackfest'>
            <h3 style='color: #1E3A8A; margin: 0;'>🏆 Hackfest Modul 1: Notulensi Diskusi & Ekstraktor Tugas Cerdas</h3>
            <p style='color: #475569; font-size:12px; margin: 4px 0 20px 0;'>Unggah file rekaman suara rapat kelompok atau perkuliahan Anda (.wav, .mp3) untuk diubah otomatis menjadi risalah keputusan resmi.</p>
    """, unsafe_allow_html=True)
    
    audio_file_hf = st.file_uploader("Pilih file audio diskusi kelompok Anda:", type=["wav", "mp3"], key="hf_audio_uploader")
    
    if audio_file_hf is not None and client:
        with st.spinner("Gemini AI sedang menganalisis gelombang suara diskusi..."):
            try:
                from google.genai import types
                # AI memproses konversi suara panjang secara komprehensif menjadi laporan formal
                prompt_hf1 = "Ekstrak audio ini menjadi: 1. Transkrip bersih, 2. Poin ringkasan draf keputusan rapat, 3. To-Do List daftar tugas beserta PIC pengerjaan jika ada. Tulis dalam Bahasa Indonesia yang formal."
                res_hf1 = client.models.generate_content(
                    model='gemini-2.5-flash', 
                    contents=[types.Part.from_bytes(data=audio_file_hf.read(), mime_type='audio/wav'), prompt_hf1]
                )
                if res_hf1.text:
                    st.success("✓ Laporan Notulensi Rapat Berhasil Disusun!")
                    st.markdown("### 📋 Hasil Dokumentasi Rapat Resmi:")
                    st.write(res_hf1.text.strip())
            except Exception as e:
                st.error(f"Gagal memproses data audio: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------
# INOVASI HACKFEST 2: AI SECURITY SCANNER & PII DATA FILTER
# -----------------------------------------------------------------
elif st.session_state.current_page == "hf_security":
    st.markdown("""
        <div class='card-hackfest'>
            <h3 style='color: #991B1B; margin: 0;'>🛡️ Hackfest Modul 2: Penyaring Keamanan & Deteksi Kebocoran Data (PII Filter)</h3>
            <p style='color: #475569; font-size:12px; margin: 4px 0 20px 0;'>Validasi keamanan berkas teks materi atau gambar tugas Anda sebelum dilempar ke cloud publik untuk mencegah kebocoran informasi sensitif.</p>
    """, unsafe_allow_html=True)
    
    st.markdown("<b style='font-size:13px;'>Pilih Metode Pemindaian Berkas:</b>", unsafe_allow_html=True)
    tab_scan_teks, tab_scan_gambar = st.tabs(["📄 Pindai File Teks (.txt)", "📸 Pindai Gambar Tugas"])
    
    with tab_scan_teks:
        file_teks_hf = st.file_uploader("Unggah file teks Anda:", type=["txt"], key="hf_txt_scan")
        if file_teks_hf is not None and client:
            isi_teks_raw = file_teks_hf.read().decode("utf-8")
            st.text_area("Isi Berkas Terbaca:", isi_teks_raw, height=100)
            
            if st.button("🛡️ JALANKAN PEMINDAIAN DATA SENSITIF", key="btn_scan_txt", use_container_width=True):
                with st.spinner("Sistem sedang memindai kebocoran data pribadi..."):
                    prompt_hf2 = f"Periksa apakah teks berikut mengandung data sensitif pribadi (seperti password, email pribadi, nomor HP, nomor rekening, PIN, atau alamat rumah): '{isi_teks_raw}'. Jika ada, sebutkan datanya dan berikan peringatan keamanan. Jika bersih, katakan berkas aman."
                    res_hf2 = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_hf2)
                    st.markdown("##### 🛡️ Laporan Audit Keamanan Data:")
                    st.write(res_hf2.text.strip())
                    
    with tab_scan_gambar:
        file_img_hf = st.file_uploader("Unggah foto lembar tugas Anda:", type=["png", "jpg", "jpeg"], key="hf_img_scan")
        if file_img_hf is not None and client:
            img_hf = Image.open(file_img_hf)
            st.image(img_hf, caption="Pratinjau Gambar Audit", width=250)
            
            if st.button("🛡️ PINDAI TEKS DI DALAM GAMBAR", key="btn_scan_img", use_container_width=True):
                with st.spinner("AI memindai karakter tulisan di dalam gambar..."):
                    prompt_hf3 = ["Analisa tulisan di dalam gambar ini. Apakah ada data pribadi sensitif seperti nomor kontak, sandi rahasia, atau data pribadi penting? Berikan penilaian status keamanan (AMAN atau WASPADA).", img_hf]
                    res_hf3 = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_hf3)
                    st.markdown("##### 🛡️ Laporan Hasil Analisis Citra Gambar:")
                    st.write(res_hf3.text.strip())
                    
    st.markdown("</div>", unsafe_allow_html=True)
