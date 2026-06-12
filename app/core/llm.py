from langchain_openai import ChatOpenAI


# ==========================================
# LLM
# ==========================================

llm = ChatOpenAI(
    model="gpt-5.4",
    temperature=0
)

