from pydantic import BaseModel


class SkillGap(BaseModel):
    skill: str
    importance: str  # "required" | "preferred"
    status: str  # "matched" | "partial" | "missing"
    evidence: str | None
    # Higher = more worth closing. required+missing scores highest;
    # anything already matched scores 0 and sinks to the bottom.
    priority: int


class GapAnalysis(BaseModel):
    gaps: list[SkillGap]