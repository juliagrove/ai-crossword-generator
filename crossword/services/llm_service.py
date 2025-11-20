import json
from typing import List

from django.conf import settings
from google import genai
from pydantic import BaseModel, Field


class Clue(BaseModel):
    word: str = Field(description="Crossword word")
    clue: str = Field(description="Crossword clue")


class WordList(BaseModel):
    clues: List[Clue]


class CrosswordClueGenerator:
    """
    This class gets crossword word/clue pairs using Geminis structured
    outputs to ensure proper JSON formatting from the LLM repsonse
    """

    def __init__(self):
        self.model_name = settings.GEMINI_MODEL_NAME
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def generate(self, category, num_words):
        prompt = self._build_prompt(category, num_words)
        try:
            print("Calling Gemini API")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": WordList.model_json_schema(),
                },
            )
            return self._parse_json(response)

        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")

    def _build_prompt(self, category, num_words):
        return f"""
            You are a crossword generator. Give me { num_words } words and short clues that follow the category: { category }. 
            Do NOT generate any additonal information other than the Word and its clue. 
            Do NOT add the number of letters to the end of the clues
        """

    def _parse_json(self, response):
        output = json.loads(response.text)
        return {item["word"].replace(" ", ""): item["clue"] for item in output["clues"]}


clue_generator = CrosswordClueGenerator()
