#
import streamlit as st

page_title = "NDAI DenHub"

st.set_page_config(
    page_title=page_title,
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

st.title(page_title)

# -----------------------------------------
st.subheader("- Billing Automation")

st.page_link(
    "pages/bill-step01-ocr.py",
    label="Step 1 - Pdf Bill Reader w. OCR",
    icon="🛞"
)

st.page_link(
    "pages/bill-step01-api.py",
    label="Step 1b - Pdf Bill Reader w. API",
    icon="🛞"
)

st.page_link(
    "pages/bill-step02-odapi.py",
    label="Step 2 - OpenDental API Reader",
    icon="🛞"
)

st.page_link(
    "pages/bill-step02-mysql.py",
    label="Step 2b - OpenDental MySQL Client",
    icon="🛞"
)

st.page_link(
    "pages/billing-agent.py",
    label="DenHub - Billing Agent",
    icon="🛞"
)

# -----------------------------------------

# -----------------------------------------
st.subheader("- Old Pages")
st.page_link(
    "pages/invoice-reader.py",
    label="Invoice Reader - Using OpenAI API",
    icon="🎁"
)

