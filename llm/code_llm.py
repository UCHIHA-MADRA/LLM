from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from transformers import RobertaTokenizer, RobertaForSequenceClassification
import torch
from config import CODE_MODEL_NAME

class CodeLLM:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.load_models()
        
    def load_models(self):
        """Load code generation and analysis models"""
        # Code generation model
        self.code_tokenizer = AutoTokenizer.from_pretrained(CODE_MODEL_NAME)
        self.code_model = AutoModelForCausalLM.from_pretrained(
            CODE_MODEL_NAME, 
            device_map="auto",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        
        # Code analysis model (CodeBERT)
        self.analysis_tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")
        self.analysis_model = RobertaForSequenceClassification.from_pretrained(
            "microsoft/codebert-base",
            num_labels=2  # For bug detection
        )
        
    def generate_code(self, prompt, max_length=512, temperature=0.7):
        """Generate code based on prompt"""
        inputs = self.code_tokenizer.encode(prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.code_model.generate(
                inputs,
                max_length=max_length,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.code_tokenizer.eos_token_id
            )
            
        generated_code = self.code_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_code[len(prompt):].strip()
    
    def analyze_code_quality(self, code):
        """Analyze code for potential bugs or issues"""
        inputs = self.analysis_tokenizer(
            code, 
            return_tensors="pt", 
            truncation=True, 
            max_length=512
        )
        
        with torch.no_grad():
            outputs = self.analysis_model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)
            
        # Return probability of code having bugs
        return {
            "bug_probability": probabilities[0][1].item(),
            "quality_score": probabilities[0][0].item()
        }
    
    def debug_code(self, buggy_code, error_message=""):
        """Suggest fixes for buggy code"""
        debug_prompt = f"""# Debug this code:
# Error: {error_message}
# Buggy code:
{buggy_code}

# Fixed code:
"""
        
        fixed_code = self.generate_code(debug_prompt, max_length=1024)
        return fixed_code
    
    def explain_code(self, code):
        """Generate explanation for code"""
        explain_prompt = f"""# Explain this code:
{code}

# Explanation:
"""
        
        explanation = self.generate_code(explain_prompt, max_length=512)
        return explanation