"""
main.py — testing ground for PawPal+ logic.
Run with: python main.py
"""

from pawpal_system import (
    Owner, Pet, Task, Scheduler, Schedule,
    sort_tasks_by_time, filter_tasks, spawn_next_occurrence,
)

# ---------------------------------------------------------------------------
# Shared setup
# ---------------------------------------------------------------------------
owner = Owner(name="Jordan", available_minutes=90)

dog = Pet(name="Buddy", species="Dog", breed="Labrador", age_years=4)
cat = Pet(name="Luna",  species="Cat", breed="Siamese",  age_years=2)

owner.add_pet(dog)
owner.add_pet(cat)

# Tasks added OUT OF ORDER intentionally to prove sorting works
dog.add_task(Task(name="Brush coat",     category="grooming",    duration_minutes=20, priority="low"))
dog.add_task(Task(name="Morning walk",   category="walk",        duration_minutes=30, priority="high"))
dog.add_task(Task(name="Feed breakfast", category="feed",        duration_minutes=10, priority="high"))
cat.add_task(Task(name="Playtime",       category="enrichment",  duration_minutes=15, priority="medium"))
cat.add_task(Task(name="Litter box",     category="hygiene",     duration_minutes=10, priority="medium"))

# ---------------------------------------------------------------------------
# Scenario 1 — Both pets, 90-min budget (start times assigned)
# ---------------------------------------------------------------------------
scheduler = Scheduler(owner=owner, pets=[dog, cat])
schedule  = scheduler.generate_schedule(date="2026-03-29")

print("=" * 50)
print("  SCENARIO 1 - Both pets, 90-min budget")
print("=" * 50)
print(schedule.display())
print()
print("Reasoning:", scheduler.explain_plan())
print(f"Time remaining: {schedule.remaining_time(owner.available_minutes)} min")

# ---------------------------------------------------------------------------
# Scenario 2 — Tight budget, dog only (task skipped)
# ---------------------------------------------------------------------------
owner.update_availability(30)
scheduler2 = Scheduler(owner=owner, pets=[dog])
schedule2  = scheduler2.generate_schedule(date="2026-03-29")

print()
print("=" * 50)
print("  SCENARIO 2 - Dog only, 30-min budget")
print("=" * 50)
print(schedule2.display())
print()
print("Reasoning:", scheduler2.explain_plan())
print(f"Time remaining: {schedule2.remaining_time(owner.available_minutes)} min")

# ---------------------------------------------------------------------------
# Scenario 3 — Sort & filter demo
# ---------------------------------------------------------------------------
all_tasks = owner.get_all_tasks()

print()
print("=" * 50)
print("  SCENARIO 3 - Sort by time / filter demo")
print("=" * 50)

sorted_by_time = sort_tasks_by_time(schedule.selected_tasks)
print("Tasks in schedule sorted by start time:")
for t in sorted_by_time:
    print(f"  {t.start_time}  [{t.priority.upper()}] {t.pet_name}: {t.name}")

buddy_tasks = filter_tasks(all_tasks, pet_name="Buddy")
print(f"\nBuddy's tasks only ({len(buddy_tasks)}):")
for t in buddy_tasks:
    print(f"  {t.name} ({t.priority})")

done_tasks = filter_tasks(all_tasks, completed=True)
print(f"\nCompleted tasks: {len(done_tasks)}")

# ---------------------------------------------------------------------------
# Scenario 4 — Recurring tasks
# ---------------------------------------------------------------------------
print()
print("=" * 50)
print("  SCENARIO 4 - Recurring tasks")
print("=" * 50)

daily_walk = Task(name="Evening walk", category="walk",
                  duration_minutes=20, priority="high", recurrence="daily",
                  due_date="2026-03-29")
dog.add_task(daily_walk)

print(f"Task '{daily_walk.name}' | recurrence: {daily_walk.recurrence} | due: {daily_walk.due_date}")
daily_walk.mark_complete()
print(f"  Marked complete.")

next_task = spawn_next_occurrence(daily_walk, from_date=daily_walk.due_date)
if next_task:
    dog.add_task(next_task)
    print(f"  Next occurrence spawned: '{next_task.name}' due {next_task.due_date}")

# ---------------------------------------------------------------------------
# Scenario 5 — Conflict detection
# ---------------------------------------------------------------------------
print()
print("=" * 50)
print("  SCENARIO 5 - Conflict detection")
print("=" * 50)

# Build a schedule manually with two overlapping tasks
vet_visit = Task(name="Vet visit",  category="meds",     duration_minutes=60, priority="high",   start_time="09:00")
grooming  = Task(name="Grooming",   category="grooming", duration_minutes=45, priority="medium", start_time="09:30")
# Vet:      09:00 - 10:00
# Grooming: 09:30 - 10:15  <-- overlaps

conflict_schedule = Schedule("2026-03-29")
conflict_schedule.selected_tasks = [vet_visit, grooming]

dummy_scheduler = Scheduler(owner=owner, pets=[dog])
conflicts = dummy_scheduler.detect_conflicts(conflict_schedule)

print("Tasks with manually set overlapping times:")
print(f"  Vet visit:  09:00 - 10:00 (60 min)")
print(f"  Grooming:   09:30 - 10:15 (45 min)")
print()
if conflicts:
    for warning in conflicts:
        print(" ", warning)
else:
    print("  No conflicts detected.")

print("=" * 50)
