from langchain_core.messages import HumanMessage
from app.langgraph.workflow import graph


class QueryService:

    def ask(self, query):

        response = graph.invoke(
            {
                "messages": [
                    HumanMessage(content=query)
                ],
                "citations": []
            }
        )

        return response

    def stream(self, query):

        for chunk in graph.stream(
            {
                "messages": [
                    HumanMessage(content=query)
                ],
                "citations": []
            },
            stream_mode="values"
        ):

            if "messages" in chunk:

                last_message = chunk["messages"][-1]

                if hasattr(
                    last_message,
                    "content"
                ):

                    yield last_message.content


query_service = QueryService()


# from langchain_core.messages import HumanMessage

# from app.langgraph.workflow import graph


# class QueryService:

#     def ask(self, query):

#         response = graph.invoke(
#     {
#         "messages": [
#             HumanMessage(content=query)
#         ],
#         "citations": []
#     }
# )

#         return response


# query_service = QueryService()