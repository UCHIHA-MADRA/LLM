import gradio as gr
from llm.load_llm import load_llm
from rag.vectorstore import get_vectorstore
from rag.rag_chain import create_qa_chain
from auth.github_oauth import app as oauth_app, session
from flask import jsonify
import threading

# Load components once
llm_pipeline = load_llm()
vectorstore = get_vectorstore()
qa_chain = create_qa_chain(llm_pipeline, vectorstore)

def get_user_display_name():
    user_info = session.get('user_info', {})
    return user_info.get('name') or user_info.get('login') or 'Anonymous'

def chat_interface(query):
    # Check if user is authenticated
    if 'oauth_token' not in session:
        return "Please login with GitHub first"
    
    user_name = get_user_display_name()
    response = qa_chain.run(query)
    return f"[{user_name}] {response}"

# Create Gradio interface with user info
def create_interface():
    with gr.Blocks(
        title="🧠 RAG Chatbot",
        css="* {font-family: -apple-system, BlinkMacSystemFont, sans-serif !important;}"
    ) as iface:
        gr.Markdown("# AI Code Assistant")
        gr.Markdown("Please login with GitHub at: http://localhost:3000/login")
        
        # Chat interface
        with gr.Row():
            query_input = gr.Textbox(label="Ask a question")
            submit_btn = gr.Button("Submit")
        
        output_text = gr.Textbox(label="Response")
        
        # Handle submit button
        submit_btn.click(
            fn=chat_interface,
            inputs=query_input,
            outputs=output_text
        )
        
    return iface

# Create and launch the interface
def run_gradio():
    iface = create_interface()
    iface.launch(
        server_port=7861,
        share=False,
        prevent_thread_lock=True,
        show_error=True
    )

if __name__ == "__main__":
    # Start Gradio in a separate thread
    import threading
    threading.Thread(target=run_gradio, daemon=True).start()
    
    # Start Flask app
    oauth_app.run(port=3000, debug=False)
# Remove this line below - it's causing the port conflict
# iface.launch()
