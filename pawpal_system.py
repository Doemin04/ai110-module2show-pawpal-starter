"""
PawPal+ — logic layer
All backend classes live here. UI and tests import from this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta


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
    pet_name: str = ""          # set automatically by Pet.add_task()
    start_time: str = ""        # "HH:MM", assigned by Scheduler
    recurrence: str = "none"    # "none", "daily", or "weekly"
    due_date: str = ""          # "YYYY-MM-DD", used by recurring tasks

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
        """Attach a care task to this pet and stamp the pet's name on it."""
        task.pet_name = self.name
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
        """Create an owner with a daily time budget and optional preferences."""
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


# ---------------------------------------------------------------------------
# Module-level algorithmic helpers
# ---------------------------------------------------------------------------

def _time_str_to_minutes(t: str) -> int:
    """Convert 'HH:MM' to total minutes since midnight."""
    h, m = map(int, t.split(":"))
    return h * 60 + m


def sort_tasks_by_time(tasks: list[Task]) -> list[Task]:
    """Return tasks sorted by start_time ascending; tasks with no time go last."""
    return sorted(tasks, key=lambda t: t.start_time if t.start_time else "99:99")


def filter_tasks(
    tasks: list[Task],
    *,
    completed: bool | None = None,
    pet_name: str | None = None,
) -> list[Task]:
    """Return tasks matching all supplied filters; omit a filter to skip it."""
    result = tasks
    if completed is not None:
        result = [t for t in result if t.completed == completed]
    if pet_name is not None:
        result = [t for t in result if t.pet_name == pet_name]
    return result


def spawn_next_occurrence(task: Task, from_date: str) -> Task | None:
    """Return a fresh Task for the next occurrence of a recurring task, or None if non-recurring."""
    if task.recurrence == "none":
        return None
    delta = timedelta(days=1) if task.recurrence == "daily" else timedelta(weeks=1)
    next_date = str(date.fromisoformat(from_date) + delta)
    return Task(
        name=task.name,
        category=task.category,
        duration_minutes=task.duration_minutes,
        priority=task.priority,
        notes=task.notes,
        recurrence=task.recurrence,
        due_date=next_date,
        pet_name=task.pet_name,
    )


_PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


class Schedule:
    def __init__(self, date: str) -> None:
        """Create an empty schedule for the given date."""
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
            pet_label  = f"{task.pet_name}: " if task.pet_name else ""
            time_label = f" @ {task.start_time}" if task.start_time else ""
            lines.append(
                f"  {i}. [{task.priority.upper()}] {pet_label}{task.name}"
                f"{time_label} ({task.category}) - {status}"
            )
        lines.append(f"  Total: {self.total_duration_minutes} min")
        return "\n".join(lines)

    def remaining_time(self, available_minutes: int) -> int:
        """Return how many minutes are left after the scheduled tasks."""
        return available_minutes - self.total_duration_minutes


class Scheduler:
    def __init__(self, owner: Owner, pets: list[Pet]) -> None:
        """Create a scheduler for the given owner and selected list of pets."""
        self.owner = owner
        self.pets = pets
        self.last_schedule: Schedule | None = None  # set by generate_schedule()

    def _pending_tasks(self) -> list[Task]:
        """Return all incomplete tasks from the selected pets only."""
        return [t for pet in self.pets for t in pet.tasks if not t.completed]

    def generate_schedule(self, date: str, day_start: str = "08:00") -> Schedule:
        """Sort pending tasks by priority, fit as many as possible into the time budget, assign start times, and store the result."""
        schedule = Schedule(date)
        sorted_tasks = sorted(
            self._pending_tasks(),
            key=lambda t: (_PRIORITY_ORDER.get(t.priority, 99), t.name),
        )
        budget = self.owner.available_minutes
        current = _time_str_to_minutes(day_start)
        for task in sorted_tasks:
            if task.duration_minutes <= budget:
                h, m = divmod(current, 60)
                task.start_time = f"{h:02d}:{m:02d}"
                schedule.selected_tasks.append(task)
                schedule.total_duration_minutes += task.duration_minutes
                budget -= task.duration_minutes
                current += task.duration_minutes
        self.last_schedule = schedule
        return schedule

    def detect_conflicts(self, schedule: Schedule) -> list[str]:
        """Check scheduled tasks for overlapping time windows and return a warning string for each conflict found."""
        warnings: list[str] = []
        timed = [t for t in schedule.selected_tasks if t.start_time]
        for i, t1 in enumerate(timed):
            for t2 in timed[i + 1:]:
                s1, e1 = _time_str_to_minutes(t1.start_time), _time_str_to_minutes(t1.start_time) + t1.duration_minutes
                s2, e2 = _time_str_to_minutes(t2.start_time), _time_str_to_minutes(t2.start_time) + t2.duration_minutes
                if s1 < e2 and s2 < e1:
                    end1 = f"{e1 // 60:02d}:{e1 % 60:02d}"
                    end2 = f"{e2 // 60:02d}:{e2 % 60:02d}"
                    warnings.append(
                        f"CONFLICT: '{t1.name}' ({t1.start_time}-{end1})"
                        f" overlaps '{t2.name}' ({t2.start_time}-{end2})"
                    )
        return warnings

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
        all_pending = self._pending_tasks()
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
