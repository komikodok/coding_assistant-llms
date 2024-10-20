from langchain_community.chat_models.ollama import ChatOllama
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder

import json


with open("config.json", "r") as f:
    config = json.load(f)

model_config = config["model"]

llm = ChatOllama(model=model_config["repo_id"])

string_parser = StrOutputParser()

template = """
                You are Bot Njir, a helpful assistant who uses casual Indonesian language but with slightly curt responses. Occasionally (about every 2-5 responses), you give a random joke.

                Avoid any references to religion.

                Respond to the user's input naturally, don't hesitate break the flow with mysterious wolf howls at random points, but always return to the main conversation.

                **Always respond in Indonesian**
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", template),
        MessagesPlaceholder("chat_history"),
        ("human", "Question: {question}")
    ]
)

conversation_chain = (
    prompt 
    | llm 
    | string_parser
)

class ConversationChain:
     
    def __init__(self):
        self.conversation_chain = conversation_chain
        self.chat_history = None

    def invoke(self, input_message: str | dict) -> str:
        if isinstance(input_message, str):
            result = self.conversation_chain.invoke({"question": input_message, "chat_history": self.chat_history})
        elif isinstance(input_message, dict):
            result = self.conversation_chain.invoke(input_message)
        
        return result