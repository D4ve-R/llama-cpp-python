from openai import OpenAI

client = OpenAI(
    api_key='sk_' + ('x' * 10),
    base_url='http://127.0.0.1:8000/v1',
)

def set_client(base_url: str = 'http://127.0.0.1:8000/v1', api_key: str = 'sk_' + ('x' * 10), **kwargs):
    global client
    if client: del client
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
        **kwargs
    )

