import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
from pathlib import Path
from config import TRAINING_DATA_DIR, CODE_MODEL_NAME, BATCH_SIZE, LEARNING_RATE

class CodeDataset(Dataset):
    def __init__(self, data_files, tokenizer, max_length=512):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.examples = []
        
        for file_path in data_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.examples.extend(self._process_data(data))
    
    def _process_data(self, data):
        """Process different types of training data"""
        examples = []
        
        for item in data:
            if 'content' in item:  # GitHub code
                examples.append(item['content'])
            elif 'question_body' in item:  # StackOverflow Q&A
                qa_text = f"Question: {item['question_title']}\n{item['question_body']}\nAnswer: {item['answer_body']}"
                examples.append(qa_text)
                
        return examples
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        text = self.examples[idx]
        encoding = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt"
        )
        
        return {
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "labels": encoding["input_ids"].flatten()
        }

class CodeModelTrainer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(CODE_MODEL_NAME)
        self.model = AutoModelForCausalLM.from_pretrained(CODE_MODEL_NAME)
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def prepare_dataset(self):
        """Prepare training dataset from scraped data"""
        data_dir = Path(TRAINING_DATA_DIR)
        
        # Collect all training files
        github_files = list((data_dir / "github").rglob("*.json"))
        stackoverflow_files = list((data_dir / "stackoverflow").rglob("*.json"))
        
        all_files = github_files + stackoverflow_files
        
        # Split into train/validation
        split_idx = int(0.8 * len(all_files))
        train_files = all_files[:split_idx]
        val_files = all_files[split_idx:]
        
        train_dataset = CodeDataset(train_files, self.tokenizer)
        val_dataset = CodeDataset(val_files, self.tokenizer)
        
        return train_dataset, val_dataset
    
    def train(self, output_dir="./code_model_finetuned"):
        """Train the code model"""
        train_dataset, val_dataset = self.prepare_dataset()
        
        training_args = TrainingArguments(
            output_dir=output_dir,
            overwrite_output_dir=True,
            num_train_epochs=3,
            per_device_train_batch_size=BATCH_SIZE,
            per_device_eval_batch_size=BATCH_SIZE,
            learning_rate=LEARNING_RATE,
            warmup_steps=500,
            logging_steps=100,
            save_steps=1000,
            evaluation_strategy="steps",
            eval_steps=500,
            save_total_limit=2,
            prediction_loss_only=True,
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
        )
        
        trainer.train()
        trainer.save_model()
        
        return trainer