import streamlit as st

STAGE_ORDER = [
    "QUEUED",
    "FETCHING",
    "SUMMARIZING",
    "FILTERED",
    "DELIVERY"
]

STAGE_ICONS = {
    "QUEUED": "⏳",
    "FETCHING": "📡",
    "SUMMARIZING": "📝",
    "FILTERED": "🔍",
    "DELIVERY": "📦"
}

STAGE_LABELS = {
    "QUEUED": "Queued",
    "FETCHING": "Fetching Data",
    "SUMMARIZING": "Analyzing Content",
    "FILTERED": "Filtering Results",
    "DELIVERY": "Delivery"
}

def get_step_class(status):
    """Return CSS class based on status"""
    if status == "RUNNING":
        return "running"
    elif status in ("DONE", "ACCEPTED"):
        return "done"
    elif status == "SKIPPED":
        return "skipped"
    elif status == "ERROR":
        return "error"
    else:
        return "pending"

def get_step_icon(stage, status):
    """Return icon based on stage and status"""
    if status == "RUNNING":
        return "🔄"
    elif status in ("DONE", "ACCEPTED"):
        return "✅"
    elif status == "SKIPPED":
        return "⚠️"
    elif status == "ERROR":
        return "❌"
    else:
        return STAGE_ICONS.get(stage, "⏳")

def render_url_card(url, events):
    """Render URL card with progress tracking"""
    # Filter events for this URL
    url_events = [e for e in events if e.get("url") == url]
    
    # Build stage status map
    stage_status = {}
    for e in url_events:
        if e["type"] != "STATUS":
            continue
        stage = e.get("stage")
        stage_status[stage] = e
    
    # Card HTML header
    st.markdown(f"""
    <div class="url-card">
        <div class="url-header">
            <span class="url-icon">🔗</span>
            <span class="url-text">{url}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # No events yet - show queued state
    if not url_events:
        st.markdown("""
        <div class="progress-step pending">
            <span class="step-icon">⏳</span>
            <div class="step-content">
                <p class="step-title">Queued</p>
                <p class="step-status">Waiting to process</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Render each stage
        for stage in STAGE_ORDER:
            event = stage_status.get(stage)
            
            if not event:
                # Stage not reached yet
                st.markdown(f"""
                <div class="progress-step pending">
                    <span class="step-icon">{STAGE_ICONS.get(stage, '⏳')}</span>
                    <div class="step-content">
                        <p class="step-title">{STAGE_LABELS.get(stage, stage.title())}</p>
                        <p class="step-status">Pending</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                continue
            
            status = event.get("status", "")
            step_class = get_step_class(status)
            icon = get_step_icon(stage, status)
            
            st.markdown(f"""
            <div class="progress-step {step_class}">
                <span class="step-icon">{icon}</span>
                <div class="step-content">
                    <p class="step-title">{STAGE_LABELS.get(stage, stage.title())}</p>
                    <p class="step-status">{status.title()}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show error if present
            if "error" in event:
                st.error(f"⚠️ {event['error']}", icon="🚨")
    
    # Close card
    st.markdown("</div>", unsafe_allow_html=True)