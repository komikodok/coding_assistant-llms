from langchain_community.chat_models.ollama import ChatOllama
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import Field, BaseModel

import json
from typing import Literal, Dict


with open("config.json", "r") as f:
    config = json.load(f)

model_config = config["model"]

llm = ChatOllama(model=model_config["repo_id"])

class Classifier(BaseModel):
        
        category: Literal["conversation", "error_handling"] = Field( 
            description="Classify the user input. Respond with either 'conversation' or 'error_handling'"
        )


json_parser = JsonOutputParser(pydantic_object=Classifier)
template = """
            You are a classifier that determines whether the user input is a conversation starter or a program error. \
            Restrict yourself to a binary classification. If the input seems to be a question, chat, or request for information except program code, classify it as 'conversation'. \
            If the input seems to indicate an error in code, classify it as 'error_handling'. \
            
            Format instructions: {format_instructions}. \
            Example instructions: {example_instructions}. \
"""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", template),
        ("human", "Question: {question}")
    ]
)

format_prompt = prompt.partial(
    format_instructions=json_parser.get_format_instructions(),
    example_instructions="""{"category": "conversation"} or {"category": "error_handling"}""")


classifier_chain = (
    format_prompt 
    | llm 
    | json_parser
)

class ClassifierChain:
     
    def __init__(self):
        self.classifier_chain = classifier_chain

    def invoke(self, input_message: str | dict) -> dict:
        if isinstance(input_message, str):
            result = self.classifier_chain.invoke({"question": input_message})
        elif isinstance(input_message, dict):
            result = self.classifier_chain.invoke(input_message)
        
        return result
