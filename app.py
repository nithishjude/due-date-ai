import re
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import streamlit as st
from google import genai
from google.genai import types

from prompts import SUMMARY_REQUEST_PROMPT, SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE

MODEL_NAME = "gemini-flash-lite-latest"

st.set_page_config(
    page_title="DeadlineSnap · AI Deadline Tracker",
    page_icon="📅",
    layout="centered",
)

# ── Premium CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background: #050510 !important;
    color: #e2e8f0 !important;
}

/* ── Animated mesh background ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 20% 10%, rgba(99,55,255,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 80%, rgba(30,140,255,0.14) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 50% 50%, rgba(200,80,255,0.07) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
    animation: bg-shift 12s ease-in-out infinite alternate;
}
@keyframes bg-shift {
    0%   { opacity: 0.8; transform: scale(1); }
    100% { opacity: 1;   transform: scale(1.04); }
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header, .stDeployButton { display: none !important; }
.block-container {
    max-width: 760px !important;
    padding: 1rem 1.5rem 4rem !important;
    position: relative;
    z-index: 1;
}

/* ── Glowing logo card ── */
.logo-card {
    background: linear-gradient(135deg,
        rgba(99,55,255,0.2) 0%,
        rgba(30,100,255,0.15) 50%,
        rgba(200,60,255,0.12) 100%);
    border: 1px solid rgba(140,100,255,0.3);
    border-radius: 24px;
    padding: 2.5rem 2rem 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    margin-bottom: 1.8rem;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow:
        0 0 60px rgba(100,60,255,0.15),
        0 0 120px rgba(100,60,255,0.06),
        inset 0 1px 0 rgba(255,255,255,0.08);
}
.logo-card::after {
    content: '';
    position: absolute;
    top: -80px; left: 50%;
    transform: translateX(-50%);
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(140,80,255,0.25) 0%, transparent 70%);
    animation: halo 4s ease-in-out infinite;
    pointer-events: none;
}
@keyframes halo {
    0%, 100% { opacity: 0.6; transform: translateX(-50%) scale(1);   }
    50%       { opacity: 1;   transform: translateX(-50%) scale(1.15); }
}
.logo-emoji {
    font-size: 3.8rem;
    display: block;
    margin-bottom: 0.5rem;
    filter: drop-shadow(0 0 20px rgba(160,100,255,1));
    animation: bob 3.5s ease-in-out infinite;
    position: relative;
    z-index: 1;
}
@keyframes bob {
    0%, 100% { transform: translateY(0);   }
    50%       { transform: translateY(-8px); }
}
.logo-name {
    font-size: 2.4rem;
    font-weight: 900;
    background: linear-gradient(100deg, #c084fc, #818cf8, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
    line-height: 1;
    position: relative;
    z-index: 1;
}
.logo-tagline {
    color: #94a3b8;
    font-size: 0.9rem;
    margin-top: 0.5rem;
    font-weight: 400;
    letter-spacing: 0.2px;
    position: relative;
    z-index: 1;
}

/* ── Glass card ── */
.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    backdrop-filter: blur(12px);
    margin-bottom: 1rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}

/* ── Info bar ── */
.info-bar {
    background: rgba(99,55,255,0.1);
    border: 1px solid rgba(99,55,255,0.25);
    border-radius: 12px;
    padding: 0.55rem 1rem;
    font-size: 0.82rem;
    color: #a78bfa;
    font-weight: 500;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Streamlit buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.6rem 1.2rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 20px rgba(124,58,237,0.4) !important;
    letter-spacing: 0.2px;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 30px rgba(124,58,237,0.65) !important;
    background: linear-gradient(135deg, #8b5cf6, #6366f1) !important;
}
.stButton > button:active { transform: translateY(0) !important; }
.stButton > button:disabled {
    background: rgba(255,255,255,0.07) !important;
    color: #475569 !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ── Form inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.65rem 0.9rem !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(124,58,237,0.6) !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.15) !important;
    outline: none !important;
}
.stTextInput label, .stTextArea label {
    color: #94a3b8 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}

/* ── Chat messages ── */
.stChatMessage {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important;
    padding: 1rem !important;
    margin-bottom: 0.6rem !important;
    backdrop-filter: blur(8px) !important;
}
[data-testid="stChatMessageContent"] p {
    color: #e2e8f0 !important;
    font-size: 0.92rem !important;
    line-height: 1.65 !important;
}

/* ── Chat input ── */
.stChatInputContainer, [data-testid="stChatInput"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 14px !important;
    backdrop-filter: blur(12px) !important;
}
.stChatInputContainer:focus-within {
    border-color: rgba(124,58,237,0.5) !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.12) !important;
}

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.06) !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #7c3aed !important; }

/* ── Success / Error ── */
.stSuccess {
    background: rgba(52,211,153,0.1) !important;
    border: 1px solid rgba(52,211,153,0.3) !important;
    border-radius: 10px !important;
    color: #6ee7b7 !important;
}
.stAlert {
    background: rgba(239,68,68,0.1) !important;
    border: 1px solid rgba(239,68,68,0.3) !important;
    border-radius: 10px !important;
}

/* ── Countdown badges ── */
.badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    margin: 0.6rem 0 1rem;
}
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.3rem 0.7rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    border: 1px solid;
    white-space: nowrap;
    transition: transform 0.15s;
}
.badge:hover { transform: scale(1.04); }
.b-red    { background:rgba(239,68,68,0.13);  border-color:rgba(239,68,68,0.4);  color:#fca5a5; }
.b-amber  { background:rgba(251,191,36,0.13); border-color:rgba(251,191,36,0.4); color:#fde68a; }
.b-green  { background:rgba(52,211,153,0.13); border-color:rgba(52,211,153,0.4); color:#6ee7b7; }
.b-muted  { background:rgba(148,163,184,0.1); border-color:rgba(148,163,184,0.25);color:#94a3b8; }

/* ── Section label ── */
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #64748b;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── Secrets ───────────────────────────────────────────────────────────────────
GEMINI_API_KEY     = st.secrets["GEMINI_API_KEY"]
GMAIL_ADDRESS      = st.secrets["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]

# ── Cached client ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)

gemini_client = get_gemini_client()

# ── Deadline parser ───────────────────────────────────────────────────────────
MONTH_MAP = {
    "jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,
    "jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12,
}

def parse_deadlines(text: str) -> list[dict]:
    today = date.today()
    year  = today.year
    found, seen = [], set()

    for m in re.finditer(
        r'([A-Za-z]{3,9})\s+(\d{1,2})(?:st|nd|rd|th)?(?:[,\s]+(\d{4}))?', text
    ):
        mon = MONTH_MAP.get(m.group(1)[:3].lower())
        if not mon:
            continue
        yr = int(m.group(3)) if m.group(3) else year
        try:
            d = date(yr, mon, int(m.group(2)))
        except ValueError:
            continue
        ctx = text[max(0, m.start()-60):m.start()].strip().split('\n')[-1].strip()
        label = (ctx or m.group(0))[:55]
        if d not in seen:
            seen.add(d)
            found.append({"label": label, "date": d, "days_left": (d - today).days})

    for m in re.finditer(r'(\d{4})-(\d{2})-(\d{2})', text):
        try:
            d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            continue
        if d not in seen:
            seen.add(d)
            ctx = text[max(0, m.start()-60):m.start()].strip().split('\n')[-1].strip()
            found.append({"label": (ctx or m.group(0))[:55], "date": d,
                          "days_left": (d - today).days})

    return sorted(found, key=lambda x: x["date"])


def render_badges(deadlines: list[dict]) -> None:
    if not deadlines:
        return
    st.markdown('<p class="section-label">⏱ Live Countdown</p>', unsafe_allow_html=True)
    html = '<div class="badge-row">'
    for dl in deadlines:
        days = dl["days_left"]
        ds   = dl["date"].strftime("%b %d")
        lbl  = dl["label"][:28]
        if days < 0:
            cls, icon, tag = "b-muted", "✅", "done"
        elif days == 0:
            cls, icon, tag = "b-red",   "🔥", "TODAY"
        elif days <= 3:
            cls, icon, tag = "b-red",   "🚨", f"{days}d"
        elif days <= 7:
            cls, icon, tag = "b-amber", "⚠️", f"{days}d"
        else:
            cls, icon, tag = "b-green", "📌", f"{days}d"
        html += f'<span class="badge {cls}">{icon} {ds} · {lbl} · {tag}</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ── Email ─────────────────────────────────────────────────────────────────────
def send_email(to: str, name: str, summary: str) -> tuple[bool, str]:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📅 Your Deadline Digest — DeadlineSnap"
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = to
    msg.attach(MIMEText(
        f"Hi {name},\n\nHere's your deadline digest:\n\n{summary}\n\n— DeadlineSnap 📅",
        "plain"
    ))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            s.send_message(msg)
        return True, ""
    except Exception as e:
        return False, str(e)


# ── Gemini ────────────────────────────────────────────────────────────────────
def ask_gemini(parts: list) -> str:
    try:
        return st.session_state.chat.send_message(parts).text
    except Exception as e:
        return f"Sorry, something went wrong: {e}"


# ── Message helpers ───────────────────────────────────────────────────────────
def render_message(msg: dict) -> None:
    with st.chat_message(msg["role"]):
        if msg["kind"] == "text":
            st.write(msg["content"])
        elif msg["kind"] == "image":
            st.image(msg["content"])


def add_message(role: str, kind: str, content) -> None:
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])
    if role == "assistant" and kind == "text":
        new = parse_deadlines(content)
        existing_dates = {d["date"] for d in st.session_state.get("deadlines", [])}
        for dl in new:
            if dl["date"] not in existing_dates:
                st.session_state.deadlines.append(dl)
                existing_dates.add(dl["date"])
        st.session_state.deadlines.sort(key=lambda x: x["date"])


# ══════════════════════════════════════════════════════════════════════════════
# ONBOARDING
# ══════════════════════════════════════════════════════════════════════════════
if "onboarded" not in st.session_state:

    st.markdown("""
    <div class="logo-card">
        <span class="logo-emoji">📅</span>
        <p class="logo-name">DeadlineSnap</p>
        <p class="logo-tagline">Your AI-powered academic deadline detector</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card" style="margin-bottom:1.4rem;">
        <p style="color:#94a3b8;font-size:0.88rem;line-height:1.7;text-align:center;">
            📸 &nbsp;Snap a photo of your syllabus or timetable<br>
            🤖 &nbsp;Gemini reads every deadline instantly<br>
            📧 &nbsp;Get a digest sent straight to your email
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("onboarding_form"):
        name  = st.text_input("Your name", placeholder="e.g. Priya Sharma")
        email = st.text_input("Email address", placeholder="you@example.com",
                              help="Your deadline digest will be emailed here.")
        go    = st.form_submit_button("Get Started 🚀", use_container_width=True)

    if go:
        if not name.strip() or not email.strip():
            st.warning("Please fill in both fields.")
        elif "@" not in email or "." not in email.split("@")[-1]:
            st.warning("That email doesn't look right — please double-check.")
        else:
            st.session_state.name      = name.strip()
            st.session_state.email     = email.strip()
            st.session_state.deadlines = []
            st.session_state.messages  = []
            st.session_state.chat      = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            )
            st.session_state.onboarded = True
            st.rerun()
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN INTERFACE
# ══════════════════════════════════════════════════════════════════════════════

# ── Logo ──
st.markdown("""
<div class="logo-card" style="padding:1.6rem 2rem 1.4rem;">
    <span class="logo-emoji" style="font-size:2.8rem;">📅</span>
    <p class="logo-name" style="font-size:2rem;">DeadlineSnap</p>
    <p class="logo-tagline">AI-powered deadline detector</p>
</div>
""", unsafe_allow_html=True)

# ── Info bar + Send button ──
col_info, col_btn = st.columns([4, 2], vertical_alignment="center")
with col_info:
    st.markdown(
        f'<div class="info-bar">👤 <b>{st.session_state.name}</b>'
        f'&ensp;·&ensp;📬 {st.session_state.email}</div>',
        unsafe_allow_html=True,
    )
with col_btn:
    send_disabled = len(st.session_state.get("messages", [])) <= 2
    if st.button("📧 Email Digest", disabled=send_disabled,
                 use_container_width=True):
        with st.spinner("Generating digest..."):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])
        with st.spinner("Sending to inbox..."):
            ok, err = send_email(st.session_state.email,
                                 st.session_state.name, summary)
        if ok:
            st.success("✅ Digest sent! Check your inbox.")
        else:
            st.error(f"Send failed: {err}")

# ── Countdown badges ──
if st.session_state.get("deadlines"):
    render_badges(st.session_state.deadlines)
    st.divider()

# ── Chat history ──
if not st.session_state.messages:
    add_message("assistant", "text",
                WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name))
else:
    for m in st.session_state.messages:
        render_message(m)

# ── Input ──
user_input = st.chat_input(
    "Ask anything, or attach a photo / PDF of your syllabus 📎",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "webp", "pdf"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text  = user_input.text or ""
    parts = []

    if photo:
        photo_bytes = photo.getvalue()
        # If it's a PDF, we don't try to render it visually in chat, just show a doc icon
        if photo.type == "application/pdf":
            add_message("user", "text", f"📄 Uploaded document: {photo.name}")
        else:
            add_message("user", "image", photo_bytes)
        
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))

    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo:
        parts.append(
            "This is an academic document. Extract all deadlines, due dates, "
            "exam dates and events. List them clearly with dates."
        )

    with st.spinner("Scanning for deadlines..."):
        answer = ask_gemini(parts)

    add_message("assistant", "text", answer)
