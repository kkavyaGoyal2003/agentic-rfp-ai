import streamlit as st

st.header("🔗 RFP URL Input")

urls_text = st.text_area(
    label="Enter RFP URLs (one per line)",
    height=200
)

uploaded_file = st.file_uploader(
    label="Upload URL list (.txt)",
    type=["txt"]
)

if st.button("Submit URLs"):
    urls = []

    if urls_text:
        urls.extend(
            [u.strip() for u in urls_text.splitlines() if u.strip()]
        )

    if uploaded_file is not None:
        file_urls = uploaded_file.read().decode("utf-8").splitlines()
        urls.extend([u.strip() for u in file_urls if u.strip()])

    # Remove duplicates
    st.session_state.urls = list(set(urls))

    st.success(f"{len(st.session_state.urls)} URLs queued successfully.")
