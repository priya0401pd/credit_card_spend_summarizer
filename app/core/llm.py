from langchain_openai import ChatOpenAI


# ==========================================
# LLM
# ==========================================

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

