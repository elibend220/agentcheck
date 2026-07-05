"""
llm_ollama.py

Real backend: wraps a local Ollama model behind the same
`Callable[[str], str]` interface that agent.py expects, so it can be
swapped for the test fake with zero changes to graph.py.

Requires a running Ollama server (`ollama serve`) with a model already
pulled locally, e.g. `ollama pull llama3.1`. This module is not exercised
by the test suite, since that would require network access to a model
server that is not guaranteed to exist in every environment; see
tests/test_graph.py for what is verified without one.
"""
from __future__ import annotations

from langchain_ollama import ChatOllama


def make_ollama_llm(model: str = "llama3.1", base_url: str = "http://localhost:11434"):
    chat = ChatOllama(model=model, base_url=base_url, temperature=0.0)

    def call(prompt: str) -> str:
        response = chat.invoke(prompt)
        return response.content

    return call
