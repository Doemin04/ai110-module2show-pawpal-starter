"""
main.py — temporary testing ground for PawPal+ logic.
Run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=90)

dog = Pet(name="Buddy", species="Dog", breed="Labrador", age_years=4)
cat = Pet(name="Luna",  species="Cat", breed="Siamese",  age_years=2)

owner.add_pet(dog)
owner.add_pet(cat)

# --- Tasks for Buddy ---
dog.add_task(Task(name="Morning walk",   category="walk",     duration_minutes=30, priority="high"))
dog.add_task(Task(name="Feed breakfast", category="feed",     duration_minutes=10, priority="high"))
dog.add_task(Task(name="Brush coat",     category="grooming", duration_minutes=20, priority="low"))

# --- Tasks for Luna ---
cat.add_task(Task(name="Litter box clean", category="hygiene", duration_minutes=10, priority="medium"))
cat.add_task(Task(name="Playtime",         category="enrichment", duration_minutes=15, priority="medium"))

# --- Scenario 1: both pets, comfortable budget (90 min) ---
scheduler = Scheduler(owner=owner, pets=[dog, cat])
schedule  = scheduler.generate_schedule(date="2026-03-29")

print("=" * 45)
print("  SCENARIO 1 — Both pets, 90-min budget")
print("=" * 45)
print(schedule.display())
print()
print("Reasoning:")
print(scheduler.explain_plan())
print(f"Time remaining: {schedule.remaining_time(owner.available_minutes)} min")

# --- Scenario 2: tight budget — only 30 min, dog only ---
owner.update_availability(30)
scheduler2 = Scheduler(owner=owner, pets=[dog])
schedule2  = scheduler2.generate_schedule(date="2026-03-29")

print()
print("=" * 45)
print("  SCENARIO 2 — Dog only, 30-min budget")
print("=" * 45)
print(schedule2.display())
print()
print("Reasoning:")
print(scheduler2.explain_plan())
print(f"Time remaining: {schedule2.remaining_time(owner.available_minutes)} min")
print("=" * 45)
