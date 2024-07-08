
from dataclasses import dataclass, field

from lightrag.core import Component, Generator, DataClass
from lightrag.components.model_client import GroqAPIClient
from lightrag.components.output_parsers import JsonOutputParser

@dataclass
class QAOutput(DataClass):
    key: str = field(
        metadata={"desc": "header from the list of headers that is closest to the given header"}
    )


qa_template = r"""<SYS>
You are a financial experent, given a header and a list of headers you have to written which is the closest resemblence to the given headers.
<OUTPUT_FORMAT>
{{output_format_str}}
</OUTPUT_FORMAT>
</SYS>
List of headers: {{list_of_headers}}
User: {{input_str}}
You:"""

class QA(Component):
    def __init__(self):
        super().__init__()

        parser = JsonOutputParser(data_class=QAOutput, return_data_class=True)
        self.generator = Generator(
            model_client=GroqAPIClient(),
            model_kwargs={"model": "llama3-8b-8192"},
            template=qa_template,
            prompt_kwargs={"output_format_str": parser.format_instructions()},
            output_processors=parser,
        )

    def call(self, query: str, list_of_headers: list):
        return self.generator.call({"input_str": query, "list_of_headers":list_of_headers})

    async def acall(self, query: str, list_of_headers: list):
        return await self.generator.acall({"input_str": query, "list_of_headers":list_of_headers})
    