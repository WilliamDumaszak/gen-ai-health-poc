from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict
from news import fetch_news

# Pasta onde o vector store será salvo
VECTORSTORE_DIR = Path(__file__).parent.parent / "vectorstore"

# Inicializa ChromaDB local
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=str(VECTORSTORE_DIR)
))
collection = client.get_or_create_collection("news_srag")

# Divisor de texto
splitter = CharacterTextSplitter(chunk_size=800, chunk_overlap=100)

# Embeddings OpenAI
emb_model = OpenAIEmbeddings()

def index_articles(articles: List[Dict]):
    """
    Recebe lista de notícias formatadas (fetch_news) e indexa no Chroma.
    """
    texts = []
    metadatas = []
    ids = []

    for a in articles:
        content = a.get("content") or a.get("title") or ""
        if not content.strip():
            continue
        chunks = splitter.split_text(content)
        for i, chunk in enumerate(chunks):
            texts.append(chunk)
            ids.append(f"{a['id']}_{i}")  # id único por chunk
            metadatas.append({
                "title": a.get("title"),
                "url": a.get("url"),
                "published": a.get("published")
            })

    if texts:
        collection.add(documents=texts, metadatas=metadatas, ids=ids)
        client.persist()
        print(f"{len(texts)} chunks indexados no vectorstore.")

def retrieve(query: str, k: int = 5) -> List[Dict]:
    """
    Recupera os k chunks mais relevantes para a query.
    """
    results = collection.query(query_texts=[query], n_results=k)
    # Retorna lista de dicionários com texto + metadados
    output = []
    for text, meta in zip(results['documents'][0], results['metadatas'][0]):
        output.append({"text": text, "metadata": meta})
    return output

def index_latest_news(days: int = 7):
    """
    Função utilitária que busca notícias recentes e já indexa.
    """
    articles = fetch_news(days=days)
    index_articles(articles)
    return len(articles)