import streamlit as st
import os
import PyPDF2
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Initialize Hugging Face client
# It's good practice to specify a model.
# Mixtral is a good general-purpose instruction-following model.
# You might need to adjust based on what's available or your preference.
MODEL_NAME = "mistralai/Mixtral-8x7B-Instruct-v0.1" # Example model
# If the above model is too large or causes issues, try a smaller one like:
# MODEL_NAME = "HuggingFaceH4/zephyr-7b-beta"
# MODEL_NAME = "google/flan-t5-large" # (if available for text-generation via InferenceClient)

if not hf_token:
    st.error("HUGGINGFACEHUB_API_TOKEN not found. Please set it in your .env file.")
    st.stop()

try:
    client = InferenceClient(model=MODEL_NAME, token=hf_token)
except Exception as e:
    st.error(f"Error initializing Hugging Face client: {e}")
    st.stop()

# Extract text from PDF
def extract_text_from_pdf(file) -> str:
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

# Load prompt template and insert document content and summary type
def load_prompt_template(text: str, summary_type: str) -> str:
    prompt_file_path = "prompt_logic.md"
    if not os.path.exists(prompt_file_path):
        return "❌ prompt_logic.md file not found. Please create it with the required prompt structure."
    with open(prompt_file_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Truncate document text to avoid overly long prompts (adjust as needed)
    # LLMs have context window limits. Mixtral's is quite large (32k tokens),
    # but prompts for the InferenceClient might have practical limits.
    # 10000 characters is roughly 2500-3000 tokens.
    max_chars = 10000
    truncated_text = text[:max_chars]
    if len(text) > max_chars:
        st.warning(f"Document text was truncated to the first {max_chars} characters for the prompt.")

    prompt = template.replace("{document}", truncated_text)
    prompt = prompt.replace("{summary_type}", summary_type) # Add summary type to prompt
    return prompt

# Generate output using Hugging Face model
def generate_structured_output(text: str, summary_type: str) -> str:
    prompt = load_prompt_template(text, summary_type)
    if "❌" in prompt: # Error message from load_prompt_template
        return prompt

    try:
        # Adjust max_new_tokens as needed. For summary, keywords, and questions,
        # 512 might be too short, especially for detailed summaries.
        response = client.text_generation(
            prompt=prompt,
            max_new_tokens=1024,  # Increased token limit
            temperature=0.5,      # Temperature for creativity vs. factuality
            # top_p=0.9,          # Nucleus sampling
            # repetition_penalty=1.1 # To reduce repetition
        )
        return response
    except Exception as e:
        st.error(f"Error during API call to Hugging Face: {e}")
        return "❌ Error generating output from the model."

# Streamlit UI
st.set_page_config(page_title="GenAI — Document Insights Generator")
st.title("📄 GenAI — Document Insights Generator")

summary_level = st.selectbox(
    "Choose summary type:",
    ["Brief", "Detailed", "Executive"],
    index=0 # Default to "Brief"
)

uploaded_file = st.file_uploader("Upload a PDF or TXT document", type=["pdf", "txt"])

if uploaded_file:
    st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
    file_type = uploaded_file.name.split(".")[-1].lower()

    text = ""
    if file_type == "pdf":
        text = extract_text_from_pdf(uploaded_file)
    elif file_type == "txt":
        try:
            text = uploaded_file.read().decode("utf-8")
        except Exception as e:
            st.error(f"Error reading text file: {e}")
            text = "" # Ensure text is empty on error
    else:
        st.error("Unsupported file type. Please upload a PDF or TXT file.")
        st.stop()

    if not text:
        st.error("Could not extract text from the document.")
        st.stop()

    st.subheader("📄 Document Preview (First 500 characters)")
    st.text_area("Preview", text[:500] + "...", height=100, disabled=True)

    if st.button(f"🔍 Generate {summary_level} Insights"):
        with st.spinner(f"Generating {summary_level} summary, keywords & questions... Please wait."):
            # Pass the selected summary_level to the generation function
            output = generate_structured_output(text, summary_level)

        st.subheader("📊 Structured Report")
        if "❌" in output:
            st.error(output)
        else:
            st.markdown(output) # Render Markdown
            st.success("✅ Insights generated successfully!")

# Display prompt logic for transparency
prompt_file_path = "prompt_logic.md"
if os.path.exists(prompt_file_path):
    with open(prompt_file_path, "r", encoding="utf-8") as f:
        prompt_doc_template = f.read()
    with st.expander("📜 View Raw Prompt Engineering Logic (Template)"):
        st.markdown("This is the template used. `{document}` and `{summary_type}` are replaced at runtime.")
        st.code(prompt_doc_template, language="markdown")
else:
    st.warning("prompt_logic.md not found, so cannot display prompt logic.")



