import chromadb
from fandom_rag import FandomRAG

def print_collection_documents(collection_name, limit=10):
    """
    Print the first 200 characters of each document in a ChromaDB collection
    
    Args:
        collection_name (str): Name of the collection (e.g., 'fandom_minecraft')
        limit (int): Maximum number of documents to display
    """
    
    try:
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(path="./fandom_chroma_db")
        
        # Get the collection
        collection = client.get_collection(collection_name)
        
        # Get all documents (or up to limit)
        results = collection.get(limit=limit)
        
        print(f"Collection: {collection_name}")
        print(f"Total documents in collection: {collection.count()}")
        print(f"Showing first {len(results['documents'])} documents:")
        print("=" * 80)
        
        # Print each document
        for i, (doc, metadata, doc_id) in enumerate(zip(results['documents'], results['metadatas'], results['ids'])):
            title = metadata.get('title', 'Unknown Title')
            url = metadata.get('url', 'No URL')
            
            print(f"\nDocument {i+1}:")
            print(f"ID: {doc_id}")
            print(f"Title: {title}")
            print(f"URL: {url}")
            print(f"Content (first 200 chars): {doc[:200]}...")
            print("-" * 40)
            
    except Exception as e:
        print(f"Error: {e}")
        
        # List available collections
        try:
            collections = client.list_collections()
            print(f"\nAvailable collections:")
            for col in collections:
                print(f"  - {col.name}")
        except:
            print("Could not list collections")

def print_fandom_wiki(wiki_name, limit=10):
    """
    Print documents from a fandom wiki using the FandomRAG class
    
    Args:
        wiki_name (str): Wiki name without 'fandom_' prefix (e.g., 'minecraft')
        limit (int): Maximum number of documents to display
    """
    
    collection_name = f"fandom_{wiki_name}"
    print(f"Looking for wiki: {wiki_name}")
    print_collection_documents(collection_name, limit)

def list_all_collections():
    """List all available collections in the database"""
    
    try:
        client = chromadb.PersistentClient(path="./fandom_chroma_db")
        collections = client.list_collections()
        
        print("Available collections:")
        for col in collections:
            count = col.count() if hasattr(col, 'count') else "Unknown"
            print(f"  - {col.name} ({count} documents)")
            
    except Exception as e:
        print(f"Error listing collections: {e}")

if __name__ == "__main__":
    # Example usage
    
    print("=== ChromaDB Collection Browser ===\n")
    
    # List all collections first
    list_all_collections()
    
    print("\n" + "="*50 + "\n")
    
    # Print documents from minecraft wiki (change this to your wiki)
    wiki_name = input("Enter wiki name (e.g., 'minecraft'): ").strip()
    
    if wiki_name:
        limit = input("Enter number of documents to show (default 5): ").strip()
        limit = int(limit) if limit.isdigit() else 5
        
        print_fandom_wiki(wiki_name, limit)
    else:
        print("No wiki name provided. Showing example with minecraft:")
        print_fandom_wiki("minecraft", 5)