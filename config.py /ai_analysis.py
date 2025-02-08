from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# Model AI untuk analisis keamanan smart contract
MODEL_NAME = "microsoft/codebert-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

def analyze_smart_contract(code: str):
    """ Analisis AI untuk smart contract """
    inputs = tokenizer(code, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    risk_score = probabilities[0][1].item()  # Probabilitas adanya celah keamanan
    return "Aman" if risk_score < 0.5 else "Berisiko"
