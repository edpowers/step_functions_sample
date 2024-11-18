"""Workflow Models."""

from typing import Literal

from pydantic import BaseModel


class RetryConfig(BaseModel):
    ErrorEquals: list[str]
    IntervalSeconds: int
    MaxAttempts: int
    BackoffRate: float


class TaskState(BaseModel):
    """Task state for model."""

    Type: Literal["Task"]
    Resource: str
    # Can specify the task type by providing the resource ARN.
    # All Task types except the one that invokes an HTTPS API, use the following syntax
    # arn:partition:service:region:account:task_type:name
    InputPath: str | None = None
    ResultPath: str | None = None
    OutputPath: str | None = None
    Retry: list[RetryConfig] | None = None
    Next: str | None = None
    End: bool | None = None


class WorkflowDefinition(BaseModel):
    Comment: str | None = None
    StartAt: str
    States: dict[str, TaskState]
