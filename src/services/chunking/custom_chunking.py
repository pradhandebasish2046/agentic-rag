from qdrant_client import QdrantClient,models
import fitz
import re
from uuid import uuid4
import tiktoken
import shutil
import numpy as np
import bm25s
import os
from src.utils.logger import logger

from src.constants import chunk_size,min_chunk_size

def num_tokens_from_string(string, encoding_name = "cl100k_base") -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def read_pdf(path):
    doc = fitz.open(path)
    page_text_lst = [page.get_text("text",sort=True) for page in doc]
    return page_text_lst

def split_docs(string):
    delimiters = [',', ';', '\n\n','\n','.']  # List of delimiters 

    # Create the regex pattern dynamically
    pattern = f"[^{''.join(delimiters)}]+[{'|'.join(delimiters)}]?"

    # Split using re.finditer
    matches = re.finditer(pattern, string)

    # Combine the words with their respective delimiters
    res = [match.group(0) for match in matches]
    return res

def parts_to_chunk(parts, chunk_size=chunk_size,min_chunk_size=min_chunk_size):
    chunk_1st = []
    chunk = ""
    for i in range(len(parts)): 
        sub_part = parts[i] 
        if num_tokens_from_string(sub_part+chunk) < chunk_size: 
            chunk+=sub_part 
            if i == len(parts)-1: 
                chunk_1st.append(chunk)
                break
        else:
            chunk_1st.append(chunk)
            chunk = sub_part
            if i == len(parts)-1:
                chunk_1st.append(chunk)
                break
    if num_tokens_from_string(chunk_1st[-1]) < min_chunk_size:
        last_chunk = chunk_1st.pop()
        chunk_1st[-1] = chunk_1st[-1]+last_chunk
    return chunk_1st

def find_page_break_pattern(chunk, pattern):
    next_page = False
    matches = re.finditer(pattern, chunk)
    for match in matches:
        value = int(match.group(1))
        if match.start() == 0:
            next_page = True
            return value, next_page

        return value, next_page

    return -1, False


def find_page_num(list_of_chunk_docs):
    prev_page=1
    page_details = []
    final_chunk_1st = []
    page_break_pattern = r"!@#(\d+)!@#" 
    for i in range(len(list_of_chunk_docs)):
        chunk = list_of_chunk_docs[i]#.page_content
        chunk_without_page_break = re.sub(page_break_pattern, "", chunk)
        page_num,next_page = find_page_break_pattern(chunk, page_break_pattern)

        if page_num == -1:
            page_details.append(prev_page)
            final_chunk_1st.append(chunk_without_page_break)
        else:
            if next_page:
                page_details.append(page_num+1)

                final_chunk_1st.append(chunk_without_page_break)
            else:
                page_details.append(page_num)
                final_chunk_1st.append(chunk_without_page_break)

            prev_page = page_num+1

    return final_chunk_1st,page_details

def create_docs(chunks,pages,file_name,ids):
    metadata = [] # [{'page_no':i} for i in pages]
    documents = [] # [doc for doc in chunks]
    corpus_json = []

    for doc,page_no,id in zip(chunks,pages,ids):
        documents.append(doc)
        each_metadata = {'page_no':page_no,"file_name":file_name}
        metadata.append(each_metadata)
        each_dict = {'page_content':doc,"metadata":{'page_no':page_no,"file_name":file_name,"id":id}}
        corpus_json.append(each_dict)
    return documents, metadata, corpus_json

def create_docs(chunks,pages,file_name,ids):
    metadata = [] # [{'page_no':i} for i in pages]
    documents = [] # [doc for doc in chunks]
    corpus_json = []

    for doc,page_no,id in zip(chunks,pages,ids):
        documents.append(doc)
        each_metadata = {'page_no':page_no,"file_name":file_name}
        metadata.append(each_metadata)
        each_dict = {'page_content':doc,"metadata":{'page_no':page_no,"file_name":file_name,"id":id}}
        corpus_json.append(each_dict)
    return documents, metadata, corpus_json

def final_chunking_pipeline(path):
    logger.info(f">>>>> Chunking Started >>>>>")
    page_chunk_lst = read_pdf(path)
    total_text = "".join(page_chunk_lst[i].strip("\n")+f"!@#{i+1}!@#\n" for i in range(len(page_chunk_lst)))
    logger.info(f">>>>> read_pdf Completed >>>>>")
    parts = split_docs(total_text)
    logger.info(f">>>>> Split docs Completed >>>>>")
    list_of_chunk_docs = parts_to_chunk(parts)
    logger.info(f">>>>> parts_to_chunk Completed >>>>>")
    final_chunk_1st,page_details = find_page_num(list_of_chunk_docs)
    logger.info(f">>>>> find_page_num Completed >>>>>")
    uuids = [str(uuid4()) for _ in range(len(list_of_chunk_docs))]
    documents, metadata, corpus_json = create_docs(list_of_chunk_docs,page_details,path,uuids)
    logger.info(f">>>>> create_docs Completed >>>>>")
    logger.info(f">>>>> Chunking Pipeline Completed >>>>>")
    return documents, metadata, corpus_json,uuids