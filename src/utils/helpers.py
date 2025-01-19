from collections import OrderedDict
import re

def update_qa_dict(question, answer, qa_dict, n):
    if not isinstance(qa_dict, OrderedDict):
        raise TypeError("qa_dict must be an OrderedDict.")

    if len(qa_dict) >= n:
        qa_dict.popitem(last=False)  # Remove the first (oldest) item.
    
    qa_dict[question] = answer  # Add the new question-answer pair.
    return qa_dict


def extract_source_pdf(source):
    try:
        pattern = r'([^/]+\.pdf)#page=(\d+)'

        match = re.search(pattern, source)

        if match:
            pdf_file_name = match.group(1)
            page_number = int(match.group(2))
            return pdf_file_name,page_number
        else:
            return None,None
    except Exception as e:
        return None,None