from qdrant_client import QdrantClient,models
import shutil
import os
import asyncio
from src.utils.logger import logger

def create_qdrant_dense_emd(documents,metadata,ids,client,collection_name):
    logger.info(f">>>>> create_qdrant_dense_emd started >>>>>")
    
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=client.get_fastembed_vector_params()
        )
    batch_size = 100 
    total_docs = len(documents) 
    logger.info(f">>>>> started batching >>>>>")
    for i in range(0, total_docs, batch_size): 
        batch_documents = documents[i:i + batch_size] 
        batch_metadata = metadata[i:i + batch_size] 
        batch_ids = ids[i:i + batch_size]

        client.add(
        collection_name=collection_name,
        documents=batch_documents,
        metadata=batch_metadata,
        ids=batch_ids,
        parallel=0,  # Use all available CPU cores to encode data.
        # Requires wrapping code into if __name__ == '__main__' block
        )
        logger.info(f">>>>> Batch completed {i} >>>>>")
    logger.info(f">>>>> create_qdrant_dense_emd completed >>>>>")
    return client