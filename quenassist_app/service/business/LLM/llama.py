from langchain.llms.base import LLM
from transformers import AutoConfig
from transformers import AutoTokenizer
from transformers import AutoModel
from typing import List, Dict, Optional

from pydantic import BaseModel

from gradio_client import Client

from quenassist_app.service.business.LLM.models import SocialScene

class llamaClient(LLM):
    tokenizer: object = None
    model: object = None

    def __init__(self) -> None:
        super().__init__()

    @property
    def _llm_type() -> str:
        return "ChatGLM3"

    def load_model(self, model_path: str) -> None:
        model_config = AutoConfig.from_pretrained(
            model_path,
            trust_remote_code=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True
        )
        self.model = AutoModel.from_pretrained(
            model_path, config=model_config, trust_remote_code=True, device_map="auto").eval()

    def _call(self, prompt: str, history: List = [], stop: Optional[List[str]] = ["<|user|>"]) -> str:
        past_key_values = None
        history = []
        query = prompt
        current_length = 0
        result = ""
        for response, history, past_key_values in self.model.stream_chat(self.tokenizer, query, history=history, top_p=1, temperature=0.01, past_key_values=past_key_values, return_past_key_values=True):
            result += response[current_length:]
            current_length = len(response)
        return result
    
# class llamaClient_quen:
#     def __init__(self) -> None:
#         self.quen_client = Client("http://120.76.130.14:6006/prompt/")
    
#     def query(self, question: str, context: str, scene: –) -> str:
#         result_prompt = self.quen_client.predict(
#             scene.task,
#             api_name="/cls_choose_change"
#         )

#         return self.llama(prompt)