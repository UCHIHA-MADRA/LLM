from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline

def create_qa_chain(llm_pipeline, vectorstore):
    llm = HuggingFacePipeline(pipeline=llm_pipeline)
    retriever = vectorstore.as_retriever()
    return RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)
