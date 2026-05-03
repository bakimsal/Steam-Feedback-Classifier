import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import time

# src klasöründeki modülleri içeri aktarabilmek için ana yolu ekliyoruz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipeline.predict import predict_review

st.set_page_config(
    page_title="Steam Feedback AI",
    page_icon="🎮",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (Premium Dark Mode) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

html, body, [class*="css"]  {
    font-family: 'Outfit', sans-serif;
}

/* Gradient Başlık */
.gradient-text {
    background: linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 3.2rem;
    margin-bottom: 0;
    padding-bottom: 0;
    line-height: 1.2;
}

.sub-text {
    color: #a6adc8;
    font-size: 1.15rem;
    font-weight: 300;
    margin-top: 0.2rem;
    margin-bottom: 2rem;
}

/* Sonuç Kartı ve Animasyonu */
.result-container {
    animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    background: linear-gradient(145deg, rgba(30, 30, 46, 0.7), rgba(17, 17, 27, 0.7));
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 2.5rem;
    border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: 0 15px 35px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.1);
    margin-top: 1rem;
    text-align: center;
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(30px) scale(0.95); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}

/* Badge Stilleri */
.badge-Bug {
    background: linear-gradient(135deg, rgba(243, 139, 168, 0.2), rgba(243, 139, 168, 0.05));
    color: #f38ba8;
    border: 1px solid rgba(243, 139, 168, 0.4);
    padding: 0.8rem 2rem;
    border-radius: 50px;
    font-weight: 600;
    font-size: 1.5rem;
    display: inline-flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 0 20px rgba(243, 139, 168, 0.15);
}

.badge-Feature-Request {
    background: linear-gradient(135deg, rgba(166, 227, 161, 0.2), rgba(166, 227, 161, 0.05));
    color: #a6e3a1;
    border: 1px solid rgba(166, 227, 161, 0.4);
    padding: 0.8rem 2rem;
    border-radius: 50px;
    font-weight: 600;
    font-size: 1.5rem;
    display: inline-flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 0 20px rgba(166, 227, 161, 0.15);
}

.badge-Neutral {
    background: linear-gradient(135deg, rgba(180, 190, 254, 0.2), rgba(180, 190, 254, 0.05));
    color: #b4befe;
    border: 1px solid rgba(180, 190, 254, 0.4);
    padding: 0.8rem 2rem;
    border-radius: 50px;
    font-weight: 600;
    font-size: 1.5rem;
    display: inline-flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 0 20px rgba(180, 190, 254, 0.15);
}

/* St Butonları ve Inputları Hedefleyen İnce Ayarlar */
div.stButton > button:first-child {
    border-radius: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
    transition: all 0.3s ease !important;
}

div.stButton > button:first-child:hover {
    transform: translateY(-2px);
}

.stTextArea textarea {
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.1);
    background: rgba(0,0,0,0.2) !important;
    font-size: 1.1rem;
}
.stTextArea textarea:focus {
    border-color: #00C9FF;
    box-shadow: 0 0 0 1px #00C9FF;
}

/* Metrik Kartları */
[data-testid="stMetricValue"] {
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #00C9FF, #92FE9D);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
[data-testid="stMetricLabel"] {
    font-size: 1rem !important;
    color: #a6adc8 !important;
}
</style>
""", unsafe_allow_html=True)


# ==== SIDEBAR ====
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3204/3204905.png", width=60)
    st.markdown("### ⚙️ Yapay Zeka Ayarları")
    
    model_name = st.selectbox(
        "Aktif Model Motoru:",
        ("CatBoost", "SVM", "BerTURK"),
        index=0,
        help="Sınıflandırma işlemi için arka planda çalışacak makine öğrenmesi motorunu seçin."
    )
    
    st.markdown("---")
    st.markdown("### 📊 Model Doğrulukları")
    st.progress(0.948, text="CatBoost (%94.8)")
    st.progress(0.945, text="BerTURK (%94.5)")
    st.progress(0.928, text="SVM (%92.8)")
    
    st.markdown("---")
    st.caption("Steam Feedback Analizi için Geliştirildi.")

# ==== HEADER ====
st.markdown('<h1 class="gradient-text">Steam Feedback AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Oyun Yorumları İçin Gelişmiş Doğal Dil İşleme Analizi</p>', unsafe_allow_html=True)

# ==== INPUT SECTION ====
text_input = st.text_area(
    "Kullanıcı Yorumu:", 
    height=140, 
    placeholder="Buraya bir Steam yorumu yazın veya yapıştırın.\nÖrn: 'Oyun sürekli çöküyor, acilen düzeltilmeli...' veya 'Lütfen daha fazla harita ekleyin.'",
    label_visibility="collapsed"
)

col_btn1, col_btn2 = st.columns([1, 2])
with col_btn1:
    submit = st.button("✨ Yapay Zeka ile Analiz Et", type="primary", use_container_width=True)

if submit:
    if text_input.strip() == "":
        st.warning("⚠️ Lütfen analiz edilecek bir metin girin.")
    else:
        # Loading efekti
        with st.spinner("Yapay sinir ağları metni işliyor..."):
            time.sleep(0.5) # Çok kısa bekleme (Animasyon hissi için)
            result = predict_review(text_input, model_name)
        
        if result.get('error'):
            st.error(f"⚠️ {result['error']}")
        else:
            label = result['label']
            confidence = result['confidence']
            model_used = result['model']
            
            # Badge Seçimi
            badge_html = ""
            if label == "Bug":
                badge_html = f'<div class="badge-Bug">🐞 Hata Bildirimi (Bug)</div>'
            elif label == "Feature Request":
                badge_html = f'<div class="badge-Feature-Request">✨ Özellik İsteği</div>'
            else:
                badge_html = f'<div class="badge-Neutral">💬 Nötr / Genel Yorum</div>'
            
            # Animasyonlu Sonuç Alanı
            st.markdown(f"""
            <div class="result-container">
                <h4 style="color: #a6adc8; margin-bottom: 1.5rem; font-weight: 300; letter-spacing: 2px; text-transform: uppercase; font-size: 0.9rem;">Analiz Sonucu</h4>
                {badge_html}
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            st.write("")
            
            # Alt Metrikler
            col1, col2, col3 = st.columns(3)
            conf_percent = f"%{confidence * 100:.1f}" if confidence is not None else "N/A"
            
            with col1:
                st.metric(label="Güven Skoru", value=conf_percent, delta="Yüksek Kararlılık" if confidence and confidence > 0.8 else None)
            with col2:
                st.metric(label="Kullanılan Motor", value=model_used)
            with col3:
                st.metric(label="Kelime Sayısı", value=f"{len(text_input.split())}")

st.markdown("---")

# ==== CHART SECTION ====
st.markdown("### 📈 Motor Başarı Karşılaştırması")

performance_df = pd.DataFrame({
    'Model': ['SVM', 'BerTURK', 'CatBoost'],
    'Accuracy': [92.86, 94.50, 94.87]
})

fig = px.bar(
    performance_df, 
    x='Accuracy', 
    y='Model',
    orientation='h',
    text='Accuracy',
    color='Model',
    color_discrete_map={
        'SVM': 'rgba(0, 201, 255, 0.7)',
        'BerTURK': 'rgba(146, 254, 157, 0.7)',
        'CatBoost': 'rgba(255, 107, 107, 0.7)'
    }
)

fig.update_traces(
    texttemplate='<b>%{text}%</b>', 
    textposition='inside', 
    insidetextfont=dict(color='white', size=14),
    marker_line_width=0
)

fig.update_layout(
    showlegend=False, 
    margin=dict(t=10, l=0, r=0, b=0), 
    height=220,
    xaxis=dict(range=[85, 100], title="", gridcolor="rgba(255,255,255,0.05)", zeroline=False),
    yaxis=dict(title="", tickfont=dict(size=14, weight="bold")),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Outfit", color="#cdd6f4")
)

st.plotly_chart(fig, use_container_width=True)
