import requests
from bs4 import BeautifulSoup
from googlesearch import search
import json
import re
import os
import json

# Function to fetch webpage content
def fetch_webpage(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        return soup
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Function to extract data where all keywords are present
def extract_data(soup, keywords):
    results = []
    for element in soup.find_all(string=True):  # Searches all text elements
        text = element.strip()
        text = re.sub(r'\s+', ' ', text)  # Clean whitespace
        if all(re.search(keyword, text, re.IGNORECASE) for keyword in keywords):  # Match all keywords
            if text not in results:  # Avoid duplicates
                results.append(text)
    return results

# Function to search Google and fetch URLs
def search_google(keywords, num_results=10):
    query = " ".join(keywords)  # Combine keywords for a single search query
    print(f"Searching Google for: {query}")
    urls = []
    try:
        for url in search(query, num=num_results, stop=num_results, lang="en"):
            urls.append(url)
    except Exception as e:
        print(f"Error during Google search: {e}")
    return urls

# Append scraped data to an existing JSON file
def save_to_json(data, output_file):
    # Check if the file already exists
    if os.path.exists(output_file):
        # Load existing data
        with open(output_file, "r") as f:
            existing_data = json.load(f)
    else:
        # If file doesn't exist, start with an empty list
        existing_data = []

    # Combine new data with existing data
    combined_data = existing_data + data

    # Remove duplicates by ensuring unique URLs
    unique_data = {item["url"]: item for item in combined_data}.values()

    # Save the updated dataset
    with open(output_file, "w") as f:
        json.dump(list(unique_data), f, indent=4)
    print(f"Appended data to {output_file}. Total entries: {len(unique_data)}")


# Main function to orchestrate the scraping
def scrape_internet(keywords, num_results=10, output_file="relevant_data.json"):
    all_results = []

    # Step 1: Search Google for relevant URLs
    urls = search_google(keywords, num_results=num_results)

    # Step 2: Scrape each URL for matching content
    for url in urls:
        print(f"Scraping {url}...")
        soup = fetch_webpage(url)
        if soup:
            matching_data = extract_data(soup, keywords)
            if matching_data:  # Save only if matching data is found
                print(f"Found {len(matching_data)} relevant snippets on {url}.")
                all_results.append({
                    "url": url,
                    "content": matching_data
                })

    # Step 3: Save all results to a file
    save_to_json(all_results, output_file)

# Entry point
if __name__ == "__main__":
    # Keywords to search for
    keywords = ["red team", "pentesting", "malware", "exploit"]

    # Number of search results to fetch from Google
    num_results = 10000000

    # Output file to save relevant data
    output_file = "/home/randompolymath/Desktop/RedRidingHoodCompany/chatbot/scraped/results.json"

    # Start scraping
    scrape_internet(keywords, num_results, output_file)
