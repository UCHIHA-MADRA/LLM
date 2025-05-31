def update_knowledge_base(urls: list):
    new_texts = [extract_clean_text(url) for url in urls]
    vectorstore.add_texts(new_texts)
    vectorstore.persist()
