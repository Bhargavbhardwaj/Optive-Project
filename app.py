import streamlit as st
import os
import tempfile
from Phase1_FileAnalyzer.file_analyzer import run_phase1
from Phase2_Cleansing.main import run_phase2
from Phase3_Analyzer.main import run_phase3

st.set_page_config(page_title="Document Analyzer", layout="wide")

st.title("📂 Document Analysis Pipeline")
st.write("Upload a file or ZIP archive. The system will run **Phase 1 → Phase 2 → Phase 3** and generate reports.")

# Upload file
uploaded_file = st.file_uploader("Upload file or ZIP", type=None)

if uploaded_file:
    # Save uploaded file to temp dir
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, uploaded_file.name)
        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())

        st.success(f"File uploaded: {uploaded_file.name}")

        # --- Run Phase 1 ---
        st.info("🔍 Running Phase 1: File Analyzer...")
        phase1 = run_phase1(input_path, output_dir=os.path.join(tmpdir, "phase1_output"))
        st.write("**Phase 1 Results:**")
        st.dataframe(phase1["results"])

        # --- Run Phase 2 ---
        st.info("🧹 Running Phase 2: File Cleansing...")
        phase2 = run_phase2(phase1["csv_path"], output_dir=os.path.join(tmpdir, "phase2_output"))
        st.success("Phase 2 completed ✅")

        # --- Run Phase 3 ---
        st.info("📊 Running Phase 3: Analysis & Report Generation...")
        phase3 = run_phase3(phase2["csv_path"], output_dir=os.path.join(tmpdir, "phase3_output"))
        st.success("Phase 3 completed ✅")

        # Show Phase 3 results in table
        st.write("**Final Report (Phase 3):**")
        st.dataframe(phase3["results"])

        # --- Download buttons ---
        with open(phase3["csv_path"], "rb") as f:
            st.download_button("⬇️ Download CSV Report", f, file_name="phase3_report.csv")

        with open(phase3["txt_path"], "rb") as f:
            st.download_button("⬇️ Download TXT Report", f, file_name="phase3_report.txt")
