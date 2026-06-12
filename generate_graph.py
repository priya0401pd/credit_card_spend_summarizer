from app.langgraph.workflow import graph

graph_image = graph.get_graph().draw_mermaid_png()

with open("workflow.png", "wb") as f:
    f.write(graph_image)

print("Workflow diagram saved")