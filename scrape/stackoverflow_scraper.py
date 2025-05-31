import requests
import json
from pathlib import Path
from config import STACKOVERFLOW_API_KEY, TRAINING_DATA_DIR

class StackOverflowScraper:
    def __init__(self):
        self.base_url = "https://api.stackexchange.com/2.3"
        self.key = STACKOVERFLOW_API_KEY
        
    def get_questions_by_tag(self, tag, max_questions=1000):
        """Get questions for a specific programming language tag"""
        url = f"{self.base_url}/questions"
        params = {
            "order": "desc",
            "sort": "votes",
            "tagged": tag,
            "site": "stackoverflow",
            "filter": "withbody",
            "pagesize": 100,
            "key": self.key
        }
        
        questions = []
        page = 1
        
        while len(questions) < max_questions:
            params["page"] = page
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                break
                
            data = response.json()
            if not data.get("items"):
                break
                
            questions.extend(data["items"])
            page += 1
            
            if data.get("has_more") is False:
                break
                
        return questions[:max_questions]
    
    def get_answers_for_question(self, question_id):
        """Get answers for a specific question"""
        url = f"{self.base_url}/questions/{question_id}/answers"
        params = {
            "order": "desc",
            "sort": "votes",
            "site": "stackoverflow",
            "filter": "withbody",
            "key": self.key
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("items", [])
        return []
    
    def scrape_qa_pairs(self, language_tag, max_questions=1000):
        """Scrape Q&A pairs for a programming language"""
        questions = self.get_questions_by_tag(language_tag, max_questions)
        
        qa_pairs = []
        
        for question in questions:
            if question.get("accepted_answer_id"):
                answers = self.get_answers_for_question(question["question_id"])
                accepted_answer = next(
                    (a for a in answers if a["answer_id"] == question["accepted_answer_id"]),
                    None
                )
                
                if accepted_answer:
                    qa_pairs.append({
                        "question_title": question["title"],
                        "question_body": question["body"],
                        "answer_body": accepted_answer["body"],
                        "question_score": question["score"],
                        "answer_score": accepted_answer["score"],
                        "tags": question["tags"],
                        "language": language_tag
                    })
        
        # Save to JSON
        save_dir = Path(TRAINING_DATA_DIR) / "stackoverflow"
        save_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = save_dir / f"{language_tag}_qa.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(qa_pairs, f, indent=2, ensure_ascii=False)
            
        return qa_pairs