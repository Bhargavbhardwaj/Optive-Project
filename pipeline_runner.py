# pipeline_runner.py
import os
import sys
import subprocess
import logging
from typing import Tuple

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ROOT = os.path.dirname(os.path.abspath(__file__))

def _run_subprocess(script_path: str, args: list):
    cmd = [sys.executable, script_path] + args
    logger.info("Running subprocess: %s", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        logger.error("Subprocess failed: %s", proc.stderr)
        raise RuntimeError(f"Script {script_path} exited with {proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}")
    return proc.stdout

# Try direct import wrappers first (recommended). If not available, fallback to subprocess.
def run_phase1(input_dir: str, output_dir: str):
    """
    Run Phase1. Prefer direct function `analyze_files`, else call file_analyzer.py CLI.
    """
    try:
        sys.path.insert(0, ROOT)
        from Phase1_FileAnalyzer.file_analyzer import analyze_files  # type: ignore
        logger.info("Using direct import analyze_files from Phase1_FileAnalyzer")
        return analyze_files(input_dir, output_dir)
    except Exception as e:
        logger.info("Direct import for Phase1 failed (%s). Falling back to subprocess.", e)
        script = os.path.join(ROOT, "Phase1_FileAnalyzer", "file_analyzer.py")
        _run_subprocess(script, ["--input", input_dir, "--output", output_dir])
        # assume outputs are in output_dir: return a path or None. For consistency return output_dir
        return output_dir

def run_phase2(input_dir: str, output_dir: str):
    """
    Run Phase2. Prefer direct function `cleanse_files`, else call Phase2_Cleansing/main.py CLI.
    """
    try:
        sys.path.insert(0, ROOT)
        from Phase2_Cleansing.main import cleanse_files  # type: ignore
        logger.info("Using direct import cleanse_files from Phase2_Cleansing")
        return cleanse_files(input_dir, output_dir)
    except Exception as e:
        logger.info("Direct import for Phase2 failed (%s). Falling back to subprocess.", e)
        script = os.path.join(ROOT, "Phase2_Cleansing", "main.py")
        _run_subprocess(script, ["--input", input_dir, "--output", output_dir])
        return output_dir

def run_phase3(input_dir: str, output_dir: str) -> Tuple[str, str]:
    """
    Run Phase3. Prefer direct function `run_analysis` returning (csv_path, txt_path),
    else call Phase3_Analyzer/main.py and return paths where we expect outputs.
    """
    try:
        sys.path.insert(0, ROOT)
        from Phase3_Analyzer.main import run_analysis  # type: ignore
        logger.info("Using direct import run_analysis from Phase3_Analyzer")
        return run_analysis(input_dir, output_dir)
    except Exception as e:
        logger.info("Direct import for Phase3 failed (%s). Falling back to subprocess.", e)
        script = os.path.join(ROOT, "Phase3_Analyzer", "main.py")
        _run_subprocess(script, ["--input", input_dir, "--output", output_dir])
        # assume the script wrote 'phase3_report.csv' and 'phase3_report.txt' into output_dir
        csv_path = os.path.join(output_dir, "phase3_report.csv")
        txt_path = os.path.join(output_dir, "phase3_report.txt")
        if not os.path.exists(csv_path) or not os.path.exists(txt_path):
            raise FileNotFoundError(f"Expected output files not found in {output_dir}")
        return csv_path, txt_path

def run_pipeline(uploaded_dir: str, working_dir: str) -> Tuple[str, str]:
    """
    orchestrate Phase1 -> Phase2 -> Phase3 using directories.
    uploaded_dir: directory that contains extracted uploaded files
    working_dir: temp working directory where intermediate outputs are written
    Returns (report_csv_path, report_txt_path)
    """
    os.makedirs(working_dir, exist_ok=True)
    phase1_out = os.path.join(working_dir, "phase1_out")
    cleansing_out = os.path.join(working_dir, "cleansed_output")
    phase3_out = os.path.join(working_dir, "phase3_out")

    os.makedirs(phase1_out, exist_ok=True)
    os.makedirs(cleansing_out, exist_ok=True)
    os.makedirs(phase3_out, exist_ok=True)

    # Phase 1: analyze (metadata + maybe extraction)
    run_phase1(uploaded_dir, phase1_out)

    # Phase 2: cleanse - input commonly is either uploaded_dir or phase1_out/extract folder.
    # If your Phase1 extracts files into uploaded_dir or a specific folder, change this accordingly.
    # We'll pass uploaded_dir as input to Phase2 by default; adjust if your pipeline expects a different path.
    run_phase2(uploaded_dir, cleansing_out)

    # Phase 3: analysis on cleansed output
    csv_path, txt_path = run_phase3(cleansing_out, phase3_out)

    return csv_path, txt_path
