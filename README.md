# DeadlineSnap 📅

**DeadlineSnap** is a modern, AI-powered academic tracker built with **Streamlit** and **Google Gemini 1.5 Flash**. 

Simply snap a photo of your syllabus, upload a PDF timetable, or type a description of your assignments. DeadlineSnap's AI vision model will instantly extract all upcoming deadlines, display a live color-coded countdown in a beautiful premium UI, and email you a compiled digest using Python's built-in SMTP.

![DeadlineSnap UI Concept](https://img.shields.io/badge/UI-Premium_Glassmorphism-7c3aed?style=flat-square) ![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=Streamlit&logoColor=white) ![Gemini API](https://img.shields.io/badge/Gemini_API-8E75B2?style=flat-square)

---

## ✨ Features

- **📸 Multimodal Input:** Upload photos (.jpg, .png) or PDFs (.pdf) of syllabi and assignment sheets.
- **🧠 Smart AI Extraction:** Powered by Google Gemini to intelligently find dates, tasks, and exams from messy unstructured documents.
- **⏱ Live Countdown Badges:** Automatically generates color-coded badges indicating urgency (🔥 Today, 🚨 3 days, ⚠️ 7 days, 📌 Upcoming).
- **📧 Email Digests:** One-click integration with Gmail SMTP to send a formatted plain-text summary of your deadlines straight to your inbox.
- **🎨 Premium UI/UX:** Built with a beautiful custom CSS design featuring an animated mesh background, glassmorphism cards, glowing text, and Google Inter typography.

---

## 🚀 Quick Start (Run Locally)

### 1. Prerequisites
- Python 3.9+
- A free [Google Gemini API Key](https://aistudio.google.com/)
- A Gmail account with 2-Step Verification enabled and an [App Password](https://myaccount.google.com/apppasswords) created.

### 2. Installation

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/nithishjude/due-date-ai.git
cd due-date-ai
python -m venv venv

# Activate the virtual environment:
# Windows: .\venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

pip install -r requirements.txt
```

### 3. Setup Secrets

Create a `secrets.toml` file inside the `.streamlit/` directory:

```bash
mkdir .streamlit
# Or simply copy the provided example file:
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Fill in `.streamlit/secrets.toml` with your real credentials:

```toml
GEMINI_API_KEY      = "AIzaSyYourGeminiKeyHere..."
GMAIL_ADDRESS       = "your.email@gmail.com"
GMAIL_APP_PASSWORD  = "abcd efgh ijkl mnop"  # 16-character App Password (NO spaces needed in actual use)
```
*(Note: `secrets.toml` is ignored by Git, ensuring your keys stay safe).*

### 4. Run the App

```bash
streamlit run app.py
```
The app will open automatically in your browser at `http://localhost:8501`.

---

## 🛠 Tech Stack

- **Frontend/Backend:** [Streamlit](https://streamlit.io/)
- **AI Model:** Google Gemini (`google-genai` SDK)
- **Email Delivery:** Native Python `smtplib` (Gmail SMTP-SSL)
- **Styling:** Custom CSS injected via `st.markdown`

---

## 💡 How it works under the hood

1. **System Prompting:** `prompts.py` strictly scopes Gemini to only answer questions related to academic schedules and formats its output specifically for our regex parser.
2. **Context Persistence:** Streamlit's `st.session_state` passes the entire chat history (including image bytes) back to the Gemini API on every message, enabling multi-turn memory.
3. **Regex Hooking:** The UI intercepts Gemini's text responses in real-time, scans for dates using Python `re`, and calculates the `(date - today).days` timedelta to render the live UI badges.

---

*Built with ❤️ and AI.*
