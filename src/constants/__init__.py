import os
qdrant_store_path = os.path.join("kb_store","qdrant")
bm25s_store_path = os.path.join("kb_store","bm25s")

chunk_size=300
min_chunk_size=50

emd_path = os.path.join("kb_store","qdrant")
# keyword_path = "kb_store/bm25s"
collection_name = "startups"

k = 5
weights = [0.6,0.5]

no_of_chat_history_pair = 3