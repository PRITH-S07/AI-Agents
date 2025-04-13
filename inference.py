# inference.py
import os
from llama_index.core import VectorStoreIndex, Settings, Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.huggingface import HuggingFaceLLM
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

def load_txt_documents(folder_path):
    docs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                text = f.read()
                docs.append(Document(text=text, metadata={"filename": filename}))
    return docs

def main(volume_path="/root/data"):
    documents = load_txt_documents(os.path.join(volume_path, "cleaned_data"))

    model_name = "TheBloke/Mistral-7B-Instruct-v0.1-GPTQ"
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype=torch.float16,
        trust_remote_code=True
    )

    llm = HuggingFaceLLM(
        model=model,
        tokenizer=tokenizer,
        context_window=4096,
        max_new_tokens=512,
        tokenizer_name=model_name,
        query_wrapper_prompt="### Instruction:\n{query_str}\n\n### Response:",
        generate_kwargs={"temperature": 0.7, "do_sample": True}
    )

    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

    Settings.llm = llm
    Settings.embed_model = embed_model

    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=os.path.join(volume_path, "index"))

    print("✅ Index stored at", os.path.join(volume_path, "index"))
