import uuid
import requests
import streamlit as st

st.set_page_config(
    page_title="Credit Card Spend Summarizer",
    page_icon="💳",
    layout="wide"
)

# ----------------------------------------------------
# CSS
# ----------------------------------------------------

st.markdown("""
<style>

/* Main App */
.stApp {
    background-color: ##241b2c;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #393a3b;
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: #f5f8fa;
}

/* Header Banner */
.header-banner {
    background: linear-gradient(
    135deg,
    #1E293B,
    #0F172A,
    #020617
);
    padding: 35px;
    border-radius: 20px;
    color: white;
    box-shadow: 0px 5px 20px rgba(0,0,0,0.15);
    margin-bottom: 25px;
    
    /* These three lines center everything inside perfectly */
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
}

.header-title {
    font-size: 48px;
    font-weight: 700;
}

.header-subtitle {
    font-size: 18px;
    opacity: 0.9;
}

/* Section Titles */
.section-title {
    color: #565449;
    font-size: 28px;
    font-weight: 700;
}

/* Specific styling for Upload & Action Buttons (avoid styling history buttons) */
div.stButton > button[data-testid="baseButton-secondary"] {
    border-radius: 10px;
    font-weight: 600;
    color:#6A97C0
}

/* Chat Input styling */
.stChatInput {
    border-radius: 12px;
}

/* Divider */
hr {
    border: 1px solid #D8CFBC;
}

</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------
# CONFIG
# ----------------------------------------------------

FASTAPI_URL = "http://localhost:8000"

# ----------------------------------------------------
# SESSION
# ----------------------------------------------------

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# ----------------------------------------------------
# LOAD HISTORY
# ----------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []

try:
    if not st.session_state.history:
        response = requests.get(
            f"{FASTAPI_URL}/api/v1/history/{st.session_state.session_id}"
        )
        if response.status_code == 200:
            st.session_state.history = response.json()
except Exception:
    st.session_state.history = []

history = st.session_state.history


# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------

with st.sidebar:
    st.markdown("## 💳")
    st.markdown(
        """
        <h1 style='color:white; margin-top:-15px;'>
        Credit Card<br>
        Spend<br>
        Summarizer
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.write("---")

    # New Chat Button
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.history = []
        st.rerun()

    # Search Chats
    search_text = st.text_input("Search Chats", placeholder="Search...")

    st.markdown("### Chat History")

    user_queries = [
        item["message"]
        for item in history
        if item.get("role") == "user"
    ]

    # Filter
    if search_text:
        user_queries = [q for q in user_queries if search_text.lower() in q.lower()]

    # Display History
    if user_queries:
        # Added enumerate to fix potential duplicate item['id'] crashes
        for idx, item in enumerate(reversed(history)):
            if item.get("role") == "user":
                if search_text and search_text.lower() not in item["message"].lower():
                    continue
                st.button(
                    item["message"][:35] + "...",
                    key=f"history_{item.get('id', idx)}_{idx}",
                    use_container_width=True
                )
    else:
        st.caption("No conversations yet")

    st.write("---")
    
    # Sidebar footer elements
    st.button("⚙ Settings", key="sidebar_settings", use_container_width=True)
    st.button("↩ Logout", key="sidebar_logout", use_container_width=True)


# ----------------------------------------------------
# MAIN HEADER
# ----------------------------------------------------

st.markdown("""
<div class="header-banner">
    <div class="header-title">💳 Credit Card Spend Summarizer</div><br><br><br><br><br>

</div>
""", unsafe_allow_html=True)


# ----------------------------------------------------
# MAIN LAYOUT
# ----------------------------------------------------

left, right = st.columns([1, 2], gap="large")


# ----------------------------------------------------
# UPLOAD PANEL
# ----------------------------------------------------

with left:
    st.markdown("### 📄 Upload Document")
    st.write("Upload your Statement (PDF)")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        label_visibility="collapsed"
    )

    if st.button("Upload & Process", use_container_width=True):
        if uploaded_file:
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file,
                    "application/pdf"
                )
            }
            with st.spinner("Uploading and analyzing statement..."):
                try:
                    response = requests.post(
                        f"{FASTAPI_URL}/upload/pdf",
                        files=files
                    )
                    if response.status_code == 200:
                        st.success("File uploaded successfully!")
                    else:
                        st.error(f"Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"Could not connect to backend server: {e}")
        else:
            st.warning("Please upload a PDF first")

    st.markdown("---")
    st.caption("🔒 Your data is secure, encrypted, and private.")


# ----------------------------------------------------
# CHAT PANEL
# ----------------------------------------------------

with right:
    st.markdown("### 💬 Chat Insights")
    
    # Render Chat History Container
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["message"])

    # Chat Input
    prompt = st.chat_input("Ask anything about your spending...")

    if prompt:
        # Append message immediately to state
        st.session_state.history.append({"role": "user", "message": prompt})
        st.session_state.pending_query = prompt
        st.rerun()


# ----------------------------------------------------
# PROCESS QUERY AFTER UI RENDERS
# ----------------------------------------------------

if "pending_query" in st.session_state:
    query = st.session_state.pending_query
    del st.session_state.pending_query

    with right:
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{FASTAPI_URL}/api/v1/query",
                    json={
                        "session_id": st.session_state.session_id,
                        "query": query
                    }
                )
                
                if response.status_code == 200:
                    history_response = requests.get(
                        f"{FASTAPI_URL}/api/v1/history/{st.session_state.session_id}"
                    )
                    if history_response.status_code == 200:
                        st.session_state.history = history_response.json()
                    st.rerun()  # Only rerun here if processing succeeded to paint new screen
                else:
                    st.error(f"Error fetching response: {response.text}")
            except Exception as e:
                st.error(f"Backend connection loss: {e}")


# ----------------------------------------------------
# FOOTER
# ----------------------------------------------------

st.markdown("""
<br><hr>
<center style="opacity: 0.7; font-size: 14px;">
    🔒 Bank-grade Security &nbsp;&nbsp;•&nbsp;&nbsp; 
    Doc Private & Confidential &nbsp;&nbsp;•&nbsp;&nbsp; 
    💳 Your Data, Your Control
</center>
""", unsafe_allow_html=True)