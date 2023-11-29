import os
from typing import List
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware

from llama_cpp import __version__
from llama_cpp.server.endpoints.openai_v1 import router as v1_router
from llama_cpp.server.endpoints.chroma import router as chroma_router

def create_app(
    cors_allow_origins: List[str]=['*'],
    **kwargs
):
    middleware = [
        Middleware(RawContextMiddleware, plugins=(plugins.RequestIdPlugin(),))
    ]
    app = FastAPI(
        middleware=middleware,
        **kwargs
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(v1_router)
    app.include_router(chroma_router)

    @app.get('/')
    async def root():
        return FileResponse(os.path.join(os.path.dirname(__file__), 'static', 'index.html'),
                            headers={'X-LLAMA-CPP-VERSION': __version__})
    return app
