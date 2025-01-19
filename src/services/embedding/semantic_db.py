from qdrant_client import QdrantClient,models
import shutil
import os
from src.utils.logger import logger

def create_qdrant_dense_emd(documents,metadata,ids,emd_path,collection_name):
    logger.info(f">>>>> create_qdrant_dense_emd started >>>>>")
    if os.path.exists(emd_path): 
        shutil.rmtree(emd_path)

    client = QdrantClient(path = emd_path)
    client.set_model("BAAI/bge-base-en-v1.5")

    if not client.collection_exists("startups"):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=client.get_fastembed_vector_params()
        )
    # uuids = [str(uuid4()) for _ in range(len(chunks))]

    # metadata = [{'page_no':i} for i in pages]
    # documents = [doc for doc in chunks]

    client.add(
    collection_name=collection_name,
    documents=documents,
    metadata=metadata,
    ids=ids,
    parallel=0,  # Use all available CPU cores to encode data.
    # Requires wrapping code into if __name__ == '__main__' block
    )
    logger.info(f">>>>> create_qdrant_dense_emd completed >>>>>")
    return client