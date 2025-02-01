# D:\Adnan_project\TradingBot\sentiment_analyzer.py
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import torch
# Device configuration
device = "cuda" if torch.cuda.is_available() else "cpu"

# Advanced Sentiment Analysis Model
sentiment_model_name = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
sentiment_analysis = pipeline("sentiment-analysis", model=sentiment_model_name, device=device)

# Named Entity Recognition Model
ner_model_name = "dbmdz/bert-large-cased-finetuned-conll03-english"
tokenizer = AutoTokenizer.from_pretrained(ner_model_name)
ner_model = AutoModelForTokenClassification.from_pretrained(ner_model_name)
ner_model.to(device)
ner = pipeline("ner", model=ner_model, tokenizer=tokenizer, device=device)

def get_ai_response(prompt):
    try:
        result = sentiment_analysis(prompt)
        return result[0]['label']
    except Exception as e:
        print(f"Error in Sentiment Analysis: {e}")
        return None

def get_named_entities(text):
    try:
        ner_results = ner(text)
        return ner_results
    except Exception as e:
        print(f"Error in NER: {e}")
        return None
