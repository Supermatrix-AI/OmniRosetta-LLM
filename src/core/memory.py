from langchain.memory import ConversationBufferMemory


memory = ConversationBufferMemory(memory_key="chat_history")


def remember(query, answer):
    memory.save_context({"input": query}, {"output": answer})
