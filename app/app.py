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
    st.markdown("### ⚙️ Sistem Bilgisi")
    
    st.info("🤖 **Ensemble (Toplu) Analiz:**\nYorumunuz arka planda CatBoost, SVM ve BerTURK motorlarına aynı anda gönderilir. Modellerin hepsi kendi analizini yapar ve sonuçlar anlık olarak karşılaştırılır.")
    
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
        with st.spinner("Tüm yapay sinir ağları metni eşzamanlı olarak işliyor..."):
            
            results = []
            models_list = ["CatBoost", "SVM", "BerTURK"]
            
            for m in models_list:
                res = predict_review(text_input, m)
                results.append({
                    'Model': m,
                    'Label': res['label'] if not res.get('error') else "Hata",
                    'Confidence': (res['confidence'] * 100) if res.get('confidence') is not None else 0.0,
                    'Error': res.get('error')
                })
            
            res_df = pd.DataFrame(results)
            
            st.write("")
            st.markdown("### 🔍 Model Değerlendirmeleri")
            col1, col2, col3 = st.columns(3)
            
            # Kart 1: CatBoost
            cat_res = res_df[res_df['Model'] == 'CatBoost'].iloc[0]
            with col1:
                st.markdown(f"""
                <div style="background: rgba(17,34,64,0.4); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255, 107, 107, 0.3); text-align: center;">
                    <h4 style="color: #ff6b6b; margin-bottom: 10px; font-weight: 600;">CatBoost</h4>
                    <div style="font-size: 1.2rem; font-weight: bold; color: white; margin-bottom: 5px;">{cat_res['Label']}</div>
                    <div style="color: #a6adc8; font-size: 0.9rem;">Güven Skoru: %{cat_res['Confidence']:.1f}</div>
                </div>
                """, unsafe_allow_html=True)
                
            # Kart 2: SVM
            svm_res = res_df[res_df['Model'] == 'SVM'].iloc[0]
            with col2:
                st.markdown(f"""
                <div style="background: rgba(17,34,64,0.4); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(0, 201, 255, 0.3); text-align: center;">
                    <h4 style="color: #00C9FF; margin-bottom: 10px; font-weight: 600;">SVM</h4>
                    <div style="font-size: 1.2rem; font-weight: bold; color: white; margin-bottom: 5px;">{svm_res['Label']}</div>
                    <div style="color: #a6adc8; font-size: 0.9rem;">Güven Skoru: %{svm_res['Confidence']:.1f}</div>
                </div>
                """, unsafe_allow_html=True)
                
            # Kart 3: BerTURK
            ber_res = res_df[res_df['Model'] == 'BerTURK'].iloc[0]
            with col3:
                st.markdown(f"""
                <div style="background: rgba(17,34,64,0.4); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(146, 254, 157, 0.3); text-align: center;">
                    <h4 style="color: #92FE9D; margin-bottom: 10px; font-weight: 600;">BerTURK</h4>
                    <div style="font-size: 1.2rem; font-weight: bold; color: white; margin-bottom: 5px;">{ber_res['Label']}</div>
                    <div style="color: #a6adc8; font-size: 0.9rem;">Güven Skoru: %{ber_res['Confidence']:.1f}</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.write("")
            st.markdown("### 📊 Kararlılık Grafiği")
            
            # Grafik (Dikey Sütun Grafiği)
            fig = px.bar(
                res_df, 
                x='Model', 
                y='Confidence',
                color='Model',
                text=res_df['Confidence'].apply(lambda x: f"%{x:.1f}"),
                color_discrete_map={
                    'SVM': 'rgba(0, 201, 255, 0.8)',
                    'BerTURK': 'rgba(146, 254, 157, 0.8)',
                    'CatBoost': 'rgba(255, 107, 107, 0.8)'
                }
            )
            
            fig.update_traces(
                textposition='outside', 
                textfont=dict(color='#cdd6f4', size=14, family="Outfit"),
                marker_line_width=0,
                width=0.5
            )
            
            fig.update_layout(
                showlegend=False, 
                margin=dict(t=30, l=0, r=0, b=0), 
                height=300,
                yaxis=dict(range=[0, 115], title="Güven Skoru (%)", gridcolor="rgba(255,255,255,0.05)", zeroline=False),
                xaxis=dict(title="", tickfont=dict(size=14, weight="bold")),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Outfit", color="#cdd6f4")
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.write("")
            
            # En yüksek güven skorunu bul ve Ortak Kararı En Alta Koy
            best_model_idx = res_df['Confidence'].idxmax()
            best_model_row = res_df.loc[best_model_idx]
            
            final_label = best_model_row['Label']
            best_model_name = best_model_row['Model']
            
            badge_html = ""
            if final_label == "Bug":
                badge_html = f'<div class="badge-Bug">🐞 Hata Bildirimi (Bug)</div>'
            elif final_label == "Feature Request":
                badge_html = f'<div class="badge-Feature-Request">✨ Özellik İsteği</div>'
            else:
                badge_html = f'<div class="badge-Neutral">💬 Nötr / Genel Yorum</div>'
                
            st.markdown(f"""
            <div class="result-container" style="margin-top: 1rem;">
                <h4 style="color: #a6adc8; margin-bottom: 1.5rem; font-weight: 300; letter-spacing: 2px; text-transform: uppercase; font-size: 0.9rem;">Ortak Karar (En Güçlü Tahmin: {best_model_name})</h4>
                {badge_html}
            </div>
            """, unsafe_allow_html=True)
