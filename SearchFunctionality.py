import requests
from bs4 import BeautifulSoup
import urllib.parse

def perform_search(engine, query, num_results):
    query = urllib.parse.quote_plus(query)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    if engine == "Google":
        url = f"https://www.google.com/search?q={query}&num={num_results}"
    elif engine == "Bing":
        url = f"https://www.bing.com/search?q={query}&count={num_results}"
    elif engine == "Baidu":
        url = f"https://www.baidu.com/s?wd={query}&rn={num_results}"
    else:
        return "Invalid search engine selected."

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if engine == "Google":
            return parse_google_results(soup, num_results)
        elif engine == "Bing":
            return parse_bing_results(soup, num_results)
        elif engine == "Baidu":
            return parse_baidu_results(soup, num_results)
        
    except requests.RequestException as e:
        return f"An error occurred: {str(e)}"

def parse_google_results(soup, num_results):
    results = []
    for div in soup.find_all('div', class_='g')[:num_results]:
        title_element = div.find('h3')
        link_element = div.find('a')
        if title_element and link_element and not div.find('span', text='Ad'):
            results.append({
                'title': title_element.text,
                'link': link_element['href']
            })
    return results

def parse_bing_results(soup, num_results):
    results = []
    for li in soup.find_all('li', class_='b_algo')[:num_results]:
        title_element = li.find('h2')
        link_element = li.find('a')
        if title_element and link_element and not li.find('span', class_='b_adSlug'):
            results.append({
                'title': title_element.text,
                'link': link_element['href']
            })
    return results

def parse_baidu_results(soup, num_results):
    results = []
    for div in soup.find_all('div', class_=lambda x: x and x.startswith('result c-container'))[:num_results]:
        title_element = div.find('h3', class_='t')
        link_element = title_element.find('a') if title_element else None
        if title_element and link_element and not div.find('span', class_='c-icon c-icon-bear-p'):
            results.append({
                'title': title_element.text.strip(),
                'link': link_element['href']
            })
    return results

def compile_results(all_results):
    compiled_results = []
    seen_links = set()
    
    for engine, results in all_results.items():
        for result in results:
            if result['link'] not in seen_links:
                result['engine'] = engine
                compiled_results.append(result)
                seen_links.add(result['link'])
    
    return compiled_results

if __name__ == "__main__":
    engine = input("Enter search engine (Google, Bing, DuckDuckGo, or Baidu): ")
    query = input("Enter your search query: ")
    num_results = int(input("Enter number of results to fetch: "))
    results = perform_search(engine, query, num_results)
    
    if isinstance(results, list):
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Title: {result['title']}")
            print(f"Link: {result['link']}")
    else:
        print(results)  # Print error message