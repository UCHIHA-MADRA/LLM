import requests
import os
import json
from pathlib import Path
from config import GITHUB_API_TOKEN, SUPPORTED_LANGUAGES, TRAINING_DATA_DIR

class GitHubCodeScraper:
    def __init__(self):
        self.headers = {"Authorization": f"token {GITHUB_API_TOKEN}"}
        self.base_url = "https://api.github.com"
        
    def search_repositories(self, language, min_stars=10, max_repos=100):
        """Search for popular repositories in a specific language"""
        query = f"language:{language} stars:>{min_stars}"
        url = f"{self.base_url}/search/repositories"
        params = {"q": query, "sort": "stars", "per_page": max_repos}
        
        response = requests.get(url, headers=self.headers, params=params)
        return response.json().get("items", [])
    
    def get_repository_files(self, repo_full_name, language):
        """Get code files from a repository"""
        url = f"{self.base_url}/repos/{repo_full_name}/git/trees/main"
        params = {"recursive": "1"}
        
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code != 200:
            return []
            
        tree = response.json().get("tree", [])
        code_files = []
        
        for item in tree:
            if item["type"] == "blob" and self._is_code_file(item["path"], language):
                code_files.append(item)
                
        return code_files
    
    def download_file_content(self, repo_full_name, file_path):
        """Download content of a specific file"""
        url = f"{self.base_url}/repos/{repo_full_name}/contents/{file_path}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            content = response.json().get("content", "")
            import base64
            return base64.b64decode(content).decode('utf-8', errors='ignore')
        return None
    
    def _is_code_file(self, file_path, language):
        """Check if file is a code file for the specified language"""
        extensions = {
            "python": [".py"],
            "javascript": [".js", ".jsx", ".ts", ".tsx"],
            "java": [".java"],
            "cpp": [".cpp", ".cc", ".cxx", ".h", ".hpp"],
            "go": [".go"],
            "rust": [".rs"]
        }
        
        file_ext = Path(file_path).suffix.lower()
        return file_ext in extensions.get(language, [])
    
    def scrape_and_save(self, language, max_repos=100):
        """Scrape repositories and save code samples"""
        repos = self.search_repositories(language, max_repos=max_repos)
        
        save_dir = Path(TRAINING_DATA_DIR) / "github" / language
        save_dir.mkdir(parents=True, exist_ok=True)
        
        code_samples = []
        
        for repo in repos:
            print(f"Processing {repo['full_name']}...")
            files = self.get_repository_files(repo["full_name"], language)
            
            for file_info in files[:10]:  # Limit files per repo
                content = self.download_file_content(repo["full_name"], file_info["path"])
                if content and len(content) < 10000:  # Skip very large files
                    code_samples.append({
                        "repo": repo["full_name"],
                        "file_path": file_info["path"],
                        "content": content,
                        "language": language,
                        "stars": repo["stargazers_count"]
                    })
        
        # Save to JSON
        output_file = save_dir / f"{language}_samples.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(code_samples, f, indent=2, ensure_ascii=False)
            
        return code_samples