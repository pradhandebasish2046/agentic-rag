from src.services.retriever.keyword_retriever import keyword_search
from src.services.retriever.dense_retriever import similarity_search
import numpy as np
from src.utils.logger import logger


def weighted_rrf(rank_lists, weights, alpha=60, default_rank=1000, k=5):
    all_items = set(item for rank_list in rank_lists for item,_ in rank_list)
    item_to_index = {item: idx for idx, item in enumerate(all_items)}
    rank_matrix = np.full((len(all_items), len(rank_lists)), default_rank)
    for list_idx, rank_list in enumerate(rank_lists):
        for item, rank in rank_list:
            rank_matrix[item_to_index[item], list_idx] = rank

    weighted_rrf_scores = np.sum(weights*(1.0/(alpha + rank_matrix)), axis=1)
    sorted_indices = np.argsort(-weighted_rrf_scores) # Negative for descending order
    sorted_items = [(list(item_to_index.keys()) [idx], weighted_rrf_scores [idx]) for idx in sorted_indices]

    return sorted_items[:k]


def get_doc_and_source(rrf_retriever, retrieve_doc_dict_keyword, retrieve_doc_dict_sim_search):
    final_retrieve_lst = []
    unique_source = []
    all_source= []

    for final_retrieve_doc_with_score in rrf_retriever:
        final_retrieve_doc = final_retrieve_doc_with_score[0]
        final_retrieve_lst.append(final_retrieve_doc)

        if final_retrieve_doc in list(retrieve_doc_dict_keyword.keys()): 
            source = retrieve_doc_dict_keyword[final_retrieve_doc]
            all_source.append(source)
            if source not in unique_source:
                unique_source.append(source)

        elif final_retrieve_doc in list(retrieve_doc_dict_sim_search.keys()):
            source = retrieve_doc_dict_sim_search[final_retrieve_doc] 
            all_source.append(source) 
            if source not in unique_source:
                unique_source.append(source) 
    return final_retrieve_lst, unique_source, all_source


def prepare_retrieve_doc(final_retrieve_lst,all_source):
    i = 1
    context = ""
    for doc,source in zip(final_retrieve_lst,all_source):
        context += doc.strip("\n")
        context += "\n-----------------\n"
        i+=1
    return context.strip("\n")

def custom_ensemble_retriever (query,k, weights,client,collection_name,keyword_retriever):
    logger.info(f">>>>> custom_ensemble_retriever Started >>>>>")
    retrieve_doc_sim_search, retrieve_doc_dict_sim_search = similarity_search(query,client,collection_name,k=5)
    retrieve_doc_keyword, retrieve_doc_dict_keyword = keyword_search(query,keyword_retriever)

    weights = np.array(weights)
    rrf_retriever = weighted_rrf([retrieve_doc_keyword, retrieve_doc_sim_search], weights, k=k)
    final_retrieve_lst, unique_source, all_source = get_doc_and_source(rrf_retriever, retrieve_doc_dict_keyword, retrieve_doc_dict_sim_search) 
    retrieve_context = prepare_retrieve_doc(final_retrieve_lst, all_source)
    logger.info(f">>>>> custom_ensemble_retriever Completed >>>>>")

    return retrieve_context, unique_source,all_source