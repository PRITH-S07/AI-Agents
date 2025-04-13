from llama_index.core import StorageContext, load_index_from_storage

# Re-load the saved index from disk
storage_context = StorageContext.from_defaults(persist_dir="stored_index")
index_1 = load_index_from_storage(storage_context)

# Now you can use it to query
query_engine = index_1.as_query_engine()
response = query_engine.query("What is the grading policy?")
print(response)
