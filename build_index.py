import json
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm
from langchain.text_splitter import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "Document title"),
    ("##", "Section"),
    ("###", "Sub-section"),
    ("####", "Paragraph"),
    ("#####", "Sub-paragraph"),
]


def main():
    chroma_client = chromadb.PersistentClient(path="./chroma.db")
    collection = chroma_client.create_collection(name="legislation")

    # Initialize the text splitter
    # splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    print("Building index")
    with open("data/documents_crawl4ai.json") as f:
        docs = json.load(f)

    doc_ix = 0
    for doc in tqdm(docs):
        chunks = splitter.split_text(doc["content"])
        for chunk_ix, chunk in enumerate(chunks):
            chunk_header = ""
            for k, v in chunk.metadata.items():
                chunk_header += f"{k}: {v}; "
            chunk_header += "Text: "
            collection.upsert(
                documents=[chunk_header + chunk.page_content],
                ids=[f"doc{doc_ix}_chunk{chunk_ix}"],
            )
        doc_ix += 1


if __name__ == "__main__":
    main()


# results = collection.query(
#     query_texts=["This is a query document about florida"], # Chroma will embed this for you
#     n_results=2 # how many results to return
# )

# print(results)
