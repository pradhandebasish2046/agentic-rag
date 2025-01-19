from src.utils.logger import logger
from src.services.llm.llm_call import llm_call

def create_chat_history_modify_question(current_question,chat_history):
    logger.info(f">>>>>> Inside create_chat_history_modify_question function with chat history {chat_history}<<<<<<")
    i=0
    chat_history_prompt = """### Chat History: \n\n"""
    for question, answer in chat_history.items():
        answer = answer.strip("\n")
        chat_history_prompt+=f"User: {question}\nAssistant: {answer}\n\n"
        i+=1

    chat_history_prompt = chat_history_prompt+f"User: {question}"
    chat_history_prompt = chat_history_prompt+f"\n\n### Latest User Question:\n{current_question}"
    logger.info(f">>>>>> Chat History {chat_history_prompt}<<<<<<")

    return chat_history_prompt

def modify_query(query,chat_history):
    chat_history = create_chat_history_modify_question(query,chat_history)
    messages = [
        {"role": "system", "content": "Given a chat history and the latest user question which might reference context in the chat history, formulate a standalone question which can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is without any preamble and comments."},
        {"role": "user", "content": chat_history}
    ]
    final_modified_question = llm_call(messages)
    return final_modified_question

def create_prompt_without_history(curr_query,context):
    messages = [
        {"role": "system", "content": "Your task is to analyze the users query and give the answer crisply based on the given context with source link if available. If you can not find the answer politely say 'No information is available to generate the answer' "},
        {"role": "user", "content": f"Here is the user query\n{curr_query}\nHere is the relevant context separated by -----------------\n{context}"}
    ]
    logger.info(f">>>>>> Message without history {messages}<<<<<<")

    return messages

def create_prompt_with_history(curr_query,chat_history,context):
    messages = [
        {"role": "system", "content": "Your task is to analyze the users query and give the answer crisply based on the given context. If you can not find the answer politely say 'No information is available to generate the answer' "},
    ]
    for question, answer in chat_history.items():


        messages.append({"role": "user", "content": question})
        messages.append({"role": "assistant", "content": answer})
    messages.append({"role": "user", "content": f"Here is the user query\n{curr_query}\nHere is the relevant context separated by -----------------\n{context}"})

    logger.info(f">>>>>> Message with history {messages}<<<<<<")
    return messages

    
    

