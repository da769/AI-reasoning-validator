from dataclasses import dataclass, field
from typing import List


@dataclass
class EvaluationCriterion:
    name: str
    score: int
    maximum: int
    feedback: str


@dataclass
class EvaluationResult:
    problem_id: str
    verdict: str
    total_score: int
    maximum_score: int
    criteria: List[EvaluationCriterion] = field(default_factory=list)