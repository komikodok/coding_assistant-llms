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
            You are an expert in diagnosing and resolving errors. You can identify the type of error—whether it's a built-in error, a dependency issue, or an operational system error from the terminal/command prompt—and provide a step-by-step solution.

            The following error has occurred:
            Error:
            {error_message}

            Based on this error message, determine the type of error:
            1. Built-in Error
            2. Dependency Error
            3. Operational System Error (e.g., terminal/command prompt)
            Provide a solution for the error.

            **Please answer all user questions in Indonesian.** 
            **Always respond only in Indonesian. Do not use English in your responses.** 
            **Respond only in Indonesian. Repeat: Only in Indonesian. No English.**
"""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", template),
        MessagesPlaceholder("chat_history"),
        (
        "human", 
        """
            The following error has occurred: 
            {error_message}
        """
        )
    ]
)

error_handling_chain = (
    prompt 
    | llm 
    | string_parser
)

class ErrorHandlingChain:
     
    def __init__(self):
        self.error_handling_chain = error_handling_chain
        self.chat_history = None

    def invoke(self, input_message: str | dict) -> str:
        if isinstance(input_message, str):
            result = self.error_handling_chain.invoke({"question": input_message, "chat_history": self.chat_history})
        elif isinstance(input_message, dict):
            result = self.error_handling_chain.invoke(input_message)
        
        return result