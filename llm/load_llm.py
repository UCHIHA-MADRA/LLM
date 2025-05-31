from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from config import MODEL_NAME

def load_llm():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, device_map="auto")
    return pipeline("text-generation", model=model, tokenizer=tokenizer)
