import chromadb
from wiki import gen_rag_database

class FandomRAG:
    def __init__(self, db_path="./fandom_chroma_db"):
        """Initialize with persistent storage"""
        self.client = chromadb.PersistentClient(path=db_path)
        self.db_path = db_path
        self.collections = {}
        
        # Load existing collections on startup
        self._load_existing_collections()
    
    def _load_existing_collections(self):
        """Load all existing collections into memory"""
        try:
            existing_collections = self.client.list_collections()
            for collection_info in existing_collections:
                collection_name = collection_info.name
                if collection_name.startswith("fandom_"):
                    wiki_name = collection_name.replace("fandom_", "")
                    collection = self.client.get_collection(collection_name)
                    self.collections[wiki_name] = collection
                    print(f"Loaded existing {wiki_name} wiki with {collection.count()} documents")
        except Exception as e:
            print(f"Note: {e}")
    
    def add_wiki(self, wiki_name, documents=None):
        """Create a new collection for a specific wiki or load existing one"""
        collection_name = f"fandom_{wiki_name}"
        
        # Check if wiki already exists
        if wiki_name in self.collections:
            print(f"Wiki '{wiki_name}' already loaded with {self.collections[wiki_name].count()} documents")
            return self.collections[wiki_name]
        
        try:
            # Try to load existing collection
            collection = self.client.get_collection(collection_name)
            self.collections[wiki_name] = collection
            print(f"Loaded existing {wiki_name} wiki with {collection.count()} documents")
            return collection
            
        except Exception:
            # Collection doesn't exist, create new one
            if documents is None:
                print(f"Crawling {wiki_name} wiki...")
                documents = gen_rag_database(wiki_name)
            
            if not documents:
                print(f"No documents found for {wiki_name}")
                return None
            
            collection = self.client.create_collection(collection_name)
            
            # Add documents
            collection.add(
                documents=[doc['content'] for doc in documents],
                ids=[f"{wiki_name}_page_{i}" for i in range(len(documents))],
                metadatas=[{
                    'title': doc['title'],
                    'url': doc['url'],
                    'wiki': wiki_name
                } for doc in documents]
            )
            
            self.collections[wiki_name] = collection
            print(f"Created new {wiki_name} wiki with {len(documents)} documents")
            return collection
    
    def search_wiki(self, wiki_name, query, n_results=3):
        """Search a specific wiki"""
        if wiki_name not in self.collections:
            # Try to load the wiki if it exists in storage
            try:
                collection_name = f"fandom_{wiki_name}"
                collection = self.client.get_collection(collection_name)
                self.collections[wiki_name] = collection
                print(f"Loaded {wiki_name} wiki from storage")
            except (ValueError, Exception):
                return f"Wiki '{wiki_name}' not found. Available wikis: {self.list_wikis()}"
        
        collection = self.collections[wiki_name]
        results = collection.query(query_texts=[query], n_results=n_results)
        return results
    
    def search_all_wikis(self, query, n_results=2):
        """Search across all wikis"""
        all_results = {}
        
        # Load all available wikis if not already loaded
        existing_collections = self.client.list_collections()
        for collection_info in existing_collections:
            collection_name = collection_info.name
            if collection_name.startswith("fandom_"):
                wiki_name = collection_name.replace("fandom_", "")
                if wiki_name not in self.collections:
                    collection = self.client.get_collection(collection_name)
                    self.collections[wiki_name] = collection
        
        for wiki_name, collection in self.collections.items():
            results = collection.query(query_texts=[query], n_results=n_results)
            all_results[wiki_name] = results
        
        return all_results
    
    def list_wikis(self):
        """List all available wikis (both loaded and stored)"""
        # Get all stored collections
        try:
            existing_collections = self.client.list_collections()
            all_wikis = set()
            
            for collection_info in existing_collections:
                collection_name = collection_info.name
                if collection_name.startswith("fandom_"):
                    wiki_name = collection_name.replace("fandom_", "")
                    all_wikis.add(wiki_name)
            
            # Add currently loaded wikis
            all_wikis.update(self.collections.keys())
            
            return sorted(list(all_wikis))
        except Exception:
            return list(self.collections.keys())
    
    def delete_wiki(self, wiki_name):
        """Delete a wiki collection"""
        collection_name = f"fandom_{wiki_name}"
        
        try:
            self.client.delete_collection(collection_name)
            if wiki_name in self.collections:
                del self.collections[wiki_name]
            print(f"Deleted {wiki_name} wiki")
            return True
        except ValueError:
            print(f"Wiki '{wiki_name}' not found")
            return False
    
    def get_wiki_info(self, wiki_name):
        """Get information about a wiki"""
        if wiki_name not in self.collections:
            try:
                collection_name = f"fandom_{wiki_name}"
                collection = self.client.get_collection(collection_name)
                self.collections[wiki_name] = collection
            except ValueError:
                return f"Wiki '{wiki_name}' not found"
        
        collection = self.collections[wiki_name]
        count = collection.count()
        
        # Get sample documents
        sample = collection.get(limit=3)
        sample_titles = [meta.get('title', 'Unknown') for meta in sample['metadatas']]
        
        return {
            'name': wiki_name,
            'document_count': count,
            'sample_pages': sample_titles,
            'storage_path': self.db_path
        }


# Example usage
if __name__ == "__main__":
    # Initialize persistent RAG system
    rag = FandomRAG()
    
    # List existing wikis
    print("Available wikis:", rag.list_wikis())
    
    # Add a new wiki (or load existing)
    rag.add_wiki("minecraft")
    
    # Search
    results = rag.search_wiki("minecraft", "how to craft diamond tools")
    if not isinstance(results, str):  # Not an error message
        for i, doc in enumerate(results['documents'][0][:2]):
            metadata = results['metadatas'][0][i]
            print(f"\n{metadata['title']}:")
            print(f"Content: {doc[:200]}...")
    
    # Get wiki info
    info = rag.get_wiki_info("minecraft")
    print(f"\nWiki info: {info}")