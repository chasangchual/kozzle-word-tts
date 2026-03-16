import typer
from pathlib import Path
from typing import Optional
from src.pipeline import process_korean_text
from src.config import Config

app = typer.Typer()

@app.command()
def process(
    input_path: str = typer.Argument(..., help="Input file or directory path"),
    llm_provider: str = typer.Option("ollama", help="LLM provider (ollama, openai, anthropic)"),
    model: str = typer.Option("exaone3.5:7.8b", help="LLM model name")
):
    """
    Process Korean text files to generate vocabulary learning content.
    
    This command processes Korean text files, extracts nouns, generates example 
    sentences using an LLM, and creates TTS audio files.
    """
    try:
        config = Config(llm_provider=llm_provider, model=model)
        process_korean_text(input_path, config)
        typer.echo("Processing completed successfully!")
    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()