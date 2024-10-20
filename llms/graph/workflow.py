from langgraph.graph import StateGraph, END

from coding_assistant.llms.graph.node import (
    State,
    decide_response_category,
    conversation_node,
    error_handling_node,
    insert_chat_history
)


workflow = StateGraph(State)

workflow.add_node("conversation_node", conversation_node)
workflow.add_node("error_handling_node", error_handling_node)
workflow.add_node("insert_chat_history", insert_chat_history)

workflow.set_conditional_entry_point(
    decide_response_category,
    {
        "conversation_node": "conversation_node",
        "error_handling_node": "error_handling_node"
    }
)
workflow.add_edge("conversation_node", "insert_chat_history")
workflow.add_edge("error_handling_node", "insert_chat_history")
workflow.add_edge("insert_chat_history", END)

# check workflow images
if __name__ == "__main__":
    from PIL import Image
    import io

    app = workflow.compile()

    png = app.get_graph().draw_mermaid_png()
    image = Image.open(io.BytesIO(png))
    image.show()