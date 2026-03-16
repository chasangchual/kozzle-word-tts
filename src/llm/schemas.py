from pydantic import BaseModel, Field
from typing import List


class SentenceOutput(BaseModel):
    """Schema for LLM sentence generation output."""

    word: str = Field(description="The Korean noun")
    sentences: List[str] = Field(
        description="List of exactly 3 Korean example sentences",
        min_length=3,
        max_length=3,
    )
