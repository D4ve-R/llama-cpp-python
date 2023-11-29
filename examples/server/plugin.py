from fastapi import FastAPI
import gradio as gr

from llama_cpp.server.plugins import BasePlugin, GradioPlugin
from llama_cpp.server.client import client

class ExamplePlugin(BasePlugin):
    def init(self, app: FastAPI) -> FastAPI:
        print(app.title)
        return app

class ExampleGradioPlugin(GradioPlugin):
    blocks = gr.Interface(lambda x: "Hello, " + x + "!", "textbox", "textbox")
