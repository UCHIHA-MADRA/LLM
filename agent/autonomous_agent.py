from langchain.agents import initialize_agent, Tool
from langchain.tools import SerpAPIWrapper
from langchain.llms import HuggingFacePipeline
from llm.load_llm import load_llm

search = SerpAPIWrapper()  # Set SERPAPI_API_KEY in your .env
tools = [Tool(name="Search", func=search.run, description="Searches the web")]

llm_pipeline = load_llm()
llm = HuggingFacePipeline(pipeline=llm_pipeline)

agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

# Example
print(agent.run("What is the latest news on LLaMA 3?"))
