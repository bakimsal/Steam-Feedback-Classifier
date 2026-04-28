import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px

# src klasöründeki modülleri içeri aktarabilmek için ana yolu ekliyoruz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipeline.predict import predict_review

st.set_page_config(
    page_title="Steam Review Classifier",
    page_icon="🎮",
    layout="centered"
)

# ==== SOL SIDEBAR ====
with st.sidebar:
    st.title("Steam Classifier")
    st.markdown("---")
    
    model_name = st.selectbox(
        "Kullanılacak Modeli Seçin:",
        ("SVM", "CatBoost", "BerTURK")
    )
    
    st.info("Bu sistem, Steam yorumlarını analiz etmek için eğitilmiş makine öğrenmesi modellerini kullanır.")

# ==== ANA ALAN ====
st.title("🎮 Steam Review Classifier")
st.markdown("Steam kullanıcı yorumlarını otomatik olarak **Bug**, **Feature Request** veya **Neutral** olarak sınıflandıran yapay zeka destekli analiz sistemi.")

st.markdown("---")

# Kullanıcı Girdisi
text_input = st.text_area("Analiz edilecek Steam yorumunu girin:", height=150, placeholder="Örn: Oyun sürekli çöküyor, lütfen düzeltin...")

if st.button("🔍 Analiz Et", type="primary", use_container_width=True):
    if text_input.strip() == "":
        st.warning("⚠️ Lütfen analiz etmek için bir yorum girin.")
    else:
        # Gerçek tahmin fonksiyonunu çağır
        result = predict_review(text_input, model_name)
        
        if result.get("error"):
            st.error(f"❌ **Hata:** {result['error']}")
        else:
            label = result['label']
            confidence = result['confidence']
            model_used = result['model']
            
            st.markdown("### Sonuç:")
            
            # Etikete göre görselleştirme
            if label == "Bug":
                st.error(f"🐞 **{label}**")
            elif label == "Feature Request":
                st.info(f"✨ **{label}**")
            else:
                # Neutral için gri arkaplan ve emojili uyarı simülasyonu
                st.markdown(
                    f"""
                    <div style="background-color: #f0f2f6; padding: 16px; border-radius: 8px; color: #31333f; margin-bottom: 1rem;">
                        ⚪ <b>{label}</b>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
            # Sonuçları Metric olarak göster
            col1, col2 = st.columns(2)
            col1.metric("Güven (Confidence)", f"%{int(confidence * 100)}")
            col2.metric("Kullanılan Model", model_used)

st.markdown("---")


# ==== PLACEHOLDER GRAFİK BÖLÜMÜ ====
st.subheader("Model Karşılaştırması (Demo)")

# Dummy F1 Skorları Verisi
dummy_performance = pd.DataFrame({
    'Model': ['SVM', 'CatBoost', 'BerTURK'],
    'F1 Skoru': [0.82, 0.85, 0.91]
})

# Plotly ile Bar Chart
fig = px.bar(
    dummy_performance, 
    x='Model', 
    y='F1 Skoru',
    text='F1 Skoru',
    color='Model',
    color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c']
)
fig.update_traces(texttemplate='%{text}', textposition='outside')
fig.update_layout(
    showlegend=False, 
    margin=dict(t=30, l=0, r=0, b=0), 
    height=350,
    yaxis=dict(range=[0, 1.0])
)
st.plotly_chart(fig, use_container_width=True)

st.caption("Bu değerler demo amaçlıdır.")

st.markdown("---")

# ==== NASIL ÇALIŞIR ====
st.subheader("Nasıl Çalışır?")
st.markdown("""
1. Kullanıcı yorum girer
2. Sistem yorumu analiz eder (dummy pipeline)
3. Model sonucu üretir
""")
