import bm25s
import os
from src.utils.logger import logger

def keyword_search(query,keyword_retriever,k=5):
    logger.info(f">>>>> keyword_search started >>>>>")
    # keyword_retriever = bm25s.BM25.load(path,load_corpus=True)
    query_tokens = bm25s.tokenize(query)
    results,scores = keyword_retriever.retrieve(query_tokens,k=k)
    retrieve_doc = []
    retrieve_doc_dict = {}
    rank = 1
    for doc in results[0]:
        page_content = doc['page_content']
        metadata = doc['metadata']
        retrieve_doc.append((page_content,rank))
        file_name = metadata['file_name']
        page_no = metadata['page_no']
        path = os.path.join("uploaded_files",file_name)
        source = f"{path}#page={page_no}"
        retrieve_doc_dict[page_content] = source
        rank+=1
    logger.info(f">>>>> keyword_search completed >>>>>")
    return retrieve_doc,retrieve_doc_dict