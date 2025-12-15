import streamlit as st

STAGE_ORDER = [
    "QUEUED",
    "FETCHING",
    "SUMMARIZING",
    "FILTERED",
    "DELIVERY"
]

def render_progress(events):
    stage_status = {}

    for e in events:
        if e["type"] != "STATUS":
            continue
        stage = e.get("stage")
        stage_status[stage] = e

    for stage in STAGE_ORDER:
        event = stage_status.get(stage)

        if not event:
            st.write(f"⏳ {stage.title()} — pending")
            continue

        status = event.get("status", "")
        icon = "⏳"

        if status == "RUNNING":
            icon = "🔄"
        elif status in ("DONE", "ACCEPTED"):
            icon = "✅"
        elif status == "SKIPPED":
            icon = "⚠️"
        elif stage == "ERROR":
            icon = "❌"

        st.write(f"{icon} **{stage.title()}** — {status}")

        if "error" in event:
            st.error(event["error"])
