import gradio as gr

from llama_cpp.server.client import client
from llama_cpp.server.plugins import GradioPlugin

__all__ = ['ChatbotPlugin']

_model_alias = ''

def change_model(model):
    global _model_alias
    _model_alias = model

def add_text(history, text):
    history += [(text, None)]
    return history, gr.Textbox(value="", interactive=False)

def add_file(history, file):
    history += [((file.name,), None)]
    return history

def bot(history):
    response = client.chat.completions.create(
        model=_model_alias,
        messages=[
            {'role': 'user', 'content': history[-1][0]}
        ],
        temperature=0,
        stream=True
    )

    history[-1][1] = ""
    for chunk in response:
        history[-1][1] += (chunk.choices[0].delta.content or '')
        yield history

with gr.Blocks(title='Llama C++ Server') as demo:
    with gr.Row():
        with gr.Accordion("Models"):
            dropdown = gr.Dropdown(
                [_model_alias, 'llama-2-7b.Q2_K'],
                value=_model_alias,
                label="Select a model",
                elem_id="model_dropdown"
            )
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        #bubble_full_width=False,
        #avatar_images=(None, (os.path.join(os.path.dirname(__file__), "avatar.png"))),
    )

    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Enter text and press enter, or upload an image",
            container=False,
            elem_id="chatbot-input"
        )
        btn = gr.UploadButton("📁", file_types=["image",]) #"video", "audio"])

    txt_msg = txt.submit(add_text, [chatbot, txt], [chatbot, txt], queue=False).then(
        bot, chatbot, chatbot, api_name="bot_response"
    )
    txt_msg.then(lambda: gr.Textbox(interactive=True), None, [txt], queue=False)
    file_msg = btn.upload(add_file, [chatbot, btn], [chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    dropdown.change(change_model, dropdown)

demo.queue()

class ChatbotPlugin(GradioPlugin):
    blocks = demo
    path='/'
