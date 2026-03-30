"""Tests for core PawPal+ logic."""

from pawpal_system import (
    Task, Pet, Owner, Scheduler, Schedule,
    sort_tasks_by_time, filter_tasks, spawn_next_occurrence,
)


# ---------------------------------------------------------------------------
# Existing: basic class behaviour
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """Calling mark_complete() should set task.completed to True."""
    task = Task(name="Walk", category="walk", duration_minutes=20, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a pet should increase its task list by one."""
    pet = Pet(name="Buddy", species="Dog", breed="Labrador", age_years=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task(name="Feed", category="feed", duration_minutes=10, priority="medium"))
    assert len(pet.tasks) == 1


def test_add_pet_stores_pet_object_on_owner():
    """add_pet() should store a real Pet instance (not a dict) that persists on the owner."""
    owner = Owner(name="Jordan", available_minutes=90)
    pet = Pet(name="Luna", species="Cat", breed="Siamese", age_years=2)
    owner.add_pet(pet)
    assert len(owner.pets) == 1
    assert isinstance(owner.pets[0], Pet)
    assert owner.pets[0].name == "Luna"


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

def test_sort_tasks_by_time_returns_chronological_order():
    """Tasks added in random time order should come back sorted earliest-first."""
    t1 = Task(name="A", category="walk", duration_minutes=10, priority="low",  start_time="10:00")
    t2 = Task(name="B", category="feed", duration_minutes=10, priority="low",  start_time="08:00")
    t3 = Task(name="C", category="feed", duration_minutes=10, priority="high", start_time="09:30")

    result = sort_tasks_by_time([t1, t2, t3])

    assert [t.start_time for t in result] == ["08:00", "09:30", "10:00"]


def test_sort_tasks_no_start_time_goes_last():
    """A task with no start_time should sort after all timed tasks."""
    timed   = Task(name="Walk",    category="walk", duration_minutes=20, priority="high", start_time="08:00")
    untimed = Task(name="Groom",   category="grooming", duration_minutes=15, priority="low")

    result = sort_tasks_by_time([untimed, timed])

    assert result[0].name == "Walk"
    assert result[1].name == "Groom"


# ---------------------------------------------------------------------------
# Recurrence
# ---------------------------------------------------------------------------

def test_spawn_next_occurrence_daily_adds_one_day():
    """A daily task's next occurrence should be due the following day."""
    task = Task(name="Walk", category="walk", duration_minutes=20,
                priority="high", recurrence="daily", due_date="2026-03-29")
    task.mark_complete()

    next_task = spawn_next_occurrence(task, from_date="2026-03-29")

    assert next_task is not None
    assert next_task.due_date == "2026-03-30"
    assert next_task.completed is False


def test_spawn_next_occurrence_weekly_adds_seven_days():
    """A weekly task's next occurrence should be due seven days later."""
    task = Task(name="Bath", category="grooming", duration_minutes=30,
                priority="medium", recurrence="weekly", due_date="2026-03-29")

    next_task = spawn_next_occurrence(task, from_date="2026-03-29")

    assert next_task is not None
    assert next_task.due_date == "2026-04-05"


def test_spawn_next_occurrence_none_recurrence_returns_none():
    """spawn_next_occurrence should return None for a non-recurring task."""
    task = Task(name="One-off", category="meds", duration_minutes=10, priority="high")

    result = spawn_next_occurrence(task, from_date="2026-03-29")

    assert result is None


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def _make_conflict_scheduler() -> Scheduler:
    owner = Owner(name="Test", available_minutes=120)
    pet   = Pet(name="Rex", species="Dog", breed="Mix", age_years=2)
    owner.add_pet(pet)
    return Scheduler(owner=owner, pets=[pet])


def test_detect_conflicts_flags_overlapping_tasks():
    """Two tasks whose time windows overlap should produce a conflict warning."""
    t1 = Task(name="Vet",     category="meds",     duration_minutes=60, priority="high",   start_time="09:00")
    t2 = Task(name="Groom",   category="grooming", duration_minutes=45, priority="medium", start_time="09:30")
    # Vet:   09:00-10:00
    # Groom: 09:30-10:15  → overlap

    schedule = Schedule("2026-03-29")
    schedule.selected_tasks = [t1, t2]

    warnings = _make_conflict_scheduler().detect_conflicts(schedule)

    assert len(warnings) == 1
    assert "Vet" in warnings[0]
    assert "Groom" in warnings[0]


def test_detect_conflicts_no_warning_for_sequential_tasks():
    """Tasks that end exactly when the next begins should not be flagged."""
    t1 = Task(name="Walk",  category="walk", duration_minutes=30, priority="high",   start_time="08:00")
    t2 = Task(name="Feed",  category="feed", duration_minutes=10, priority="medium", start_time="08:30")
    # Walk: 08:00-08:30
    # Feed: 08:30-08:40  → touching, not overlapping

    schedule = Schedule("2026-03-29")
    schedule.selected_tasks = [t1, t2]

    warnings = _make_conflict_scheduler().detect_conflicts(schedule)

    assert warnings == []


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_scheduler_produces_empty_schedule_for_pet_with_no_tasks():
    """A pet with no tasks should result in an empty schedule, not an error."""
    owner = Owner(name="Alex", available_minutes=60)
    pet   = Pet(name="Empty", species="Cat", breed="Persian", age_years=1)
    owner.add_pet(pet)

    schedule = Scheduler(owner=owner, pets=[pet]).generate_schedule("2026-03-29")

    assert schedule.selected_tasks == []
    assert schedule.total_duration_minutes == 0


def test_scheduler_skips_task_that_exceeds_budget():
    """A single task longer than the available budget should not appear in the schedule."""
    owner = Owner(name="Alex", available_minutes=20)
    pet   = Pet(name="Buddy", species="Dog", breed="Lab", age_years=3)
    pet.add_task(Task(name="Long walk", category="walk", duration_minutes=60, priority="high"))
    owner.add_pet(pet)

    schedule = Scheduler(owner=owner, pets=[pet]).generate_schedule("2026-03-29")

    assert schedule.selected_tasks == []


def test_filter_tasks_by_pet_name():
    """filter_tasks with a pet_name should return only that pet's tasks."""
    t1 = Task(name="Walk", category="walk", duration_minutes=20, priority="high", pet_name="Buddy")
    t2 = Task(name="Feed", category="feed", duration_minutes=10, priority="medium", pet_name="Luna")

    result = filter_tasks([t1, t2], pet_name="Buddy")

    assert len(result) == 1
    assert result[0].name == "Walk"


def test_filter_tasks_by_completed_status():
    """filter_tasks with completed=True should return only finished tasks."""
    done    = Task(name="Done task",    category="walk", duration_minutes=10, priority="low",  completed=True)
    pending = Task(name="Pending task", category="feed", duration_minutes=10, priority="high", completed=False)

    result = filter_tasks([done, pending], completed=True)

    assert len(result) == 1
    assert result[0].name == "Done task"
