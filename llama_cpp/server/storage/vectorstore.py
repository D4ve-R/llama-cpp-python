import os
import chromadb

__all__ = ['chroma_version', 'chroma_client']

chroma_version = chromadb.__version__
chroma_client = chromadb.PersistentClient() # TODO specify persitent dir

