import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

documents = []

doc_path = "documents"

for file in os.listdir(doc_path):

    loader = TextLoader(os.path.join(doc_path, file))
    documents.extend(loader.load())


splitter = CharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

texts = splitter.split_documents(documents)


embeddings = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"
)


db = Chroma.from_documents(
    texts,
    embeddings,
    persist_directory="chroma_db"
)

db.persist()

print("Documents successfully converted to vectors")