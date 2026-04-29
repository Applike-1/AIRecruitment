import os
import json
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
import numpy as np
from langchain_community.vectorstores import Chroma

class SimpleEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [self._embed_text(text) for text in texts]
    
    def embed_query(self, text):
        return self._embed_text(text)
    
    def _embed_text(self, text):
        # 简单的字符计数embedding
        vector = np.zeros(100)
        for i, char in enumerate(text[:100]):
            vector[i] = ord(char) % 256
        return vector.tolist()

class VectorStoreBuilder:
    def __init__(self):
        self.documents_dir = os.path.join(os.path.dirname(__file__), 'documents')
        self.vector_store_dir = os.path.join(os.path.dirname(__file__), 'vector_store')
        os.makedirs(self.vector_store_dir, exist_ok=True)

    def load_documents(self):
        documents = []
        for filename in os.listdir(self.documents_dir):
            if filename.endswith('.txt'):
                file_path = os.path.join(self.documents_dir, filename)
                loader = TextLoader(file_path, encoding='utf-8')
                docs = loader.load()
                for doc in docs:
                    doc.metadata['filename'] = filename
                documents.extend(docs)
        return documents

    def split_documents(self, documents):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        return text_splitter.split_documents(documents)

    def create_embeddings(self):
        return SimpleEmbeddings()

    def build_vector_store(self):
        documents = self.load_documents()
        split_docs = self.split_documents(documents)
        embeddings = self.create_embeddings()

        vector_store = Chroma.from_documents(
            documents=split_docs,
            embedding=embeddings,
            persist_directory=self.vector_store_dir
        )

        vector_store.persist()
        print(f'向量存储构建完成，共存储 {len(split_docs)} 个文本块')
        return vector_store

    def test_retrieval(self, query, k=3):
        embeddings = self.create_embeddings()
        vector_store = Chroma(
            persist_directory=self.vector_store_dir,
            embedding_function=embeddings
        )

        results = vector_store.similarity_search(query, k=k)
        print(f'\n查询: {query}')
        print(f'返回 {len(results)} 个相关文档:')
        for i, doc in enumerate(results, 1):
            print(f'\n{i}. 来源: {doc.metadata.get("filename")}')
            print(f'内容: {doc.page_content[:200]}...')

if __name__ == '__main__':
    builder = VectorStoreBuilder()
    builder.build_vector_store()
    builder.test_retrieval('如何面试？')
    builder.test_retrieval('公司有哪些福利待遇？')