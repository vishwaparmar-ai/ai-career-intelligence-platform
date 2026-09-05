"""
Provider abstraction for LLM calls. Everything that needs an LLM (resume
parsing now, job parsing / RAG / interview later) should go through this
module rather than importing the Groq SDK directly — swapping providers
or models later then only touches this one file.

Groq's API is OpenAI-compatible, which has a different tool-calling shape
than Anthropic's: tools are wrapped in {"type": "function", "function": {...}},
tool_choice names the function the same way, and the schema key is
"parameters" (not "input_schema"). The response also comes back as
message.tool_calls[0].function.arguments — a JSON *string* you have to
parse yourself, not a pre-parsed dict.
"""

import json

from groq import Groq

from backend.app.core.config import get_settings

settings = get_settings()

_client = Groq(api_key=settings.groq_api_key)


class LLMExtractionError(Exception):
    """Raised when the model doesn't return a usable tool call."""


def extract_structured(
    *,
    system_prompt: str,
    user_content: str,
    tool_name: str,
    tool_description: str,
    input_schema: dict,
) -> dict:
    """
    Forces the model to respond via a single tool call matching
    input_schema (typically a Pydantic model's .model_json_schema()).
    Returns the raw dict — the caller is responsible for validating it
    against the actual Pydantic model before trusting/persisting it.
    """
    response = _client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_description,
                    "parameters": input_schema,
                },
            }
        ],
        tool_choice={"type": "function", "function": {"name": tool_name}},
    )

    message = response.choices[0].message
    if not message.tool_calls:
        raise LLMExtractionError("Model did not return the expected tool call.")

    call = message.tool_calls[0]
    try:
        return json.loads(call.function.arguments)
    except json.JSONDecodeError as exc:
        raise LLMExtractionError(
            "Model returned malformed tool call arguments."
        ) from exc