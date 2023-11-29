import os
import sys
import subprocess as sp
import logging
import importlib
import inspect
from typing import List
from abc import ABC, abstractmethod
from fastapi import FastAPI

__all__ = ['BasePlugin', 'GradioPlugin', 'ChainPlugin']

#logger = logging.getLogger(__name__)
logger = logging.getLogger('uvicorn')

_PLUGIN_DIR = os.path.abspath(os.path.dirname(__file__))

class BasePlugin(ABC):
    """Abstract plugin base class.
    Subclasses must overwrite classmethod init(cls, app: FastAPI) -> FastAPI
    """
    @abstractmethod
    def init(self, app: FastAPI) -> FastAPI:
        raise NotImplementedError()
    
class GradioPlugin(BasePlugin):
    """blocks: gr.Blocks = gr.Interface(lambda x: "Hello, " + x + "!", "textbox", "textbox")"""
    blocks = None
    path = '/gradio'
    _base_path = '/ui'

    def init(self, app: FastAPI) -> FastAPI:
        import gradio as gr # type: ignore
        if self.blocks is None: raise Exception("No gradio.Blocks, add blocks to GradioPlugin.blocks!")
        return gr.mount_gradio_app(app, self.blocks, path=self._base_path + self.path)
    
class ChainPlugin(BasePlugin):
    """runnable: langchain.schema.runnable.Runnable"""
    runnable = None
    path = '/chain'
    _base_path = '/chains'

    def init(self, app: FastAPI) -> FastAPI:
        from langserve import add_routes # type: ignore
        if self.runnable is None: raise Exception("No runnable, add runnable to ChainPlugin.runnable!")
        add_routes(
            app,
            self.runnable,
            path=self._base_path + self.path,
        )
        return app

def install_requirements(requirements_path: str, quiet=True):
    cmd = [sys.executable, "-m", "pip", "install", "-r", requirements_path, "-q"]
    if 'requirements.txt' in requirements_path: cmd += ["-r", requirements_path]
    else: cmd += [requirements_path]
    if quiet: cmd += ["-q"]
    sp.check_call(cmd, stdout=sp.DEVNULL, stderr=sp.DEVNULL)

def import_plugins(plugin_path: str, install_deps=True) -> List[BasePlugin]:
    """Import server plugins from dir at plugin_path.
    Server plugins must be a subclass of LlamaPlugin.
    """
    derived_classes = []
    try:
        plugin_path = os.path.abspath(plugin_path)
        plugins_files = os.listdir(plugin_path)
        if install_deps:
            logger.info("installing plugin requirements")
            if 'requirements.txt' in plugins_files:
                install_requirements(os.path.join(plugin_path, 'requirements.txt'))
            else: install_requirements(plugin_path)
        for plugin_name in [plugin for plugin in plugins_files if plugin.endswith('.py')]:
            if plugin_path != _PLUGIN_DIR:
                os.symlink(os.path.join(plugin_path, plugin_name), os.path.join(_PLUGIN_DIR, plugin_name))
            try:
                module_name = f'llama_cpp.server.plugins.{plugin_name.split(".py")[0]}'
                module = importlib.import_module(module_name)
                all_classes = inspect.getmembers(module, inspect.isclass)
                classes = [cls for _, cls in all_classes if issubclass(cls, BasePlugin) 
                           and cls != BasePlugin and cls != GradioPlugin and cls != ChainPlugin]
                derived_classes += classes
            except Exception as e: raise Exception(e)
            finally: os.unlink(os.path.join(_PLUGIN_DIR, plugin_name))
    except Exception as e:
        logger.error(f"Failed to import plugin from {plugin_path}\nError {e}")
    return derived_classes
