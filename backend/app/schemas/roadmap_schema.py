from pydantic import BaseModel, Field

from backend.app.models.roadmap_model import RoadmapStatus


class LLMRoadmapItem(BaseModel):
    """
    The shape asked of the LLM. Deliberately excludes 'priority' — the
    model has been inconsistent about whether that's a string
    ('high'/'medium'/'low') or a number (1, 2, 3...) even when told,
    and Groq's schema validator rejects the whole tool call the moment
    it picks the "wrong" one for whatever we declared. Since priority is
    already fully determined by the order these items were requested in
    (Day 18's gap priority), there's nothing for the model to decide here
    anyway — better to not ask than to keep chasing its output format.
    """

    skill: str
    reason: str | None = Field(
        None, description="Why this skill matters for this specific job"
    )
    effort: str | None = Field(
        None, description="A rough time estimate, e.g. '2-3 hours', '1 day', 'a weekend'"
    )
    practical_task: str | None = Field(
        None, description="One concrete, actionable task to build or practice this skill"
    )


class LLMRoadmapData(BaseModel):
    items: list[LLMRoadmapItem] = Field(default_factory=list)


class RoadmapItem(BaseModel):
    """The final, stored/returned shape — priority is always one of our
    own labels (assigned by list position), never whatever format the
    model happened to use on a given run."""

    skill: str
    reason: str | None = None
    priority: str  # "High" | "Medium" | "Low" — computed, not model-supplied
    effort: str | None = None
    practical_task: str | None = None


class RoadmapData(BaseModel):
    items: list[RoadmapItem] = Field(default_factory=list)


class RoadmapRead(BaseModel):
    status: RoadmapStatus
    data: RoadmapData | None
    error_message: str | None

    model_config = {"from_attributes": True}