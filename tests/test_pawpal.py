"""Tests for core PawPal+ logic."""

from pawpal_system import Task, Pet, Owner


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
