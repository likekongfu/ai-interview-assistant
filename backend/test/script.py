from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# 读取所有md
md_files = list(
    Path(r"D:\javaguide\JavaGuide\docs").rglob("*.md")
)

print("md数量:", len(md_files))

docs = []

for file in md_files:
    loader = TextLoader(str(file), encoding="utf-8")
    docs.extend(loader.load())

print("文档数量:", len(docs))

# 切块
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)

chunks = splitter.split_documents(docs)

print("chunk数量:", len(chunks))

# 存入chroma
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=OllamaEmbeddings(model="bge-m3"),
    collection_name="java_guide",
    persist_directory="./chroma_db"
)

print("向量库创建成功")
