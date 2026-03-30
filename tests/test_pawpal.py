"""Tests for core PawPal+ logic."""

from pawpal_system import Task, Pet


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
