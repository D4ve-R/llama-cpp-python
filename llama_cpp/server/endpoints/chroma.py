import chromadb
from pydantic import BaseModel
from typing import Optional, Union, List, Dict
from fastapi import APIRouter, HTTPException

from llama_cpp.server.storage import chroma_client, chroma_version

__all__ = ['router']

router = APIRouter(prefix='/vectorstore')

@router.get('/')
def info():
    return {
        "chroma_version": chroma_version,
    }

@router.get('/{name}')
def get_collection(name: str):
    try:
        collection = chroma_client.get_collection(name)
        return {"collection": collection, "items": collection.get()}
    except: raise HTTPException(404, f"Collection {name} NOT found!")

@router.put('/{name}', status_code=201)
def post(name: str):
    try: return chroma_client.create_collection(name, get_or_create=True)
    except Exception as e: raise HTTPException(404, e)

class ChromaItem(BaseModel):
    ids: Union[str, List[str]] = None
    embeddings: Optional[List[List[float]]] = None
    metadatas: Optional[List[Dict]] = None
    documents: Optional[Union[str, List[str]]] = None

class CollectionPostRequest(BaseModel):
    name: Optional[str] = None
    metadata: Optional[chromadb.CollectionMetadata] = None
    items: Optional[List[ChromaItem]] = []

@router.post('/{name}', status_code=201)
def post(name: str, body: CollectionPostRequest):
    try: 
        collection = chroma_client.create_collection(name, get_or_create=True)
        collection.add()
        if body.name or body.metadata:
            collection.modify(**(body.model_dump()))
        for item in body.items:
            collection.upsert(**(item.model_dump))
        return "OK"
    except Exception as e: raise HTTPException(404, e)

@router.post('/{name}/query', status_code=201)
def post_query(name: str, query: str, n: int = 1):
    try:
        collection = chroma_client.get_collection(name)
        return collection.query(query_texts=[query], n_results=n)
    except: raise HTTPException(404, f"Collection {name} NOT found!")
    

@router.post('/{name}/query', status_code=201)
def post_query(name: str, query: str, n: int = 1):
    try:
        collection = chroma_client.get_collection(name)
        return collection.query(query_texts=[query], n_results=n)
    except: raise HTTPException(404, f"Collection {name} NOT found!")
    
@router.delete('/{collection}')
def delete(name: str):
    try: 
        chroma_client.delete_collection(name)
        return "OK"
    except: raise HTTPException(404, f"Collection {name} NOT found!")
