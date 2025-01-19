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
logger.info(f">>>>> Started >>>>>")


def process_file1(pdf_file):
    # time.sleep(3)  # Simulate processing delay
    doc = fitz.open(pdf_file.path)
    total = ""
    for page in doc:
        text = page.get_text("text", sort=True)
        total+=text
    return len(total)

def process_file2(total):
    time.sleep(1)
    return total//100

qdrant_client = None
keyword_retriever = None
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
    for pdf_file in files:
        # Notify the user that processing has started for the file
        # start_msg = cl.Message(content=f"Processing `{pdf_file.name}`...")
        # await start_msg.send()

        # Process the file (this part is where the actual file processing happens)
        documents, metadata, corpus_json, uuids  = final_chunking_pipeline(pdf_file.path)
        all_documents.extend(documents)
        all_metadata.extend(metadata)
        all_corpus_json.extend(corpus_json)
        all_ids.extend(uuids)

        # Notify the user that processing has ended for the file
        # end_msg = cl.Message(content=f"Processing complete for 1`{pdf_file.name}`. It contains {len(documents),len(metadata)} chunks")
        # await end_msg.send()
        # n2 = process_file2(n)
        # end_msg = cl.Message(content=f"Processing complete for 2`{pdf_file.name}`. It contains {n2} characters on the first page.")
        # await end_msg.send()

        # Store the result for the final summary message
        # lengths.append(n)
        # final_summary.append(f"{pdf_file.name}: {n} characters on the first page.")

    logger.info(f">>>>> Chunking completed with no of chunks {len(all_documents), len(all_metadata), len(all_ids)} >>>>>")
    logger.info(f">>>>> Embedding Started >>>>>")
    msg = cl.Message(content=f"Creating Embedding...")
    await msg.send()
    global qdrant_client
    global keyword_retriever

    qdrant_client = create_qdrant_dense_emd(documents,metadata,all_ids,emd_path,collection_name)
    keyword_retriever =  create_bm25s_db(all_corpus_json)
    logger.info(f">>>>> Embedding Completed >>>>>")

    msg = cl.Message(content=f"Embedding Completed. Not you can ask question😊")
    await msg.send()

@cl.on_message
async def main(message: cl.Message):
    query = message.content
    global qdrant_client
    global keyword_retriever
    # qdrant_client = QdrantClient(path=emd_path)
    # qdrant_client.set_model("BAAI/bge-base-en-v1.5")
    
    # retrieve_context, unique_source,all_source = custom_ensemble_retriever(query=query,k=k,weights=weights,
    #                                                         client=qdrant_client,collection_name=collection_name,
    #                                                         keyword_retriever=keyword_retriever)
    logger.info(f">>>>> Retrieve started >>>>>")
    retrieve_context, unique_source,all_source = custom_ensemble_retriever(query=query,k=k,weights=weights,
                                                            client=qdrant_client,collection_name=collection_name,
                                                            keyword_retriever=keyword_retriever)

    msg = cl.Message(content=f"Retrieving Data {len(retrieve_context)} and sources {all_source}")
    await msg.send()