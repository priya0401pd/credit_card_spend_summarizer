from langchain_core.messages import HumanMessage

from app.langgraph.workflow import graph


query = "What is the forex markup for NorthStar Gold?"

response = graph.invoke(
    {
        "messages": [
            HumanMessage(
                content=query
            )
        ]
    }
)

print("\nFINAL ANSWER\n")

for msg in response["messages"]:

    print("\n" + "=" * 80)
    print(type(msg).__name__)
    print("=" * 80)

    print(msg.content)