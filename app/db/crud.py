import numpy as np


def add_vectors(faiss_client, embeddings):
    try:
        faiss_client.index.add(embeddings)
        return "Successfully Added"
    except Exception as e:
        return str(e)
        

def search_vector(faiss_client, query_vector, top_k=5):
    """
    Searches for the top K nearest vectors in the Faiss index.

    Args:
        query_vector (np.ndarray): A single vector to search for, shape (1, dimension).
        top_k (int): Number of nearest neighbors to retrieve.

    Returns:
        (distances, indices): Distances and indices of the nearest neighbors.
    """
    query_vector = np.array(query_vector, dtype='float32').reshape(1, -1)
    distances, indices = faiss_client.index.search(query_vector, top_k)
    return indices