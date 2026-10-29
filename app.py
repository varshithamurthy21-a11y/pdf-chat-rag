"""
app.py - starting point of the app. Run:  streamlit run app.py

It sets up the page menu in the sidebar and applies the colour theme,
then shows whichever page the user picked.
"""

import streamlit as st

from theme import apply_theme

st.set_page_config(page_title="PDF Studio", page_icon="📄", layout="wide")

page = st.navigation([
    st.Page("chat_page.py", title="Chat with PDF", icon="💬", default=True),
    st.Page("views/3_Exam_Prep.py", title="Exam Prep", icon="🎯"),
    st.Page("views/4_Notes_Scanner.py", title="Notes Scanner", icon="📸"),
    st.Page("views/1_Image_to_PDF.py", title="Image to PDF", icon="🖼️"),
    st.Page("views/2_JPEG_Converter.py", title="JPEG Converter", icon="🔄"),
    st.Page("views/5_PDF_Tools.py", title="PDF Tools", icon="🧰"),
])

apply_theme()
page.run()
