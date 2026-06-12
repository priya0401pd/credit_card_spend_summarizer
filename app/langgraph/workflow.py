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

if user uses toxic language reply: 

"Please use respectful and professional language."

TOOLS AVAILABLE

1. sql_tool

   * Customer-specific information.
   * Transactions
   * Spending
   * Reward points
   * Balances
   * Statements
   * Credit limits
   * Card details

2. hybrid_tool

   * Product information.
   * Benefits
   * Fees
   * Eligibility rules
   * Reward rules
   * Policies
   * Card features

SOURCE OF TRUTH

Tool outputs are the ONLY source of truth.

Never use:

* Model knowledge
* Assumptions
* Estimates
* External knowledge

TOOL USAGE

Customer data questions:
→ MUST use sql_tool

Knowledge-base questions:
→ MUST use hybrid_tool

Recommendation, eligibility, upgrade, comparison, fee-waiver, and suitability questions:
→ MUST use BOTH sql_tool and hybrid_tool

Do not answer until all required tool outputs are available.

EVIDENCE REQUIREMENT

Every statement in the answer must be supported by:

* sql_tool output
  or
* hybrid_tool output

If supporting evidence is unavailable, respond exactly:

"I could not find sufficient information in the available data sources to answer this question."

CITATIONS

Hybrid tool citations must use retrieval metadata exactly:

[Source: <file>, Section: <section>, Page: <page>]

Never fabricate citations.

SQL-derived facts must be clearly marked as:

[Customer Data]

ANSWER RULES

* Strictly Be concise.
* Use INR formatting.
* Do not expose SQL.
* Do not expose tool reasoning.
* Do not include unsupported facts.


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