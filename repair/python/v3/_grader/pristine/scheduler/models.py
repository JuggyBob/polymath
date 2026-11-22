"""Domain types for the job scheduler."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    job_id: str
    priority: int
    created: int
    ttl: int
    payload: str
    status: str = "queued"
    tags: tuple = ()

    @property
    def expires_at(self) -> int:
        return self.created + self.ttl

    def is_expired(self, now: int) -> bool:
        return now >= self.expires_at
