import trafilatura

def extract_clean_text(url):
    downloaded = trafilatura.fetch_url(url)
    return trafilatura.extract(downloaded)
