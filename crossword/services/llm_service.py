from typing import List

from django.conf import settings
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from django.conf import settings



class Clue(BaseModel):
    word: str = Field(description="Crossword word")
    clue: str = Field(description="Crossword clue")


class WordList(BaseModel):
    clues: List[Clue]


def _get_llm():
    return init_chat_model(
        model=getattr(settings, "LLM_MODEL_NAME", "gemini-2.5-flash"),
        model_provider=getattr(settings, "LLM_PROVIDER", "google-genai"),
        api_key=getattr(settings, f"LLM_API_KEY", None)
    )

_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert Crossword Constructor. 
Your task is to generate a cohesive list of word/clue pairs based on a specific category.

### GUIDELINES:
1. **Word Selection**: Ensure words vary in length and are directly relevant to the category: {category}.
2. **Clue Style**: Write clever, engaging clues. Mix "straight" definitions with occasional wordplay or puns.
3. **Constraints**:
    - NO repeating the answer word within the clue.

### OUTPUT FORMAT:
Return exactly {num_words} pairs. Focus on high-quality, solvable entries."""),
    
    ("human", "Generate a list of {num_words} entries for the category: {category}")
])


class CrosswordClueGenerator:
    """
    Generates crossword word/clue pairs using LangChain structured outputs.
    Swap models by changing LLM_PROVIDER / LLM_MODEL_NAME in settings.
    """

    def __init__(self):
        self.chain = _PROMPT | _get_llm().with_structured_output(WordList)

    def generate(self, category, num_words):
        try:
            result = self.chain.invoke({"category": category, "num_words": num_words})
            return {clue.word.replace(" ", ""): clue.clue for clue in result.clues}
        except Exception as e:
            raise RuntimeError(f"LLM error: {e}")


clue_generator = CrosswordClueGenerator()
