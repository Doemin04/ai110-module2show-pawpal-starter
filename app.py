import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("PawPal+")

# ---------------------------------------------------------------------------
# Session-state initialisation
# Runs once per browser session; survives reruns because of the "not in" guard.
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None

# ---------------------------------------------------------------------------
# Section 1 — Owner profile
# ---------------------------------------------------------------------------
st.subheader("1. Owner Profile")

if st.session_state.owner is None:
    with st.form("owner_form"):
        owner_name       = st.text_input("Your name", value="Jordan")
        avail_minutes    = st.number_input("Daily available time (min)",
                                           min_value=10, max_value=480, value=90)
        save_owner       = st.form_submit_button("Save Profile")
    if save_owner:
        st.session_state.owner = Owner(name=owner_name,
                                       available_minutes=int(avail_minutes))
        st.rerun()
    st.stop()          # nothing else makes sense without an owner

owner = st.session_state.owner  # convenient alias for the rest of the script

col_info, col_edit = st.columns([3, 1])
col_info.success(f"**{owner.name}** — {owner.available_minutes} min/day available")
if col_edit.button("Edit"):
    st.session_state.owner = None
    st.rerun()

# ---------------------------------------------------------------------------
# Section 2 — Pets
# ---------------------------------------------------------------------------
st.divider()
st.subheader("2. My Pets")

if owner.pets:
    for pet in owner.pets:
        st.markdown(f"- **{pet.name}** — {pet.get_profile()} "
                    f"({len(pet.tasks)} task(s))")

with st.form("add_pet_form"):
    c1, c2, c3, c4 = st.columns(4)
    new_pet_name    = c1.text_input("Name",        value="Buddy")
    new_pet_species = c2.selectbox("Species",      ["Dog", "Cat", "Other"])
    new_pet_breed   = c3.text_input("Breed",       value="Labrador")
    new_pet_age     = c4.number_input("Age (yrs)", min_value=0, max_value=30, value=3)
    add_pet         = st.form_submit_button("Add Pet")

if add_pet:
    owner.add_pet(Pet(name=new_pet_name,
                      species=new_pet_species,
                      breed=new_pet_breed,
                      age_years=int(new_pet_age)))
    st.rerun()

# ---------------------------------------------------------------------------
# Section 3 — Tasks
# ---------------------------------------------------------------------------
st.divider()
st.subheader("3. Tasks")

if not owner.pets:
    st.info("Add a pet first before adding tasks.")
else:
    with st.form("add_task_form"):
        pet_map          = {p.name: p for p in owner.pets}
        target_pet_name  = st.selectbox("Assign to pet", list(pet_map.keys()))
        c1, c2, c3       = st.columns(3)
        new_task_name    = c1.text_input("Task name", value="Morning walk")
        new_task_cat     = c2.selectbox("Category",
                                        ["walk", "feed", "meds",
                                         "grooming", "enrichment", "hygiene", "other"])
        new_task_dur     = c3.number_input("Duration (min)",
                                           min_value=1, max_value=240, value=20)
        new_task_pri     = st.selectbox("Priority", ["high", "medium", "low"])
        new_task_notes   = st.text_input("Notes (optional)", value="")
        add_task         = st.form_submit_button("Add Task")

    if add_task:
        pet_map[target_pet_name].add_task(
            Task(name=new_task_name,
                 category=new_task_cat,
                 duration_minutes=int(new_task_dur),
                 priority=new_task_pri,
                 notes=new_task_notes)
        )
        st.rerun()

    for pet in owner.pets:
        if pet.tasks:
            st.markdown(f"**{pet.name}'s tasks:**")
            st.table([
                {"Task": t.name, "Category": t.category,
                 "Min": t.duration_minutes, "Priority": t.priority,
                 "Done": t.completed}
                for t in pet.tasks
            ])

# ---------------------------------------------------------------------------
# Section 4 — Generate schedule
# ---------------------------------------------------------------------------
st.divider()
st.subheader("4. Generate Schedule")

all_tasks = owner.get_all_tasks()
if not owner.pets or not all_tasks:
    st.info("Add at least one pet with tasks before generating a schedule.")
else:
    pet_names      = [p.name for p in owner.pets]
    selected_names = st.multiselect("Include pets", pet_names, default=pet_names)
    avail_override = st.number_input("Available time (min)",
                                     min_value=10, max_value=480,
                                     value=owner.available_minutes)
    schedule_date  = st.date_input("Date")

    if st.button("Generate Schedule"):
        selected_pets = [p for p in owner.pets if p.name in selected_names]
        if not selected_pets:
            st.warning("Select at least one pet.")
        else:
            owner.update_availability(int(avail_override))
            scheduler = Scheduler(owner=owner, pets=selected_pets)
            schedule  = scheduler.generate_schedule(date=str(schedule_date))

            st.success("Schedule generated!")
            st.text(schedule.display())
            st.markdown("**Reasoning:**")
            st.info(scheduler.explain_plan())
            st.metric("Time remaining", f"{schedule.remaining_time(owner.available_minutes)} min")
