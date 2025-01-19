import chainlit as cl
from src.services.final_pipeline import generate_response
from io import BytesIO
import fitz
import time
from src.services.chunking.custom_chunking import final_chunking_pipeline
from src.services.embedding.semantic_db import create_qdrant_dense_emd
from src.services.embedding.keyword_db import create_bm25s_db
from src.services.retriever.ensemble_retriever import custom_ensemble_retriever
from src.constants import *
from qdrant_client import QdrantClient,models
from src.utils.logger import logger
from src.utils.helpers import update_qa_dict
from collections import OrderedDict
from src.services.llm.prompt import create_prompt_without_history,create_prompt_with_history,modify_query
from src.services.llm.llm_call import llm_call
from src.services.web_search.web_search import search
from src.utils.helpers import extract_source_pdf

logger.info(f">>>>> Started >>>>>")

qdrant_client = None
keyword_retriever = None
chat_history = OrderedDict()
uploaded_files_path,uploaded_files_name = [],[]
@cl.on_chat_start
async def start():
    # Wait for the user to upload files
    files = await cl.AskFileMessage(
        content="Please upload one or more PDF files to begin!",
        accept=["application/pdf"],
        max_size_mb=20,
        max_files=10
    ).send()

    # Initialize a list to hold lengths of text from the first page of each PDF
    lengths = []
    final_summary = []

    # Process each file as soon as it's uploaded
    msg = cl.Message(content=f"Processing `{len(files)}` files...")
    await msg.send()
    all_documents,all_metadata,all_corpus_json,all_ids = [],[],[],[]
    logger.info(f">>>>> Chunking Started >>>>>")

    global uploaded_files_name
    global uploaded_files_path

    for pdf_file in files:
        uploaded_files_name.append(pdf_file.name)
        uploaded_files_path.append(pdf_file.path)
        documents, metadata, corpus_json, uuids  = final_chunking_pipeline(pdf_file.path)
        all_documents.extend(documents)
        all_metadata.extend(metadata)
        all_corpus_json.extend(corpus_json)
        all_ids.extend(uuids)

    logger.info(f">>>>> Chunking completed with no of chunks {len(all_documents), len(all_metadata), len(all_ids)} >>>>>")
    logger.info(f">>>>> Embedding Started >>>>>")
    msg = cl.Message(content=f"Creating Embedding...")
    await msg.send()
    global qdrant_client
    global keyword_retriever

    qdrant_client = create_qdrant_dense_emd(documents,metadata,all_ids,emd_path,collection_name)
    keyword_retriever =  create_bm25s_db(all_corpus_json)
    logger.info(f">>>>> Embedding Completed >>>>>")

    msg = cl.Message(content=f"Embedding Completed. Now you can ask question😊")
    await msg.send()

@cl.on_message
async def main(message: cl.Message):
    query = message.content
    global qdrant_client
    global keyword_retriever
    global chat_history
    global uploaded_files_path
    global uploaded_files_name

    logger.info(f">>>>> Chat History {chat_history} >>>>>")
    # qdrant_client = QdrantClient(path=emd_path)
    # qdrant_client.set_model("BAAI/bge-base-en-v1.5")
    
    # retrieve_context, unique_source,all_source = custom_ensemble_retriever(query=query,k=k,weights=weights,
    #                                                         client=qdrant_client,collection_name=collection_name,
    #                                                         keyword_retriever=keyword_retriever)
    logger.info(f">>>>> Retrieve started >>>>>")
    msg = cl.Message(content="Thinking ...")
    await msg.send()
    
    if len(chat_history) == 0:
        logger.info(f">>>>> Retrieving without history >>>>>")

        retrieve_context, unique_source,all_source = custom_ensemble_retriever(query=query,k=k,weights=weights,
                                                                client=qdrant_client,collection_name=collection_name,
                                                                keyword_retriever=keyword_retriever)
        logger.info(f">>>>> Sources {all_source} >>>>>")
        prompt_without_history = create_prompt_without_history(query,retrieve_context)
        answer = llm_call(prompt_without_history)
        if "no information is available" in answer.lower() or "no information available" in answer.lower():
            logger.info(f">>>>> Searching in Web >>>>>")
            msg = cl.Message(content="Did not find the answer inside uploaded pdfs. Searching in web😊😊")
            await msg.send()
            search_results = search(query)
            if search_results is not None:
                prompt_without_history = create_prompt_without_history(query,search_results)
                answer = llm_call(prompt_without_history)
            else:
                answer = "Error while searching in web"
        else:
            # logger.info(f">>>>> uploaded_files_path {uploaded_files_path} >>>>>")
            # all_elements = []
            for each_source in all_source:
                file_source = each_source.split("#")[0]
                if file_source in uploaded_files_path:
                    index = uploaded_files_path.index(file_source)
                    pdf_file_name = uploaded_files_name[index]
                    # pdf_file_name = os.path.basename(each_source)
                    _,page_number = extract_source_pdf(each_source)
                    # logger.info(f">>>>> PDF NAME {pdf_file_name} {page_number} {each_source}>>>>>")
                
                    if (pdf_file_name is not None) and (page_number is not None):
                        element = [cl.Pdf(name=pdf_file_name, display="side", path=file_source, page=page_number)]
                        # all_elements.append(element)
                        await cl.Message(content=f"Source {pdf_file_name}", elements=element).send()
                        break


        chat_history = update_qa_dict(query, answer, chat_history, no_of_chat_history_pair)
        msg = cl.Message(content=answer)
        await msg.send()
    else:
        logger.info(f">>>>> Retrieving with history >>>>>")
        modified_query = modify_query(query,chat_history)
        logger.info(f">>>>> Modified Query {modified_query} >>>>>")
        retrieve_context, unique_source,all_source = custom_ensemble_retriever(query=modified_query,k=k,weights=weights,
                                                                client=qdrant_client,collection_name=collection_name,
                                                                keyword_retriever=keyword_retriever)
        
        logger.info(f">>>>> Sources {all_source} >>>>>")
        prompt_with_history = create_prompt_with_history(modified_query,chat_history,retrieve_context)
        logger.info(f">>>>> prompt_with_history {prompt_with_history} >>>>>")
        answer = llm_call(prompt_with_history)
        if "no information is available" in answer.lower() or "no information available" in answer.lower():
            logger.info(f">>>>> Searching in Web >>>>>")
            msg = cl.Message(content="Did not find the answer inside uploaded pdfs. Searching in web😊😊")
            await msg.send()
            search_results = search(query)
            if search_results is not None:
                prompt_without_history = create_prompt_without_history(query,search_results)
                answer = llm_call(prompt_without_history)
            else:
                answer = "Error while searching in web"

        else:
            # logger.info(f">>>>> uploaded_files_path {uploaded_files_path} >>>>>")
            # all_elements = []
            for each_source in all_source:
                file_source = each_source.split("#")[0]
                if file_source in uploaded_files_path:
                    index = uploaded_files_path.index(file_source)
                    pdf_file_name = uploaded_files_name[index]
                    logger.info(f">>>>> PDF NAME {pdf_file_name} >>>>>")
                    # pdf_file_name = os.path.basename(each_source)
                    _,page_number = extract_source_pdf(each_source)
                
                    if (pdf_file_name is not None) and (page_number is not None):
                        element = [cl.Pdf(name=pdf_file_name, display="side", path=file_source, page=page_number)]
                        # all_elements.append(element)
                        await cl.Message(content=f"Source {pdf_file_name}", elements=element).send()
                        break
        
        chat_history = update_qa_dict(modified_query, answer, chat_history, no_of_chat_history_pair)
        msg = cl.Message(content=answer)
        await msg.send()
