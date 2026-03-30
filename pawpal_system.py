"""
PawPal+ — logic layer
All backend classes live here. UI and tests import from this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Dataclasses — simple value objects
# ---------------------------------------------------------------------------

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
        self.completed = True

    def is_high_priority(self) -> bool:
        """Return True if this task has high priority."""
        return self.priority == "high"


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age_years: int
    tasks: list[Task] = field(default_factory=list)

    def get_profile(self) -> str:
        """Return a human-readable summary of this pet."""
        return f"{self.name} ({self.species}, {self.breed}, {self.age_years}yr)"

    def add_task(self, task: Task) -> None:
        """Attach a care task directly to this pet."""
        self.tasks.append(task)


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
        self.pets.append(pet)

    def add_task(self, task: Task) -> None:
        """Add an owner-level task (not tied to a specific pet)."""
        self.tasks.append(task)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all pets, plus any owner-level tasks."""
        all_tasks: list[Task] = list(self.tasks)
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def update_availability(self, minutes: int) -> None:
        """Update the number of minutes the owner has available today."""
        self.available_minutes = minutes

    def update_preferences(self, preferences: str) -> None:
        """Update the owner's scheduling preferences."""
        self.preferences = preferences


_PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


class Schedule:
    def __init__(self, date: str) -> None:
        self.date = date
        self.selected_tasks: list[Task] = []
        self.total_duration_minutes: int = 0

    def display(self) -> str:
        """Return a formatted string representation of the schedule."""
        if not self.selected_tasks:
            return f"Schedule for {self.date}: no tasks planned."
        lines = [f"Schedule for {self.date}:"]
        for i, task in enumerate(self.selected_tasks, 1):
            status = "[done]" if task.completed else f"{task.duration_minutes} min"
            lines.append(
                f"  {i}. [{task.priority.upper()}] {task.name}"
                f" ({task.category}) - {status}"
            )
        lines.append(f"  Total: {self.total_duration_minutes} min")
        return "\n".join(lines)

    def remaining_time(self, available_minutes: int) -> int:
        """Return how many minutes are left after the scheduled tasks."""
        return available_minutes - self.total_duration_minutes


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet) -> None:
        self.owner = owner
        self.pet = pet
        self.last_schedule: Schedule | None = None  # set by generate_schedule()

    def generate_schedule(self, date: str) -> Schedule:
        """
        Build and return a Schedule for the given date.
        Reads tasks from self.owner.tasks, selects those that fit within
        the owner's available time ordered by priority, and stores the
        result in self.last_schedule before returning it.
        """
        schedule = Schedule(date)
        pending = [t for t in self.owner.get_all_tasks() if not t.completed]
        sorted_tasks = sorted(
            pending,
            key=lambda t: (_PRIORITY_ORDER.get(t.priority, 99), t.name),
        )
        budget = self.owner.available_minutes
        for task in sorted_tasks:
            if task.duration_minutes <= budget:
                schedule.selected_tasks.append(task)
                schedule.total_duration_minutes += task.duration_minutes
                budget -= task.duration_minutes
        self.last_schedule = schedule
        return schedule

    def explain_plan(self) -> str:
        """Return a plain-language explanation of how self.last_schedule was built."""
        if self.last_schedule is None:
            return "No schedule has been generated yet."
        s = self.last_schedule
        if not s.selected_tasks:
            return (
                f"No tasks were scheduled for {s.date}. "
                "Either there are no pending tasks or none fit within the available time."
            )
        all_pending = [t for t in self.owner.get_all_tasks() if not t.completed]
        skipped = [t for t in all_pending if t not in s.selected_tasks]
        lines = [
            f"For {s.date}, {len(s.selected_tasks)} task(s) were chosen "
            f"from {len(all_pending)} pending, "
            f"fitting within the {self.owner.available_minutes}-minute budget.",
            "Tasks were sorted by priority (high -> medium -> low) and added "
            "until the time budget was exhausted.",
        ]
        if skipped:
            lines.append(f"Skipped (did not fit): {', '.join(t.name for t in skipped)}.")
        return " ".join(lines)
