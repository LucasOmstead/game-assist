import requests
import time
from collections import deque
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup
import os 
from dotenv import load_dotenv
load_dotenv()

def gen_rag_database(wiki_name):
    """
    Crawl a Fandom wiki using BFS to collect documents
    
    Args:
        wiki_name (str): The wiki name (e.g., 'minecraft' for minecraft.fandom.com)
    
    Returns:
        list: List of dictionaries containing document data
    """
    
    def get_fandom_documents(wiki_name):
        """
        Use Fandom API and BFS to download wiki documents
        
        Args:
            wiki_name (str): Wiki name (e.g., 'minecraft')
            max_documents (int): Maximum number of documents to fetch
            rate_limit_delay (float): Delay between requests (0.33 = 3 req/sec)
        
        Returns:
            list: List of document dictionaries with 'title', 'content', 'url'
        """
        rate_limit_delay = 1.0 / int(os.getenv('DOCS_PER_SECOND', '1'))  
        max_documents = int(os.getenv('MAX_DOCS', '100'))
        base_url = f"https://{wiki_name}.fandom.com"
        api_url = f"{base_url}/api.php"
        
        # Start with main page
        start_url = f"{base_url}/wiki/Main_Page"
        
        # BFS setup
        queue = deque([start_url])
        visited = set()
        documents = []
        
        print(f"Starting crawl of {base_url}...")
        
        while queue and len(documents) < max_documents:
            current_url = queue.popleft()
            
            # Skip if already visited
            if current_url in visited:
                continue
                
            visited.add(current_url)
            
            try:
                # Rate limiting
                time.sleep(rate_limit_delay)
                
                print(f"Processing: {current_url}")
                
                # Get page content
                response = requests.get(current_url, timeout=10)
                response.raise_for_status()
                
                # Handle redirects - use final URL
                final_url = response.url
                if final_url != current_url:
                    # Add final URL to visited set to avoid reprocessing
                    visited.add(final_url)
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract page title
                title_elem = soup.find('h1', {'class': 'page-header__title'}) or soup.find('title')
                title = title_elem.get_text().strip() if title_elem else "Unknown"
                
                # Extract main content
                content_elem = soup.find('div', {'class': 'mw-parser-output'}) or soup.find('div', {'id': 'content'})
                if content_elem:
                    # Remove unwanted elements
                    for unwanted in content_elem.find_all(['script', 'style', 'nav', 'aside']):
                        unwanted.decompose()
                    
                    content = content_elem.get_text(strip=True, separator=' ')
                    
                    # Only add if content is substantial
                    if len(content) > 100:
                        documents.append({
                            'title': title,
                            'content': content,
                            'url': final_url  # Use final URL after redirects
                        })
                        print(f"Added document {len(documents)}: {title}")
                
                # Find new links for BFS
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    
                    # Convert relative links to absolute
                    full_url = urljoin(current_url, href)
                    parsed_url = urlparse(full_url)
                    
                    # Normalize URL (remove fragments and query params)
                    clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                    
                    # Only follow links within the same fandom wiki
                    if (parsed_url.netloc == f"{wiki_name}.fandom.com" and 
                        parsed_url.path.startswith('/wiki/') and
                        clean_url not in visited and
                        clean_url not in [url for url in queue]):  # Check queue properly
                        
                        # Ignore file uploads, special pages, and external links
                        if not any(ignore in parsed_url.path.lower() for ignore in 
                                 ['file:', 'category:', 'template:', 'special:', 'user:', 'talk:', 'help:', 'mediawiki:']):
                            queue.append(clean_url)
                            print(f"  Added to queue: {clean_url}")
                
            except Exception as e:
                print(f"Error processing {current_url}: {e}")
                continue
        
        print(f"Crawl complete. Collected {len(documents)} documents.")
        return documents
    
    # Call the crawling function
    return get_fandom_documents(wiki_name)


# Example usage
if __name__ == "__main__":
    # Test the function
    documents = gen_rag_database("minecraft")
    
    print(f"\nCollected {len(documents)} documents:")
    for i, doc in enumerate(documents[:3]):  # Show first 3
        print(f"\n{i+1}. {doc['title']}")
        print(f"   URL: {doc['url']}")
        print(f"   Content preview: {doc['content'][:200]}...")