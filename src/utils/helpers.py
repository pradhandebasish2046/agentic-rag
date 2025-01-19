from collections import OrderedDict

def update_qa_dict(question, answer, qa_dict, n):
    if not isinstance(qa_dict, OrderedDict):
        raise TypeError("qa_dict must be an OrderedDict.")

    if len(qa_dict) >= n:
        qa_dict.popitem(last=False)  # Remove the first (oldest) item.
    
    qa_dict[question] = answer  # Add the new question-answer pair.
    return qa_dict