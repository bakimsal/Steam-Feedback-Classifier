# Steam-Feedback-Classifier

This project classifies Turkish Steam user reviews into:

- Bug Report
- Feature Request
- Neutral

## Structure

- `src/` → core code (data, models, nlp, pipeline)
- `data/` → datasets
- `artifacts/` → trained models and vectorizers
- `app/` → Streamlit UI interface

## Goal

Compare SVM, CatBoost and BerTURK models.

## How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/bakimsal/Steam-Feedback-Classifier.git
   cd Steam-Feedback-Classifier
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit application:**
   ```bash
   streamlit run app/app.py
   ```

*Note: Ensure trained models are placed in the `artifacts/` folder before making predictions.*