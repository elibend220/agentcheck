# agentcheck

A two node LangGraph pipeline: one node summarizes an article, a second
node scores the likely credibility of its source based on the summary,
using a local model served by Ollama.

Written to demonstrate multi agent orchestration design in isolation,
independent of any larger system.

## Architecture

```
START -> summarize -> score_credibility -> END
```

State flows through a single `AgentState` TypedDict. Each node reads only
the fields it needs and returns only the fields it adds, which LangGraph
merges into the running state. Neither node holds any state of its own
between invocations.

## Design decision: the LLM is injected, not imported

`agent.py` defines the graph against a plain `Callable[[str], str]`
interface. It does not import Ollama, OpenAI, or any specific provider.
`llm_ollama.py` is the only file that knows a real model exists; it adapts
`ChatOllama` to that same callable interface.

This split exists for a concrete reason: it lets the graph's control flow,
state propagation, and response parsing, the logic that can be wrong
independent of any model's output quality, be verified deterministically
in `test_graph.py` using a fake that returns fixed strings, without
needing a running model server. Whether the real model's summaries and
credibility judgments are *good* is a separate question that fixed test
strings cannot answer and this suite does not claim to answer.

## Running the tests

```bash
pip install -r requirements.txt
pytest test_graph.py -v
```

These four tests were run and passed in the environment this project was
built in:

* the graph executes both nodes in order and populates all expected state
  fields
* an out of range score from a malformed model response is clamped to the
  documented 1 to 10 scale rather than passed through
* a response that does not match the expected `SCORE:`/`RATIONALE:` format
  falls back to a neutral default instead of raising an exception inside
  a graph node
* two independent invocations do not leak state into one another

None of this requires network access or a model server, by design.

## Running against a real model

```bash
ollama pull llama3.1
ollama serve
python run.py path/to/article.txt
```

## What was not verified in this environment

This project was built in a sandboxed container without network access to
Ollama's model registry and without the `ollama` binary installed. That
means the following was not run here and should not be assumed to work
without independent verification:

* `llm_ollama.py` was reviewed against the `langchain-ollama` API but
  never executed against a live Ollama server
* `run.py` end to end, including real summarization and credibility
  scoring output, was not produced here
* the actual quality of the model's summaries or credibility judgments,
  as opposed to the pipeline's ability to route and parse whatever the
  model returns, has not been assessed at all

Anyone evaluating this project should run `run.py` against a real article
on their own machine with Ollama installed rather than take the pipeline's
output quality on faith. The test suite proves the wiring is correct; it
does not and cannot prove the model's judgment is good.

## Scope

This is intentionally a standalone utility with no relation to any other
project.
