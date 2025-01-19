import bm25s
def create_bm25s_db(corpus_json):
    corpus_text = [doc['page_content'] for doc in corpus_json]
    corpus_tokens = bm25s.tokenize(corpus_text,stopwords='en')
    retriever = bm25s.BM25(corpus=corpus_json)
    retriever.index(corpus_tokens)
    return retriever