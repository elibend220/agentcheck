"""
run.py

CLI entrypoint. Reads article text from a file path argument, or from
stdin if no argument is given, runs it through the two node graph, and
prints the summary and credibility assessment.

Usage:
    python run.py article.txt
    cat article.txt | python run.py
"""
from __future__ import annotations

import sys

from agent import build_graph
from llm_ollama import make_ollama_llm


def main() -> int:
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            article_text = f.read()
    else:
        article_text = sys.stdin.read()

    if not article_text.strip():
        print("agentcheck: no article text provided", file=sys.stderr)
        return 2

    llm = make_ollama_llm()
    graph = build_graph(llm)

    result = graph.invoke({"article_text": article_text, "source_name": "unknown"})

    print("SUMMARY")
    print(result["summary"])
    print()
    print(f"CREDIBILITY SCORE: {result['credibility_score']}/10")
    print(f"RATIONALE: {result['credibility_rationale']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
