
from dataclasses import dataclass, field

from lightrag.core import Component, Generator, DataClass
from lightrag.components.model_client import GroqAPIClient
from lightrag.components.output_parsers import JsonOutputParser
from lightrag.utils.logger import get_logger







qa_template = r"""<SYS>
You are an helpful assistant, you cater to user needs, given the user query help the user get what he wanted, do no respond anything otherwise :).
</SYS>
User Prompt: {{prompt}}
User: {{input_str}}
You:"""

class Chat(Component):
    def __init__(self):
        super().__init__()

        self.generator = Generator(
            model_client=GroqAPIClient(),   
            model_kwargs={"model": "llama3-8b-8192"},
            template=qa_template
        )

    def call(self, query: str, prompt: str):
        return self.generator.call({"input_str": query, "prompt":prompt})

    async def acall(self, query: str, prompt: str):
        return await self.generator.acall({"input_str": query, "prompt":prompt})
    
    