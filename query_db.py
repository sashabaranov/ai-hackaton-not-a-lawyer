import json
import chromadb
import pprint


def main():
    chroma_client = chromadb.PersistentClient(path="./chroma.db")
    collection = chroma_client.get_collection(name="legislation")

    while True:
        query = input("Query: ")
        results = collection.query(query_texts=[query], n_results=3)
        for query_docs in results["documents"]:
            for doc in query_docs:
                print("* ", doc.replace("\n", "\n\t"), len(doc))


if __name__ == "__main__":
    main()
