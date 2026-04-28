"""
BerTURK Model Eğitimi - Steam Feedback Classifier
Bu script, IDE içinde doğrudan çalıştırılabilir
"""

print("="*70)
print(" BERTURK MODEL EĞİTİMİ - STEAM FEEDBACK CLASSIFIER")
print("="*70)

# 1️ Gerekli Kütüphaneleri Yükle
print("\n[1/9] Gerekli kütüphaneler yükleniyor...")

import torch
print(f"✓ GPU mevcut: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  GPU: {torch.cuda.get_device_name(0)}")

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset, DatasetDict
from pathlib import Path

print("✓ Kütüphaneler yüklendi!")

# 2️⃣ Veriyi Yükle ve Hazırla
print("\n[2/9] Veri yükleniyor...")

# Proje kök dizinini bul
project_root = Path(__file__).resolve().parents[2]
data_path = project_root / 'data' / 'processed' / 'balanced_reviews.csv'

print(f"📁 Veri dosyası: {data_path}")
print(f"✅ Dosya mevcut: {data_path.exists()}")

df = pd.read_csv(data_path)
print(f"\nToplam yorum: {len(df)}")
print("\nEtiket dağılımı:")
print(df['label'].value_counts())

# Etiketleri sayısal değerlere çevir
label2id = {
    'bug(hata/hile)': 0,
    'feature request(istek)': 1,
    'nötr/ çöp': 2
}

id2label = {v: k for k, v in label2id.items()}
df['labels'] = df['label'].map(label2id)

print("\nEtiket eşleştirmesi:")
for label, id in label2id.items():
    print(f"  {label} → {id}")

# Train-test split
train_df, test_df = train_test_split(
    df[['review_text', 'labels']],
    test_size=0.2,
    random_state=42,
    stratify=df['labels']
)

print(f"\n✓ Train seti: {len(train_df)} örnek")
print(f"✓ Test seti: {len(test_df)} örnek")

# Hugging Face Dataset formatına çevir
train_dataset = Dataset.from_pandas(train_df)
test_dataset = Dataset.from_pandas(test_df)

dataset = DatasetDict({
    'train': train_dataset,
    'test': test_dataset
})

print("✓ Dataset hazırlandı!")

# 3️⃣ BerTURK Tokenizer ve Model Yükle
print("\n[3/9] BerTURK modeli yükleniyor...")

model_name = "dbmdz/bert-base-turkish-cased"

print(f"  Model: {model_name}")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=3,
    id2label=id2label,
    label2id=label2id
)

print("✓ BerTURK model ve tokenizer hazır!")

# Tokenization
def tokenize_function(examples):
    return tokenizer(
        examples['review_text'],
        truncation=True,
        padding='max_length',
        max_length=128
    )

print("\nDataset tokenize ediliyor...")
tokenized_datasets = dataset.map(
    tokenize_function,
    batched=True,
    remove_columns=['review_text']
)

print(f"✓ Tokenization tamamlandı!")
print(f"  Train: {len(tokenized_datasets['train'])} örnek")
print(f"  Test: {len(tokenized_datasets['test'])} örnek")

# 4️ Eğitim Parametrelerini Ayarla
print("\n[4/9] Eğitim parametreleri ayarlanıyor...")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = accuracy_score(labels, predictions)
    return {'accuracy': accuracy}

training_args = TrainingArguments(
    output_dir='./berturk_results',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    warmup_steps=100,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=50,
    eval_strategy='epoch',
    save_strategy='epoch',
    load_best_model_at_end=True,
    metric_for_best_model='accuracy',
    learning_rate=2e-5,
    fp16=torch.cuda.is_available(),
    report_to='none',
)

print("✓ Training arguments hazırlandı!")
print(f"  Batch size: 16 (train), 32 (eval)")
print(f"  Epochs: 3")
print(f"  Learning rate: 2e-5")
print(f"  Mixed precision (FP16): {torch.cuda.is_available()}")

# 5️⃣ Modeli Eğit
print("\n[5/9] Model eğitimi başlıyor...")
print("="*70)
print(" Bu işlem GPU ile ~5-10 dakika sürebilir...")
print(" CPU ile ~20-30 dakika sürebilir...")
print("="*70)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets['train'],
    eval_dataset=tokenized_datasets['test'],
    compute_metrics=compute_metrics,
)

train_result = trainer.train()

print("\n✓ EĞİTİM TAMAMLANDI!")

# 6️⃣ Modeli Değerlendir
print("\n[6/9] Model değerlendiriliyor...")

eval_results = trainer.evaluate()

print("\n" + "="*70)
print(" BERTURK MODEL SONUÇLARI")
print("="*70)
print(f"Accuracy: {eval_results['eval_accuracy']:.4f} (%{eval_results['eval_accuracy']*100:.2f})")
print("="*70)

# Detaylı classification report
predictions = trainer.predict(tokenized_datasets['test'])
y_pred = np.argmax(predictions.predictions, axis=-1)
y_true = predictions.label_ids

print("\nClassification Report:")
print(classification_report(
    y_true, 
    y_pred, 
    target_names=[id2label[i] for i in range(3)]
))

print("\nConfusion Matrix:")
print(confusion_matrix(y_true, y_pred))

# 7️⃣ Modeli Kaydet
print("\n[7/9] Model kaydediliyor...")

model_output_dir = project_root / 'models' / 'berturk_model'
model.save_pretrained(str(model_output_dir))
tokenizer.save_pretrained(str(model_output_dir))

print(f"✓ BerTURK modeli kaydedildi: {model_output_dir}")

# 8️⃣ Model Karşılaştırması
print("\n[8/9] Model karşılaştırması...")

comparison_df = pd.DataFrame({
    'Model': ['SVM', 'CatBoost', 'BerTURK'],
    'Accuracy': ['92.86%', '94.87%', f"{eval_results['eval_accuracy']*100:.2f}%"],
    'Eğitim Süresi': ['3.39 sn', '33.36 sn', 'GPU: ~5-10 dk'],
    'Model Tipi': ['Geleneksel ML', 'Gradient Boosting', 'Deep Learning (Transformer)'],
})

print("\n" + "="*70)
print(" MODEL KARŞILAŞTIRMASI")
print("="*70)
print(comparison_df.to_string(index=False))
print("="*70)

berturk_acc = eval_results['eval_accuracy'] * 100
if berturk_acc > 94.87:
    print(f"\n KAZANAN: BERTURK ({berturk_acc:.2f}%)")
elif berturk_acc > 92.86:
    print(f"\n🥈 İKİNCİ: BERTURK ({berturk_acc:.2f}%)")
    print(" KAZANAN: CatBoost (94.87%)")
else:
    print(f"\n🥉 ÜÇÜNCİ: BERTURK ({berturk_acc:.2f}%)")
    print("🥇 KAZANAN: CatBoost (94.87%)")
    print("🥈 İKİNCİ: SVM (92.86%)")

# 9️ Örnek Tahminler
print("\n[9/9] Örnek tahminler yapılıyor...")

from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model=str(model_output_dir),
    tokenizer=str(model_output_dir)
)

test_reviews = [
    "Oyun sürekli çöküyor, FPS 10'a düşüyor, optimizasyon berbat",
    "Türkiye sunucusu eklerseniz çok sevinirim",
    "Güzel oyun arkadaşlarla oynayınca daha eğlenceli",
    "Hileciler yüzünden oyun oynanmıyor, anti-cheat sistemi geliştirmelisiniz",
    "Silah skinsleri için yeni bir market sistemi olmalı"
]

print("\n" + "="*70)
print(" BERTURK ÖRNEK TAHMİNLER")
print("="*70)
for review in test_reviews:
    result = classifier(review)[0]
    print(f"\nYorum: {review}")
    print(f"Tahmin: {result['label']} (Güven: {result['score']:.2%})")
print("="*70)

print("\n✅ TÜM İŞLEMLER TAMAMLANDI!")
