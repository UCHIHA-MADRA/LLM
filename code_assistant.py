import gradio as gr
from llm.code_llm import CodeLLM
from rag.vectorstore import get_vectorstore
from rag.rag_chain import create_qa_chain
import ast
import subprocess
import sys

class CodeAssistant:
    def __init__(self):
        self.code_llm = CodeLLM()
        self.vectorstore = get_vectorstore()
        
    def write_code(self, description, language="python"):
        """Generate code based on description"""
        prompt = f"# Write {language} code for: {description}\n# Code:\n"
        generated_code = self.code_llm.generate_code(prompt)
        
        # Analyze code quality
        quality = self.code_llm.analyze_code_quality(generated_code)
        
        return {
            "code": generated_code,
            "quality_score": quality["quality_score"],
            "bug_probability": quality["bug_probability"]
        }
    
    def debug_code(self, code, error_message=""):
        """Debug and fix code"""
        # First, analyze the code
        quality = self.code_llm.analyze_code_quality(code)
        
        if quality["bug_probability"] > 0.5:
            # Generate fix
            fixed_code = self.code_llm.debug_code(code, error_message)
            explanation = self.code_llm.explain_code(fixed_code)
            
            return {
                "fixed_code": fixed_code,
                "explanation": explanation,
                "original_bug_probability": quality["bug_probability"]
            }
        else:
            return {
                "message": "Code appears to be correct",
                "bug_probability": quality["bug_probability"]
            }
    
    def execute_code(self, code, language="python"):
        """Safely execute code and return results"""
        if language == "python":
            try:
                # Basic syntax check
                ast.parse(code)
                
                # Execute in subprocess for safety
                result = subprocess.run(
                    [sys.executable, "-c", code],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    return {"output": result.stdout, "error": None}
                else:
                    return {"output": None, "error": result.stderr}
                    
            except SyntaxError as e:
                return {"output": None, "error": f"Syntax Error: {str(e)}"}
            except subprocess.TimeoutExpired:
                return {"output": None, "error": "Code execution timed out"}
            except Exception as e:
                return {"output": None, "error": str(e)}
        else:
            return {"output": None, "error": f"Execution not supported for {language}"}
    
    def code_review(self, code):
        """Provide code review and suggestions"""
        quality = self.code_llm.analyze_code_quality(code)
        explanation = self.code_llm.explain_code(code)
        
        review = {
            "quality_score": quality["quality_score"],
            "bug_probability": quality["bug_probability"],
            "explanation": explanation,
            "suggestions": []
        }
        
        # Add specific suggestions based on analysis
        if quality["bug_probability"] > 0.3:
            review["suggestions"].append("Consider reviewing for potential bugs")
        if quality["quality_score"] < 0.7:
            review["suggestions"].append("Code quality could be improved")
            
        return review

# Create Gradio interface
def create_code_interface():
    assistant = CodeAssistant()
    
    def write_code_interface(description, language):
        result = assistant.write_code(description, language)
        return result["code"], f"Quality: {result['quality_score']:.2f}, Bug Risk: {result['bug_probability']:.2f}"
    
    def debug_code_interface(code, error_msg):
        result = assistant.debug_code(code, error_msg)
        if "fixed_code" in result:
            return result["fixed_code"], result["explanation"]
        else:
            return code, result["message"]
    
    def execute_code_interface(code):
        result = assistant.execute_code(code)
        if result["error"]:
            return f"Error: {result['error']}"
        else:
            return f"Output: {result['output']}"
    
    with gr.Blocks(title="🤖 AI Code Assistant") as interface:
        gr.Markdown("# AI Code Writing and Debugging Assistant")
        
        with gr.Tab("Write Code"):
            with gr.Row():
                description_input = gr.Textbox(label="Describe what you want to code", lines=3)
                language_dropdown = gr.Dropdown(["python", "javascript", "java", "cpp"], value="python", label="Language")
            
            write_btn = gr.Button("Generate Code")
            
            with gr.Row():
                generated_code = gr.Code(label="Generated Code", language="python")
                quality_info = gr.Textbox(label="Quality Analysis")
            
            write_btn.click(write_code_interface, [description_input, language_dropdown], [generated_code, quality_info])
        
        with gr.Tab("Debug Code"):
            with gr.Row():
                buggy_code = gr.Code(label="Code to Debug", language="python", lines=10)
                error_input = gr.Textbox(label="Error Message (optional)", lines=3)
            
            debug_btn = gr.Button("Debug Code")
            
            with gr.Row():
                fixed_code = gr.Code(label="Fixed Code", language="python")
                debug_explanation = gr.Textbox(label="Explanation", lines=5)
            
            debug_btn.click(debug_code_interface, [buggy_code, error_input], [fixed_code, debug_explanation])
        
        with gr.Tab("Execute Code"):
            exec_code = gr.Code(label="Code to Execute", language="python", lines=10)
            exec_btn = gr.Button("Execute")
            exec_output = gr.Textbox(label="Output", lines=10)
            
            exec_btn.click(execute_code_interface, exec_code, exec_output)
    
    return interface

if __name__ == "__main__":
    interface = create_code_interface()
    interface.launch()