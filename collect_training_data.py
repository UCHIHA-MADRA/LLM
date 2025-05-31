from scrape.github_scraper import GitHubCodeScraper
from scrape.stackoverflow_scraper import StackOverflowScraper
from config import SUPPORTED_LANGUAGES, MAX_REPOS_TO_SCRAPE, MAX_SO_QUESTIONS
import asyncio

def collect_all_data():
    """Collect training data from GitHub and StackOverflow"""
    github_scraper = GitHubCodeScraper()
    so_scraper = StackOverflowScraper()
    
    print("Starting data collection...")
    
    for language in SUPPORTED_LANGUAGES:
        print(f"\nCollecting data for {language}...")
        
        # Collect GitHub code samples
        print(f"Scraping GitHub repositories for {language}...")
        github_samples = github_scraper.scrape_and_save(language, MAX_REPOS_TO_SCRAPE)
        print(f"Collected {len(github_samples)} code samples from GitHub")
        
        # Collect StackOverflow Q&A
        print(f"Scraping StackOverflow for {language}...")
        so_samples = so_scraper.scrape_qa_pairs(language, MAX_SO_QUESTIONS)
        print(f"Collected {len(so_samples)} Q&A pairs from StackOverflow")
    
    print("\nData collection completed!")

if __name__ == "__main__":
    collect_all_data()