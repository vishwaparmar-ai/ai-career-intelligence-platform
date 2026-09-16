import uuid

from pydantic import BaseModel


class AgentAskRequest(BaseModel):
    question: str
    resume_id: uuid.UUID | None = None
    job_id: uuid.UUID | None = None


class ToolResult(BaseModel):
    tool: str
    result: dict


class AgentAskResponse(BaseModel):
    answer: str
    tools_used: list[str]
    tool_results: list[ToolResult]