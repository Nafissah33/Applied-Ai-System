import os

import streamlit as st

from pawpal_system import DEFAULT_DATA_FILE, PRIORITY_ICONS, Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+ AI", page_icon="🐾", layout="centered")

REPO_URL = "https://github.com/Nafissah33/Applied-Ai-System"

st.markdown(
    """
<style>
h1, h2, h3 { letter-spacing: -0.01em; }
.hero { background: #12263A; color: #F6F1E7; padding: 28px 32px; border-radius: 18px; margin-bottom: 8px; }
.hero h1 { color: #F6F1E7; margin: 0 0 6px 0; font-size: 2.3rem; }
.hero p { color: #B9C4CF; margin: 0; font-size: 1.05rem; }
.hero .tag { color: #E07A3F; font-weight: 600; letter-spacing: 0.08em; font-size: 0.8rem; }
</style>
<div class="hero">
  <div class="tag">APPLIED AI FINAL PROJECT</div>
  <h1>🐾 PawPal+ AI</h1>
  <p>Describe your pet in plain English and get a safe, explained daily care plan.
  It retrieves care guidance, checks its own work, and shows its sources.</p>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### 🐾 PawPal+ AI")
    st.caption("Nafissatou LO · 491 Applied AI for Engineers · Fall 2026")
    st.markdown(f"[View the code on GitHub]({REPO_URL})")
    st.divider()
    st.markdown("**How it works**")
    st.markdown(
        "1. Checks your request is safe\n"
        "2. Reads your pet's age and conditions\n"
        "3. Retrieves care guidance (RAG)\n"
        "4. Builds and double-checks the plan\n"
        "5. Explains each task with its source"
    )
    st.divider()
    st.info(
        "PawPal+ plans routine care. It does **not** give medical advice or doses. "
        "For health concerns or emergencies, contact a veterinarian."
    )

from pawpal_ai import AIPlanner  # noqa: E402

# Build the Owner once per session (every Streamlit rerun would otherwise reset it). If a data.json from a
# previous run exists, load it instead of starting fresh.
if "owner" not in st.session_state:
    if os.path.exists(DEFAULT_DATA_FILE):
        st.session_state.owner = Owner.load_from_json(DEFAULT_DATA_FILE)
    else:
        st.session_state.owner = Owner(name="Nafissatou", pets=[Pet(name="Mochi", species="dog")])

owner: Owner = st.session_state.owner


@st.cache_resource
def _get_planner() -> AIPlanner:
    return AIPlanner()


tab_ai, tab_manage = st.tabs(["🤖 AI Planner", "📋 My pets & schedule"])

with tab_ai:
    st.subheader("Plan a day with AI")
    st.caption(
        "Describe your pet and your time. The planner retrieves care guidance from the knowledge base, "
        "applies guardrails, schedules with the PawPal+ Scheduler, and explains every choice. Runs offline."
    )
    ai_request = st.text_input(
        "Describe your pet and time available",
        value="I have a senior dog with arthritis, I only have 45 minutes today",
    )
    use_retrieval = st.checkbox("Use retrieval (RAG)", value=True)

    if st.button("Plan with AI", type="primary"):
        st.session_state.ai_result = _get_planner().plan(ai_request, use_retrieval=use_retrieval)

    ai_result = st.session_state.get("ai_result")
    if ai_result is not None:
        if ai_result.status == "refused":
            st.error(ai_result.message)
        elif ai_result.status == "error":
            st.error(ai_result.message)
        else:
            for warning in ai_result.warnings:
                st.warning(warning)
            st.metric("Confidence", f"{ai_result.confidence:.0%}")
            st.table(
                [
                    {
                        "start": e["start_time"],
                        "end": e["end_time"],
                        "task": e["task"].title,
                        "priority": e["task"].priority,
                        "minutes": e["task"].duration_minutes,
                    }
                    for e in ai_result.plan
                ]
            )
            with st.expander("Why this plan? (sources and explanations)"):
                for chunk in ai_result.retrieved:
                    st.markdown(f"- **{chunk.citation}** (relevance {chunk.score})")
                st.text(ai_result.explanation)
            if owner.pets:
                target_name = st.selectbox("Add these tasks to", [p.name for p in owner.pets], key="ai_target_pet")
                if st.button("Add plan to this pet"):
                    target = next(p for p in owner.pets if p.name == target_name)
                    AIPlanner.apply_to_pet(ai_result, target)
                    st.success(f"Added {len(ai_result.plan)} tasks to {target.name}. See the next tab.")
        with st.expander("Agent trace"):
            for i, step in enumerate(ai_result.trace, 1):
                tool = f" `[tool: {step['tool']}]`" if step.get("tool") else ""
                st.markdown(f"{i}. **{step['step']}**{tool}: {step['detail']}")

with tab_manage:
    st.subheader("Your pets")
    new_owner_name = st.text_input("Owner name", value=owner.name)
    owner.name = new_owner_name or owner.name

    save_col, load_col = st.columns(2)
    with save_col:
        if st.button("💾 Save data"):
            owner.save_to_json(DEFAULT_DATA_FILE)
            st.success(f"Saved to {DEFAULT_DATA_FILE}.")
    with load_col:
        if st.button("📂 Reload from file"):
            if os.path.exists(DEFAULT_DATA_FILE):
                st.session_state.owner = Owner.load_from_json(DEFAULT_DATA_FILE)
                st.rerun()
            else:
                st.warning(f"No {DEFAULT_DATA_FILE} found yet — save first.")

    st.divider()

    st.subheader("Add a Pet")
    with st.form("add_pet_form", clear_on_submit=True):
        new_pet_name = st.text_input("New pet's name")
        new_species = st.selectbox("New pet's species", ["dog", "cat", "other"], key="new_species")
        new_breed = st.text_input("Breed (optional)")
        if st.form_submit_button("Add pet") and new_pet_name:
            owner.add_pet(Pet(name=new_pet_name, species=new_species, breed=new_breed))
            st.success(f"Added {new_pet_name}.")

    pet_names = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox("Manage tasks for", pet_names)
    pet: Pet = next(p for p in owner.pets if p.name == selected_pet_name)

    st.markdown("### Tasks")
    st.caption(f"Tasks for {pet.name}.")

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5 = st.columns(2)
    with col4:
        preferred_time = st.text_input("Preferred time (HH:MM, optional)", value="")
    with col5:
        recurrence = st.selectbox("Recurrence", ["", "daily", "weekly"])

    if st.button("Add task"):
        pet.add_task(
            Task(
                title=task_title,
                duration_minutes=int(duration),
                priority=priority,
                recurrence=recurrence,
                preferred_time=preferred_time or None,
            )
        )
        st.success(f"Added \"{task_title}\" for {pet.name}.")

    tasks = pet.get_tasks()
    if tasks:
        st.write("Current tasks:")
        header = st.columns([3, 2, 2, 2, 2])
        for col, label in zip(header, ["Task", "Duration", "Priority", "Preferred time", ""]):
            col.markdown(f"**{label}**")
        for t in tasks:
            row = st.columns([3, 2, 2, 2, 2])
            row[0].write(f"~~{t.title}~~" if t.completed else t.title)
            row[1].write(f"{t.duration_minutes} min")
            row[2].write(PRIORITY_ICONS.get(t.priority, t.priority))
            row[3].write(t.preferred_time or "—")
            if t.completed:
                row[4].write("✅ done")
            elif row[4].button("Mark complete", key=f"complete-{t.id}"):
                pet.complete_task(t)
                st.rerun()
    else:
        st.info("No tasks yet. Add one above.")

    st.divider()

    st.subheader("Build Schedule")
    available_minutes = st.number_input("Minutes available today", min_value=1, max_value=600, value=60)
    scheduler = Scheduler(available_minutes=int(available_minutes))

    all_tasks = owner.get_all_tasks()
    pet_name_by_task_id = {t.id: p.name for p in owner.pets for t in p.get_tasks()}

    conflicts = scheduler.detect_conflicts(all_tasks)
    if conflicts:
        st.warning(f"⚠️ {len(conflicts)} scheduling conflict(s) found — you may want to adjust these times:")
        for task_a, task_b in conflicts:
            pet_a = pet_name_by_task_id.get(task_a.id, "?")
            pet_b = pet_name_by_task_id.get(task_b.id, "?")
            task_a_slot = scheduler.generate_plan([task_a], start_time=task_a.preferred_time)
            suggested_time = scheduler.find_next_available_slot(
                task_a_slot, task_b.duration_minutes, preferred_time=task_b.preferred_time
            )
            st.warning(
                f"**{task_a.preferred_time}** — \"{task_a.title}\" ({pet_a}) and "
                f"\"{task_b.title}\" ({pet_b}) are both set for this time. "
                f"Try moving \"{task_b.title}\" to **{suggested_time}** instead."
            )

    with st.expander("All tasks, sorted by priority"):
        sorted_tasks = scheduler.sort_tasks(all_tasks)
        if sorted_tasks:
            st.table(
                [
                    {
                        "pet": pet_name_by_task_id.get(t.id, ""),
                        "title": t.title,
                        "priority": PRIORITY_ICONS.get(t.priority, t.priority),
                        "duration_minutes": t.duration_minutes,
                    }
                    for t in sorted_tasks
                ]
            )
        else:
            st.info("No tasks yet.")

    if st.button("Generate schedule"):
        plan = scheduler.generate_plan_for_owner(owner)
        if plan:
            st.success(f"Schedule generated for {owner.name}'s pets!")
            st.table(
                [
                    {
                        "start": entry["start_time"],
                        "end": entry["end_time"],
                        "pet": pet_name_by_task_id.get(entry["task"].id, ""),
                        "task": entry["task"].title,
                        "reason": entry["reason"],
                    }
                    for entry in plan
                ]
            )
            total_used = sum(entry["task"].duration_minutes for entry in plan)
            st.caption(f"Total time used: {total_used}/{available_minutes} minutes.")
        else:
            st.info(scheduler.explain_plan(plan))
