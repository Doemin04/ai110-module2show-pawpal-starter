"""
PawPal+ — logic layer
All backend classes live here. UI and tests import from this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Dataclasses — simple value objects
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age_years: int

    def get_profile(self) -> str:
        """Return a human-readable summary of this pet."""
        pass


@dataclass
class Task:
    name: str
    category: str          # e.g. "walk", "feed", "meds", "grooming"
    duration_minutes: int
    priority: str          # "high", "medium", or "low"
    notes: str = ""
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        pass

    def is_high_priority(self) -> bool:
        """Return True if this task has high priority."""
        pass


# ---------------------------------------------------------------------------
# Regular classes — objects with richer behaviour
# ---------------------------------------------------------------------------

class Owner:
    def __init__(
        self,
        name: str,
        available_minutes: int,
        preferences: str = "",
    ) -> None:
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences
        self.pets: list[Pet] = []
        self.tasks: list[Task] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's roster."""
        pass

    def add_task(self, task: Task) -> None:
        """Add a care task to this owner's task list."""
        pass

    def update_availability(self, minutes: int) -> None:
        """Update the number of minutes the owner has available today."""
        pass

    def update_preferences(self, preferences: str) -> None:
        """Update the owner's scheduling preferences."""
        pass


class Schedule:
    def __init__(self, date: str) -> None:
        self.date = date
        self.selected_tasks: list[Task] = []
        self.total_duration_minutes: int = 0

    def display(self) -> str:
        """Return a formatted string representation of the schedule."""
        pass

    def remaining_time(self, available_minutes: int) -> int:
        """Return how many minutes are left after the scheduled tasks."""
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task]) -> None:
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def generate_schedule(self, date: str) -> Schedule:
        """
        Build and return a Schedule for the given date.
        Selects tasks that fit within the owner's available time,
        ordered by priority.
        """
        pass

    def explain_plan(self) -> str:
        """Return a plain-language explanation of how the schedule was built."""
        pass
