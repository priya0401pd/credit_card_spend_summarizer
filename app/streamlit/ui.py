
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
.stApp{
    background-color:#FFFBF4;
}

/* Sidebar */
section[data-testid="stSidebar"]{
    background-color:#11120D;
}

/* Sidebar text */
section[data-testid="stSidebar"] *{
    color:white;
}

/* Header Banner */
.header-banner{
    background: linear-gradient(
        135deg,
        #565449,
        #6d6b5e
    );

    padding:35px;
    border-radius:20px;

    color:white;

    box-shadow:0px 5px 20px rgba(0,0,0,0.15);

    margin-bottom:25px;
}

.header-title{
    font-size:48px;
    font-weight:700;
}

.header-subtitle{
    font-size:18px;
    opacity:0.9;
}

/* Cards */
.custom-card{
    background:#FFFBF4;
    border:1px solid #D8CFBC;

    border-radius:20px;

    padding:25px;

    box-shadow:
        0px 4px 12px rgba(0,0,0,0.08);
}

/* Section Titles */
.section-title{
    color:#565449;
    font-size:28px;
    font-weight:700;
}

/* Upload Button */
.stButton button{
    background-color:#565449;
    color:white;
    border:none;
    border-radius:10px;
    padding:10px;
    font-weight:600;
}

/* Chat Input */
.stChatInput{
    border-radius:12px;
}

/* Divider */
hr{
    border:1px solid #D8CFBC;
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
    st.session_state.session_id = str(
        uuid.uuid4()
    )

# ----------------------------------------------------
# LOAD HISTORY
# ----------------------------------------------------

history = []

try:

    response = requests.get(
        f"{FASTAPI_URL}/api/v1/history/{st.session_state.session_id}"
    )

    if response.status_code == 200:

        history = response.json()

except Exception:
    history = []

# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------

# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------

with st.sidebar:

    st.markdown("## 💳")

    st.markdown(
        """
        <h1 style='color:white'>
        Credit Card<br>
        Spend<br>
        Summarizer
        </h1>
        """,
        unsafe_allow_html=True
    )

    # New Chat

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        st.session_state.session_id = str(
            uuid.uuid4()
        )

        st.rerun()

    st.markdown("---")

    # Search Chats

    search_text = st.text_input(
        "Search Chats",
        placeholder="Search..."
    )

    st.markdown("### Chat History")

    user_queries = [
        item["message"]
        for item in history
        if item["role"] == "user"
    ]

    # Filter

    if search_text:

        user_queries = [
            q
            for q in user_queries
            if search_text.lower()
            in q.lower()
        ]

    # Display History

    if user_queries:

        for item in reversed(history):

            if item["role"] == "user":

                st.button(
                    item["message"][:40],
                    key=f"history_{item['id']}",
                    use_container_width=True
                )

    else:

        st.caption(
            "No conversations yet"
        )

# with st.sidebar:

#     st.markdown("## 💳")
    
#     st.markdown(
#         """
#         <h1 style='color:white'>
#         Credit Card<br>
#         Spend<br>
#         Summarizer
#         </h1>
#         """,
#         unsafe_allow_html=True
#     )

#     if st.button("➕ New Chat"):

#         st.session_state.session_id = str(
#             uuid.uuid4()
#         )

#         st.rerun()

#     st.markdown("<br><br><br>", unsafe_allow_html=True)

#     st.markdown("---")

    st.button("⚙ Settings")

    st.button("↩ Logout")

# ----------------------------------------------------
# MAIN HEADER
# ----------------------------------------------------

st.markdown("""
<div class="header-banner">

<div class="header-title">
💳 Credit Card Spend Summarizer
</div>

<div class="header-subtitle">
Upload your statement and get intelligent insights
about your spending.
</div>

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

    st.markdown("## 📄 Upload Statement")

    st.write("Upload your credit card statement (PDF)")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"]
    )

    st.info("Supported format: PDF")

    if st.button("Upload & Process"):

        if uploaded_file:

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file,
                    "application/pdf"
                )
            }

            response = requests.post(
                f"{FASTAPI_URL}/upload/pdf",
                files=files
            )

            if response.status_code == 200:

                st.success(
                    "File uploaded successfully"
                )

            else:

                st.error(
                    response.text
                )

        else:

            st.warning(
                "Please upload a PDF first"
            )

    st.markdown("---")

    st.write("🔒 Your data is secure and private")

# ----------------------------------------------------
# CHAT PANEL
# ----------------------------------------------------

with right:

    st.markdown("## 💬 Chat")

    st.caption(
        "Ask questions and get insights about your spending"
    )

    for msg in history:

        with st.chat_message(
            msg["role"]
        ):
            st.markdown(
                msg["message"]
            )

    prompt = st.chat_input(
        "Ask anything about your spending..."
    )

    if prompt:

        response = requests.post(
            f"{FASTAPI_URL}/api/v1/query",
            json={
                "session_id":
                    st.session_state.session_id,

                "query":
                    prompt
            }
        )

        if response.status_code == 200:

            st.rerun()

        else:

            st.error(
                response.text
            )

# ----------------------------------------------------
# FOOTER
# ----------------------------------------------------

st.markdown("""
<hr>

<center>

🔒 Bank-grade Security    •
📄 Private & Confidential    •
💳 Your Data, Your Control

</center>
""", unsafe_allow_html=True)

