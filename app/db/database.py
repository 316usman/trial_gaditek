import faiss
import numpy as np

class FaissSingleton:
    _instance = None

    def __new__(cls, dimension=1536):
        if cls._instance is None:
            cls._instance = super(FaissSingleton, cls).__new__(cls)
            cls._instance.index = faiss.IndexFlatL2(dimension)  # L2 distance
        return cls._instance
