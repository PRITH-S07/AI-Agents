import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import json
from flask import Flask, request, jsonify

# Configuration
MODEL_ID = "TheBloke/Mistral-7B-Instruct-v0.1-GPTQ"  # Using GPTQ for efficiency
EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_DB_PATH = "path/to/your/vector_database.faiss"  # Replace with your actual path
DOCUMENT_LOOKUP_PATH = "path/to/your/document_lookup.pkl"  # Replace with your actual path
TOP_K = 3  # Number of documents to retrieve

class RAGPipeline:
    def __init__(self):
        # Load LLM
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            device_map="auto",
            torch_dtype=torch.float16,
            revision="main"
        )
        
        # Load embedding model
        self.embed_model = SentenceTransformer(EMBED_MODEL_ID)
        
        # Load vector database and document lookup
        self._load_vector_database()
    
    def _load_vector_database(self):
        """Load the FAISS index and document lookup from files."""
        # Load FAISS index
        self.index = faiss.read_index(VECTOR_DB_PATH)
        
        # Load document lookup (mapping from index to actual document content)
        with open(DOCUMENT_LOOKUP_PATH, 'rb') as f:
            self.documents = pickle.load(f)
    
    def _get_relevant_documents(self, query, top_k=TOP_K):
        """Retrieve relevant documents for the query."""
        # Embed the query
        query_embedding = self.embed_model.encode([query])[0]
        query_embedding = np.array([query_embedding]).astype('float32')
        
        # Search in FAISS
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Get the actual documents
        relevant_docs = [self.documents[idx] for idx in indices[0]]
        return relevant_docs
    
    def _format_prompt(self, query, documents):
        """Format the prompt for the LLM with retrieved documents."""
        context = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(documents)])
        
        prompt = f"""<s>[INST] You are a helpful AI assistant. Use the following retrieved documents to answer the user's question.
If the information to answer the query is not present in the documents, just say that you don't know based on the provided information.

Retrieved Documents:
{context}

User Query: {query} [/INST]</s>
"""
        return prompt
    
    def process_query(self, query):
        """End-to-end RAG pipeline processing."""
        # Get relevant documents
        relevant_docs = self._get_relevant_documents(query)
        
        # Format prompt with documents
        prompt = self._format_prompt(query, relevant_docs)
        
        # Generate response from LLM
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1,
            )
        
        response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        return response.strip()

# Initialize Flask app for API
app = Flask(__name__)

# Initialize RAG pipeline
rag_pipeline = None

@app.before_first_request
def initialize():
    global rag_pipeline
    rag_pipeline = RAGPipeline()

@app.route('/query', methods=['POST'])
def handle_query():
    data = request.json
    if 'query' not in data:
        return jsonify({"error": "No query provided"}), 400
    
    query = data['query']
    
    # Process the query
    response = rag_pipeline.process_query(query)
    
    return jsonify({"response": response})

# For command line testing
if __name__ == "__main__":
    # If running as a script, initialize the pipeline
    rag_pipeline = RAGPipeline()
    
    # Example: Process a query from command line
    if len(os.sys.argv) > 1:
        query = " ".join(os.sys.argv[1:])
        print(f"Query: {query}")
        response = rag_pipeline.process_query(query)
        print(f"Response: {response}")
    else:
        # Start the API server
        app.run(host='0.0.0.0', port=5000)
