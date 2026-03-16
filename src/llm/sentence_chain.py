from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.llm.schemas import SentenceOutput
from loguru import logger
import json


def create_sentence_prompt():
    """Create the prompt template for generating Korean example sentences."""

    prompt = ChatPromptTemplate.from_template(
        """You are generating Korean example sentences for vocabulary learning.

Noun: {word}

Requirements:
- Produce exactly 3 Korean sentences
- Each sentence must naturally include the noun "{word}"
- Sentences must be easy to understand
- No numbering
- No explanations

Return JSON:

{{
  "word": "{word}",
  "sentences": ["sentence1", "sentence2", "sentence3"]
}}"""
    )

    return prompt


def generate_sentences(llm, word: str, retry_count: int = 3) -> dict:
    """
    Generate 3 Korean example sentences for a given noun using LLM.

    Args:
        llm: LangChain LLM instance
        word: Korean noun to generate sentences for
        retry_count: Number of retries on parsing failure

    Returns:
        Dictionary with 'word' and 'sentences' keys

    Raises:
        Exception: If all retries fail
    """
    logger.info(f"Generating sentences for word: {word}")

    prompt = create_sentence_prompt()
    parser = PydanticOutputParser(pydantic_object=SentenceOutput)

    for attempt in range(retry_count):
        try:
            # Create the chain
            chain = prompt | llm

            # Invoke the chain
            response = chain.invoke({"word": word})

            # Parse the response content
            content = (
                response.content if hasattr(response, "content") else str(response)
            )

            # Try to extract JSON from the response
            content = content.strip()
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0].strip()

            # Parse JSON
            result = json.loads(content)

            # Validate using Pydantic
            validated = SentenceOutput(**result)

            logger.info(
                f"Successfully generated sentences for {word}: {validated.sentences}"
            )

            return {"word": validated.word, "sentences": validated.sentences}

        except json.JSONDecodeError as e:
            logger.warning(
                f"JSON parsing error (attempt {attempt + 1}/{retry_count}): {e}"
            )
            if attempt == retry_count - 1:
                raise Exception(
                    f"Failed to parse LLM output after {retry_count} attempts: {e}"
                )

        except Exception as e:
            logger.warning(
                f"Error generating sentences (attempt {attempt + 1}/{retry_count}): {e}"
            )
            if attempt == retry_count - 1:
                raise Exception(
                    f"Failed to generate sentences after {retry_count} attempts: {e}"
                )

    # Return empty sentences if all retries fail
    return {"word": word, "sentences": ["", "", ""]}
