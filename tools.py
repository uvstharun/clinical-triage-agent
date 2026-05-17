import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()



embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

chroma_client = chromadb.PersistentClient(path="docs/chroma_db")

collection = chroma_client.get_collection(
    name="clinical_guidelines",
    embedding_function=embedding_fn
)

print("Clinical guidelines loaded. RAG tool ready.")


def search_clinical_guidelines(query: str, n_results: int = 3) -> str:
    """
    Search clinical guidelines for relevant information.
    
    This function is called by Node 3a, 3b, and 3c depending
    on the urgency level. Each node passes a different query
    tailored to its urgency context.
    
    Args:
        query: Plain English search query
        n_results: Number of chunks to retrieve (default 3)
    
    Returns:
        Formatted string of relevant guideline chunks
    """
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    if not results["documents"][0]:
        return "No relevant guidelines found."

    output = ""
    for doc, metadata in zip(
        results["documents"][0],
        results["metadatas"][0]
    ):
        output += f"\n[Source: {metadata['source']}]\n{doc}\n"

    return output




if __name__ == "__main__":
    print("\nTesting RAG tool...\n")

    test_queries = [
        "emergency treatment for diabetes hyperglycemia",
        "statin therapy guidelines for cholesterol",
        "dietary management for type 2 diabetes"
    ]

    for query in test_queries:
        print(f"Query: {query}")
        result = search_clinical_guidelines(query)
        print(f"Result preview: {result[:150]}...")
        print()