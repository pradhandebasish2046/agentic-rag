import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

def extract_text_from_html(html_content):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Get the text from the parsed HTML
    plain_text = soup.get_text()

    # Strip leading/trailing whitespace and return the result
    return plain_text.strip()

def prepare_wev_search_context(response):
    web_result = response.json()['web']
    search_results = ""
    n=0
    for i in web_result['results']:
        if n == 5:
            break
        description = extract_text_from_html(i['description'])
        search_results+=description
        search_results+=f"\nSource link: {i['url']}\n----------\n"
        n+=1
    return search_results

def search(query):
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": os.getenv("brave_api_key")
    }
    params = {
        "q": query
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        search_results = prepare_wev_search_context(response)
        return search_results
    else:
        return None
