# Summarizer — GenAI Application

This project is a **Streamlit app** powered by the **LLaMA 2 model via Hugging Face**, designed to:

- Accept **PDF file uploads**
- Extract text from the file using **PyPDF2**
- Generate a **5-point summary** using **LLaMA-2-7B-chat** from Hugging Face

---

## Features
- Upload any `.pdf` document
- Summarize with LLaMA 2 (open-source large language model)
- Simple, interactive UI using Streamlit

---

## How to Run the App

### 1. Install Requirements
```bash
pip install streamlit PyPDF2 langchain huggingface_hub python-dotenv
```

### 2.Set Your Hugging Face API Key
Create a `.env` file in your project root:
```env
HUGGINGFACEHUB_API_TOKEN=your-hugging-face-token-here
```

> Generate your token from: https://huggingface.co/settings/tokens

### 3. Launch the App
```bash
streamlit run llama_streamlit_app.py
```

---

## Behind the Scenes
- **LLaMA-2-7B** is accessed via HuggingFace Hub using `langchain.llms.HuggingFaceHub`
- Prompts are passed in plain text to the model
- PDF text is extracted page-by-page using `PyPDF2`

---

## Example Output
**Uploaded PDF:** A loan policy document

**Generated Summary:**
- Customers incur a 2% penalty for early closure within 6 months.
- No charges apply after 6 months.
- Loan closures require a 7-day notice.
- Policy enhances transparency and planning.
- Encourages long-term financial engagement.

---

## Project Structure
```
SUMMARIZER_APP/
├── app_main.py
├── .env
├── DATA/
└── README.md
|__REQUIREMENTS.txt
```

---

## Notes
- The app uses **public inference endpoints**, which may rate-limit or queue requests.
- Requires a **free or pro Hugging Face account** to access LLaMA models.

---

## License
MIT License — Free to use and modify with credit.

---

Built using LLaMA, Streamlit, and Python.
