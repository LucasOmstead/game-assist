from flask import Flask, request, jsonify
import os
from openai import OpenAI
from fandom_rag import FandomRAG
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
db = FandomRAG()

@app.route('/search-wiki')
def search_wiki():
    wiki_name = request.args.get('wiki_name')
    query = request.args.get('query')
    
    db.add_wiki(wiki_name=wiki_name)
    results = db.search_wiki(wiki_name=wiki_name, query=query, n_results=5)
    
    if isinstance(results, str):
        return jsonify({"error": results})

    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    
    context_parts = []
    for i, (doc, metadata) in enumerate(zip(documents, metadatas), 1):
        title = metadata.get('title', 'Unknown Page')
        content_preview = doc[:500]
        context_parts.append(f"Document {i} - {title}:\n{content_preview}")
    
    context = "\n\n".join(context_parts)
    
    prompt = f"""Here are {len(documents)} documents from the {wiki_name} wiki. Answer the following question based on this information:

{context}

Question: {query}"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Answer questions based on the provided wiki documents. Be concise and accurate."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )
    
    answer = response.choices[0].message.content.strip()
    
    return jsonify({
        "wiki": wiki_name,
        "query": query,
        "answer": answer,
        "sources": len(documents)
    })

@app.route('/gen-rag-database') 
def get_new_database():
    wiki_name = request.args.get('wiki_name')
    db.add_wiki(wiki_name=wiki_name)
    return jsonify({"message": f"RAG database for {wiki_name} created/loaded."})

if __name__ == '__main__':
    app.run(debug=True)
