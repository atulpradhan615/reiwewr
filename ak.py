import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import logging
import io
import ast

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the Gemini model
model = ChatGoogleGenerativeAI(model='gemini-2.0-flash', max_tokens=2000)

# Define the prompt template for code review
prompt = PromptTemplate(
    template="""
        You are an advanced software engineer and code reviewer. Carefully check the following code for errors, suggest the correct code, and explain the required changes. Think step by step and be thorough in your review.\n\nCode:\n{code}\n\nResponse:
    """,
    input_variables=['code']
)

# Output parser
parser = StrOutputParser()

def get_code_stats(code):
    """Return statistics about the code: lines, functions, classes."""
    try:
        tree = ast.parse(code)
        num_functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
        num_classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
    except Exception:
        num_functions = num_classes = 0
    num_lines = len(code.splitlines())
    return num_lines, num_functions, num_classes

def display_code_stats(code):
    num_lines, num_functions, num_classes = get_code_stats(code)
    st.markdown(f"**Lines:** {num_lines}  |  **Functions:** {num_functions}  |  **Classes:** {num_classes}")

def get_code_from_upload(uploaded_file):
    if uploaded_file is not None:
        try:
            code = uploaded_file.read().decode('utf-8')
            return code
        except Exception as e:
            st.error(f"Error reading file: {e}")
    return ""

def review_code(code):
    chain = prompt | model | parser
    try:
        with st.spinner("Reviewing your code with Gemini..."):
            result = chain.invoke({'code': code})
        return result
    except Exception as e:
        logging.error(f"Error during LLM review: {e}")
        return f"Error during review: {e}"

def main():
    st.set_page_config(page_title="Advanced Code Reviewer", layout="wide")
    st.sidebar.title("Instructions")
    st.sidebar.info("""
    - Paste your code or upload a file.
    - Click 'Review Code' to get an AI-powered review.
    - See code stats, syntax highlighting, and detailed suggestions.
    """)
    st.sidebar.markdown("---")
    st.sidebar.write("Built with :blue[Streamlit] and :orange[Gemini]")

    st.title(" Advanced AI Code Reviewer")
    st.write("Paste your code below or upload a file for review.")

    uploaded_file = st.file_uploader("Upload a code file (optional)", type=["py", "js", "java", "cpp", "c", "ts", "go", "rb", "php"])
    code_from_file = get_code_from_upload(uploaded_file)

    usercode = st.text_area("Paste your code here:", value=code_from_file, height=300)

    if usercode:
        st.markdown("### Code Preview")
        st.code(usercode, language="python")
        display_code_stats(usercode)

    if st.button('Review Code'):
        if not usercode.strip():
            st.warning("Please paste your code or upload a file before submitting.")
        else:
            review = review_code(usercode)
            st.markdown("---")
            st.subheader(":mag: Review Result")
            st.write(review)
            st.markdown("---")
            st.info("If you found this helpful, consider giving feedback!")

if __name__ == "__main__":
    main()
