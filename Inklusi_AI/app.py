import streamlit as st
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import os
import random
import urllib.parse

# IMPOR FUNGSI MODULAR INTERNAL & PEMBANTU UI
from interface_helper import render_sidebar_status  
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

# KOORDINAT DEFAULT (Akan otomatis ter-update jika GPS HP aktif)
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

# Perhitungan waktu WIB (+7 Jam dari UTC Server Cloud)
waktu_utc = datetime.datetime.utcnow()
waktu_wib = waktu_utc + datetime.timedelta(hours=7)
waktu_sekarang_str = waktu_wib.strftime("%H:%M")

st.markdown(f"<div class='status-text-bar'>⏰ {waktu_sekarang_str} WIB | 🌤️ Status: Sistem Online Siaga</div>", unsafe_allow_html=True)
st.write("---")
# =====================================================================
# TATA LETAK BARIS MEDIA PENUH (SISTEM SATU KOLOM LUAS)
# =====================================================================
if st.session_state.current_page == "menu_utama":
    
    # --- FIX AUTOMATIC GPS: Jembatan Iframe Tersembunyi untuk Melacak Posisi HP Real-time ---
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

    # Menangkap kirim data sinyal GPS dari JavaScript HTML5 di atas
    html_event_gps = st.session_state.get("py_bridge_receiver", "") # Penyelarasan tangkapan internal
    if html_event_gps and "GPS_UPDATE:" in html_event_gps:
        try:
            koordinat_raw = html_event_gps.replace("GPS_UPDATE:", "").split(",")
            st.session_state.user_lat = float(koordinat_raw[0])
            st.session_state.user_lon = float(koordinat_raw[1])
        except:
            pass

    with st.container(border=True):
        st.markdown("<b style='font-size: 13px; color: #1E3A8A;'>📺 PUSAT MEDIA INTERAKTIF & MULTI-ALARM DAFTAR</b>", unsafe_allow_html=True)
        
        tab_galeri, tab_alarm, tab_maps, tab_cuaca = st.tabs(["📸 Galeri Foto", "⏰ Multi-Alarm Kustom", "🗺️ Peta Live GPS", "🌤️ Kondisi Cuaca"])
        
        with tab_galeri:
            foto1_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTdKjzrg_RSda0TzIKe9EA3yGkgFP4vlJ_YZX5K1EunpA&s"  
            foto2_url = "https://upload.wikimedia.org/wikipedia/commons/5/5c/Logo_Unibuc_English.jpg?utm_source=en.wikipedia.org&utm_campaign=index&utm_content=original"  
            foto3_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcReSt7Vu4eRW5IiBuyOCKW9cgvuCM6gxEBxo-bMmIokxR38a-D-jPyV4lU&s=10"  
            foto4_url = "https://ziqihuangg.github.io/images/NTU_logo.png"  
            
            st.components.v1.html(f"""
                <div id="photo_carousel" style="position: relative; width: 100%; height: 230px; border-radius: 12px; overflow: hidden; background-color: #1a1a1a; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
                    <div id="carousel_track" style="display: flex; width: 300%; height: 100%; transition: transform 0.4s ease-in-out;">
                        <img src="{foto1_url}" style="width: 33.333%; height: 100%; object-fit: cover;">
                        <img src="{foto2_url}" style="width: 33.333%; height: 100%; object-fit: cover;">
                        <img src="{foto3_url}" style="width: 33.333%; height: 100%; object-fit: cover;">
                        <img src="{foto4_url}" style="width: 33.333%; height: 100%; object-fit: cover;">
                    </div>
                    <button onclick="moveSlide(-1)" style="position: absolute; top: 50%; left: 15px; transform: translateY(-50%); background: rgba(0,0,0,0.6); color: white; border: none; font-size: 20px; padding: 10px 14px; border-radius: 50%; cursor: pointer; z-index: 10;">❮</button>
                    <button onclick="moveSlide(1)" style="position: absolute; top: 50%; right: 15px; transform: translateY(-50%); background: rgba(0,0,0,0.6); color: white; border: none; font-size: 20px; padding: 10px 14px; border-radius: 50%; cursor: pointer; z-index: 10;">❯</button>
                </div>
                <script>
                    var currentIdx = 0; var track = document.getElementById('carousel_track');
                    function moveSlide(dir) {{ currentIdx += dir; if(currentIdx>2) currentIdx=0; if(currentIdx<0) currentIdx=2; track.style.transform='translateX('+(-currentIdx*33.333)+'%)'; }}
                </script>
            """, height=240)
            
        with tab_alarm:
            st.markdown("<b style='font-size:14px; color:#1E3A8A;'>➕ Tambah Jadwal Alarm Baru:</b>", unsafe_allow_html=True)
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                jam_pilihan = st.selectbox("Pilih Jam:", [f"{i:02d}" for i in range(24)], index=waktu_wib.hour, key="sb_jam_multi")
            with col_a2:
                menit_pilihan = st.selectbox("Pilih Menit:", [f"{i:02d}" for i in range(60)], index=waktu_wib.minute, key="sb_menit_multi")
                
            teks_suara_kustom = st.text_input(
                "Ketik Kalimat Perintah Ucapan Google untuk Alarm Ini:", 
                placeholder="Contoh: Ayo bangun bos, waktunya minum obat siang.",
                key="ti_teks_multi"
            )
            
            if st.button("➕ MASUKKAN KE DAFTAR ALARM SAYA", use_container_width=True):
                waktu_baru = f"{jam_pilihan}:{menit_pilihan}"
                teks_fix = teks_suara_kustom if teks_suara_kustom else "Waktu alarm pengingat Anda telah tiba."
                st.session_state.list_alarm.append({"waktu": waktu_baru, "teks": teks_fix})
                st.success(f"✓ Berhasil menambahkan alarm baru untuk pukul {waktu_baru} WIB!")
                st.rerun()
                
            if st.session_state.list_alarm:
                st.write("---")
                st.markdown("<b style='font-size:13px; color:#475569;'>📋 Riwayat Daftar Alarm Anda Saat Ini:</b>", unsafe_allow_html=True)
                for idx, item in enumerate(st.session_state.list_alarm):
                    col_t1, col_t2, col_t3 = st.columns()
                    with col_t1: st.markdown(f"⏰ **{item['waktu']} WIB**")
                    with col_t2: st.markdown(f"🗣️ *\"{item['teks']}\"*")
                    with col_t3:
                        if st.button("❌ Hapus", key=f"del_alarm_{idx}"):
                            st.session_state.list_alarm.pop(idx)
                            st.rerun()
            
            for item in st.session_state.list_alarm:
                if waktu_sekarang_str == item['waktu']:
                    identitas_kunci = f"{item['waktu']}_{item['teks']}"
                    if st.session_state.alarm_terpicu.get(identitas_kunci) != waktu_sekarang_str:
                        st.markdown(f"<div style='background-color:#FFF5F5; padding:16px; border-radius:14px; border:2px solid #FEB2B2; margin-top:10px;'><h3>⏰ [ALARM BERBUNYI]</h3><p>🗣️ Google: \"<b>{item['teks']}</b>\"</p></div>", unsafe_allow_html=True)
                        import modules as mod
                        st.audio(mod.text_to_speech(item['teks'], f"alarm_{item['waktu']}.mp3"), autoplay=True)
                        st.session_state.alarm_terpicu[identitas_kunci] = waktu_sekarang_str
        
        with tab_maps:
            # FIX UTAMA MAPS: Menggunakan koordinat dinamis user_lat dan user_lon hasil tracking GPS HP asli
            lokasi_user_live = {"lat": [st.session_state.user_lat], "lon": [st.session_state.user_lon]}
            st.map(lokasi_user_live, zoom=15, use_container_width=True)
            st.caption("📍 Peta Interaktif GPS: Menyesuaikan lokasi real-time gawai Anda saat ini.")
            
        with tab_cuaca:
            c_col1, c_col2 = st.columns(2)
            with c_col1: st.metric(label="🌡️ Temperatur Udara Sekitar", value="24°C", delta="Normal")
            with c_col2: st.metric(label="💧 Kelembapan Sekitar", value="78%", delta="Aman")
            
    st.write("---")

# =====================================================================
# 3. ROUTER NAVIGASI DASHBOARD
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
