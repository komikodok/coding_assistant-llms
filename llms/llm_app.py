from langchain_core.messages import AIMessage, HumanMessage

from llms.graph.workflow import workflow


llm_app = workflow.compile()

class LLMApp:

    def __init__(self):
        self.llm_app = llm_app
        self.result = None

    def invoke(self, message: dict = None, **kwargs) -> "LLMApp":
        if message and isinstance(message, dict):
            input_data = message
        elif kwargs:
            input_data = kwargs
        else:
            raise ValueError("Input data provide either a dictionary message or keyword arguments")
        self.result = self.llm_app.invoke(input_data)

        return self
    
    def get_response_items(self) -> dict:
        human_message = [message for message in self.result["chat_history"] if isinstance(message, HumanMessage)]
        ai_message = [message for message in self.result["chat_history"] if isinstance(message, AIMessage)]

        response_items = {}
        response_items["question"] = self.result["question"]
        response_items["generation"] = self.result["generation"]
        response_items["chat_history"] = [
            {
                "humman_message": human.content,
                "ai_message": ai.content
            } for human, ai in zip(human_message, ai_message)
        ]

        return response_items


if __name__ == "__main__":
    import threading


    llm_app = LLMApp()
    user_input = input("You: ")

    loading = True

    def loading_screen():
        while loading:
            print("sedang mengeksekusi program")

    loading_thread = threading.Thread(target=loading_screen)
    loading_thread.start()
    result = llm_app.invoke(question=user_input)
    response = result.get_response_items()["generation"]

    loading = False
    loading_thread.join()
    print(f"Bot: {response}")