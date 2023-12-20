import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

def urlFetch(url):
    # Parse the URL
    parsed_url = urllib.parse.urlparse(url)
    # Define headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Referer': 'http://www.google.com/',
        'Upgrade-Insecure-Requests': '1',
    }
    # Use a session to persist cookies
    session = requests.Session()
    session.headers.update(headers)

    # Fetch the webpage content
    try:
        response = session.get(url)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to retrieve data from the URL due to an issue: {e}"

    # Parse the webpage with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract and return text content
    return soup.get_text()

    # Delay for a second
    time.sleep(1)
