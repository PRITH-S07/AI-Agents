from flask import Flask, request, jsonify
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.settings import Settings
import os

#Setup GPT-4o via CMU LiteLLM proxy
os.environ["OPENAI_API_KEY"] = "sk-xxxx"  # replace with your API key
os.environ["OPENAI_API_BASE"] = "https://cmu.litellm.ai/v1"

# LLM for final answer generation
llm = OpenAI(
    model="gpt-4o",
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ["OPENAI_API_BASE"]
)

# Set the global default LLM
Settings.llm = llm

# === Embedding model ===
embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")  # 384-dim

# === Load vector index ===
storage_context = StorageContext.from_defaults(persist_dir="./index_data")
index = load_index_from_storage(storage_context, embed_model=embed_model)

# === Setup Flask ===
app = Flask(__name__)

@app.route('/query', methods=['POST'])
def query_index():
    if index is None:
        return jsonify({"error": "Index not loaded"}), 500

    data = request.json
    query_text = data.get("query")
    print(f"\n🟡 Received query: {query_text}\n")

    try:
        query_engine = index.as_query_engine(
            llm=llm,
            response_mode="compact",
            system_prompt=(
                "You are an academic advisor at CMU. Given the student’s interest, past courses, and preferences "
                "(e.g., time commitment and rating), recommend 1–2 specific CMU courses. "
                "Return ONLY a valid JSON object with this format:\n\n"
                "{\n"
                "  \"courses\": [\n"
                "    {\n"
                "      \"id\": \"18-709\",\n"
                "      \"title\": \"Advanced Cloud Computing\",\n"
                "      \"description\": \"Project-based course on scalable distributed systems.\",\n"
                "      \"day\": \"Monday\",\n"
                "      \"start_time\": \"16:00\",\n"
                "      \"end_time\": \"17:50\",\n"
                "      \"location\": \"DH 2315\"\n"
                "    },\n"
                "    ...\n"
                "  ]\n"
                "}\n\n"
                "Respond with ONLY this JSON object — no explanation, no commentary."
            )
        )

        response = query_engine.query(query_text)
        print(f"\n🟢 Response: {response}\n")
        return jsonify({"response": str(response.response)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)