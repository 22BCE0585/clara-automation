import subprocess
from scripts.logger import log_event

def run_stage(command, stage_name):
    try:
        log_event(stage_name, "Stage started")
        subprocess.run(command, check=True)
        log_event(stage_name, "Stage completed successfully")
    except subprocess.CalledProcessError as e:
        log_event(stage_name, f"Stage failed: {str(e)}", level="ERROR")

if __name__ == "__main__":
    run_stage(["venv\\Scripts\\python", "-m", "scripts.extract_demo"], "DEMO_V1")
    run_stage(["venv\\Scripts\\python", "-m", "scripts.patch_version"], "ONBOARDING_V2")
    run_stage(["venv\\Scripts\\python", "-m", "scripts.generate_report"], "REPORT")