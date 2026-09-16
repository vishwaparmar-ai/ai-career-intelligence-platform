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


def generate_text(*, system_prompt: str, user_content: str) -> str:
    """
    Plain free-form text generation — no tool call, no forced schema. Used
    for RAG answers and the assistant's final synthesized response, where
    the output is prose rather than structured data to validate and store.
    """
    response = _client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    )
    return (response.choices[0].message.content or "").strip()


def select_tools(
    *, system_prompt: str, user_content: str, tools: list[dict]
) -> list[dict]:
    """
    Lets the model choose zero, one, or several tools to call
    (tool_choice="auto"), unlike extract_structured which forces exactly
    one specific tool. This is the "controlled" part of the agent
    workflow: the model only ever picks from a fixed, explicit tool list
    we defined — it can't invent a new capability or run arbitrary code,
    only request one of the functions we've exposed.

    Returns a list of {"name": ..., "arguments": {...}} — empty if the
    model decided no tool was needed for this question.
    """
    response = _client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        tools=tools,
        tool_choice="auto",
    )

    message = response.choices[0].message
    if not message.tool_calls:
        return []

    calls = []
    for call in message.tool_calls:
        try:
            arguments = json.loads(call.function.arguments)
        except json.JSONDecodeError:
            arguments = {}
        calls.append({"name": call.function.name, "arguments": arguments})
    return calls