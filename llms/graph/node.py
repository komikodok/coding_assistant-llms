from langchain_core.messages import HumanMessage, AIMessage

from llms.chains.conversation import ConversationChain
from llms.chains.error_handling import ErrorHandlingChain

from typing import (
    TypedDict
)


class State(TypedDict):
    question: str
    generation: str
    chat_history: list
    is_error_message: bool = False


def decide_response_category(state: State):
    is_error_message = state["is_error_message"]

    binary_score = "conversation_node" if is_error_message == False else "error_handling_node"

    return binary_score

def conversation_node(state: State):
    question = state["question"]
    chat_history = state["chat_history"]

    if chat_history is None:
        chat_history = [
            HumanMessage(content="Halo"),
            AIMessage(content="Halo juga!")
        ]

    conversation_chain = ConversationChain()
    generation = conversation_chain.invoke({"question": question, "chat_history": chat_history})

    return {
        "question": question,
        "generation": generation,
        "chat_history": chat_history
    }

def error_handling_node(state: State):
    question = state["question"]
    chat_history = state["chat_history"]

    if chat_history is None:
        chat_history = [
            HumanMessage(content="Halo"),
            AIMessage(content="Halo juga!")
        ]

    error_handling_chain = ErrorHandlingChain()
    generation = error_handling_chain.invoke({"error_message": question, "chat_history": chat_history})

    return {
        "question": question,
        "generation": generation,
        "chat_history": chat_history
    }

def insert_chat_history(state: State):
    question = state["question"]
    generation = state["generation"]
    chat_history = state["chat_history"]
    is_error_message = state["is_error_message"]

    chat_history.append(HumanMessage(content=question))
    chat_history.append(AIMessage(content=generation))

    return {
        "question": question,
        "generation": generation,
        "chat_history": chat_history,
        "is_error_message": is_error_message
    }


# -> Utilize this option if you desire a more sophisticated method. And delete is_error_message from state

# from assistant_coding.llms.chains.classifier import ClassifierChain

# def decide_response_category(state: State):
#     question = state["question"]

#     classifier_chain = ClassifierChain()
#     classifier = classifier_chain.invoke({"question": question})

#     binary_score = "conversation_node" if classifier["category"] == "conversation" else "error_handling_node"

#     return binary_score