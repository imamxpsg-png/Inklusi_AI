import streamlit as st

def render_sos_menu():
    """
    Modul 4: Navigasi Jalan Pintas Kilat Instan Sekali Klik.
    Seluruh sistem pemutar suara audio dibuang total agar peluncuran 
    halaman tab baru berjalan super kilat, bersih, dan bebas hambatan.
    """
    st.markdown("""
        <div class='card-sos'>
            <h3 style='color: #991B1B; margin: 0 0 4px 0;'>🚀 Modul 4: Navigasi Jalan Pintas Kilat</h3>
            <p style='color: #374151; font-size:12px; margin: 0 0 16px 0;'>Tekan salah satu tombol kotak besar di bawah ini untuk membuka tab aplikasi website baru secara instan hulu.</p>
    """, unsafe_allow_html=True)
    
    # Membuat pembagian baris kolom tombol yang besar dan responsif di layar ponsel
    col_nav1, col_nav2 = st.columns(2)
    
    with col_nav1:
        # 1. Jalan Pintas YouTube Instan
        st.link_button("📺 BUKA YOUTUBE", "https://youtube.com", use_container_width=True)
            
        st.write("") # Memberikan jarak spasi vertikal antar tombol
        
        # 2. Jalan Pintas WhatsApp Web Instan
        st.link_button("🟢 BUKA WHATSAPP WEB", "https://whatsapp.com", use_container_width=True)
            
    with col_nav2:
        # 3. Jalan Pintas Google Search Instan
        st.link_button("🔍 BUKA GOOGLE SEARCH", "https://google.com", use_container_width=True)
            
        st.write("")
        
        # 4. Jalan Pintas Wikipedia Indonesia Instan
        st.link_button("📚 BUKA WIKIPEDIA", "https://wikipedia.org", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True) # Penutup bingkai merah menyatu sempurna
