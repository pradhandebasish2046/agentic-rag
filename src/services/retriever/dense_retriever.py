import os
from src.utils.logger import logger

def similarity_search(query,client,collection_name,k=5):
    logger.info(f">>>>> similarity_search started >>>>>")
    retrieve_doc = []
    retrieve_doc_dict = {}
    retrieve_docs = client.query(collection_name = collection_name,query_text = query,limit = k)
    rank = 1
    for doc in retrieve_docs:
        id = doc.id
        page_content = doc.metadata['document']
        metadata = {'id':id,'page_no':doc.metadata['page_no'],'file_name':doc.metadata['file_name']}
        retrieve_doc.append((page_content,rank))
        file_name = metadata['file_name']
        page_no = metadata['page_no']
        path = os.path.join("uploaded_files",file_name)
        source = f"{path}#page={page_no}"
        retrieve_doc_dict[page_content] = source
        rank+=1

    logger.info(f">>>>> similarity_search completed >>>>>")
    return retrieve_doc,retrieve_doc_dict