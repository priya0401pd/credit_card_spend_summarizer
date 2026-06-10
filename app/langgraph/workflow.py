from langgraph.graph import (
    StateGraph,
    MessagesState,
    
    START,
    END
)


import json
from langgraph.prebuilt import ToolNode
from app.sql.sql_tool import sql_tool
from app.core.llm import llm

from langchain_core.messages import (
    HumanMessage,
    SystemMessage
)

from langchain_core.tools import tool

from langchain_openai import ChatOpenAI

from app.retrieval.retriever import retriever



# ==========================================
# HELPER
# ==========================================

def format_docs(docs):

    if not docs:
        return "No documents found."

    formatted = []

    for doc in docs:
          formatted.append(
    f"""
[CITATION]

Source:
{doc.get('source_file')}

Section:
{doc.get('section')}

Page:
{doc.get('page_number')}

Content:
{doc.get('content')}
"""
)

#         formatted.append(
#             f"""
# Section:
# {doc.get('section')}

# Page:
# {doc.get('page_number')}

# Source:
# {doc.get('source_file')}

# Content:
# {doc.get('content')}
# """
#         )

    return "\n\n".join(formatted)

# ==========================================
# TOOLS
# ==========================================

@tool
def fts_tool(
    query: str
):
    """
    Use for exact keyword lookups.
    """

    docs = retriever.fts_tool(
        query=query
    )

    return format_docs(docs)


@tool
def vector_tool(
    query: str
):
    """
    Use for semantic search.
    """

    docs = retriever.vector_tool(
        query=query
    )

    return format_docs(docs)


@tool
def hybrid_tool(query: str):
    """
    Use for all knowledge base questions:
    policies,
    eligibility rules,
    annual fee waiver,
    reward rules,
    forex markup,
    benefits,
    card features,
    and product information.

    This is the primary retrieval tool.
    """
    print("\nHYBRID TOOL CALLED\n")

    docs = retriever.hybrid_tool(
        query=query
    )

    return format_docs(docs)



TOOLS = [

    fts_tool,

    vector_tool,

    hybrid_tool,

    sql_tool
]

llm_with_tools = (
    llm.bind_tools(
        TOOLS
    )
)



# ==========================================
# AGENT NODE
# ==========================================

def agent_node(
    state: MessagesState
):

    system_prompt = """
You are an AI-powered Credit Card Assistant.

Your job is to answer user questions by selecting and using the appropriate tools.Tool outputs are the ONLY source of truth.
If information is not present in tool outputs, you do not know it.

AVAILABLE TOOLS

1. sql_tool
- Retrieves structured customer information.
- Use for customer-specific facts such as spend, transactions, balances, reward points, statements, limits, card details, and account information.

2. hybrid_tool
- Retrieves information from the credit card knowledge base.
- Use for policies, benefits, fees, eligibility rules, reward rules, card features, forex charges, and product information.

TOOL USAGE RULES

Customer-specific questions:
- Use sql_tool.

Knowledge-base questions:
- Use hybrid_tool.

Questions that require both customer facts and policy information:
- Use both sql_tool and hybrid_tool.

REASONING PROCESS

1. Understand the user's intent.
2. Determine what information is needed.
3. Identify whether customer data, policy information, or both are required.
4. Call the necessary tools.
5. Use information obtained from tool outputs.
6. Do not answer until sufficient information has been gathered.
7. Generate the final answer based only on retrieved facts.

IMPORTANT

- Never assume customer information.
- Never invent policy information.
- Customer facts must come from sql_tool.
- Policy information must come from hybrid_tool.
- Eligibility decisions require customer facts and policy rules.
- If information is unavailable, clearly state that.

CITATIONS

When hybrid_tool is used:
- Include the source file.
- Include the section.
- Include the page number.
- Use only citations returned by the retrieval results.

RESPONSE RULES

- Be concise.
- Use INR formatting.
- Do not expose SQL queries.
- Do not expose internal reasoning.
==================================================
GROUNDING AND HALLUCINATION PREVENTION
======================================

You must answer ONLY using information obtained from tool outputs.

Allowed Sources:

* sql_tool output
* hybrid_tool output

Rules:

1. Never use your own knowledge.
2. Never assume missing information.
3. Never infer policies that are not explicitly found in retrieval results.
4. Never infer customer facts that are not explicitly returned by sql_tool.
5. Never generate answers without supporting evidence from tools.
6. If required information is missing, state that the information is unavailable.
7. If policy information is not found in retrieval results, do not answer the policy question.
8. If customer information is not found in SQL results, do not answer the customer-specific question.
9. Do not make probabilistic guesses.
10. Do not fabricate citations.
11. Do not create page numbers, sections, source names, thresholds, limits, fees, rewards, benefits, or eligibility rules.

STRICT PROHIBITIONS

The following are prohibited:

* Hallucinated facts
* Assumptions
* Estimates
* Guesses
* External knowledge
* Generic banking knowledge
* Industry assumptions
* Policy reconstruction

When evidence is insufficient, respond with:

"I could not find sufficient information in the available data sources to answer this question."

ELIGIBILITY RULES

For eligibility decisions:

* Customer facts must come from sql_tool.
* Policy rules must come from hybrid_tool.
* If either is unavailable, do not make an eligibility decision.

ANSWER VALIDATION

Before generating a final answer, verify:

* Every customer fact is supported by sql_tool output.
* Every policy statement is supported by hybrid_tool output.
* Every citation comes from retrieval metadata.

If any statement cannot be traced to a tool result, do not include it in the answer.

"""


    response = (
        llm_with_tools.invoke(
            [
                system_prompt,
                *state["messages"]
            ]
        )
    )

    return {
        "messages":
        [response]
    }


# ==========================================
# ROUTING
# ==========================================

def should_continue(
    state: MessagesState
):

    last_message = (
        state["messages"][-1]
    )

    if last_message.tool_calls:

        return "tools"
    
    print("\nTOOL CALLS:")
    print(last_message.tool_calls)

    return END


# ==========================================
# TOOL NODE
# ==========================================


tool_node = ToolNode(
    TOOLS
)


# ==========================================
# GRAPH
# ==========================================

workflow = StateGraph(
    MessagesState
)

workflow.add_node(
    "agent",
    agent_node
)

workflow.add_node(
    "tools",
    tool_node
)

workflow.add_edge(
    START,
    "agent"
)

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)

workflow.add_edge(
    "tools",
    "agent"
)

graph = workflow.compile()