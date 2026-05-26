"""
Master Pipeline Script
Runs the complete steel distribution analysis workflow
"""

import sys
from pathlib import Path
import subprocess
import time

# Set up paths
BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / 'scripts'
MODELS_DIR = BASE_DIR / 'models'
VIZ_DIR = BASE_DIR / 'viz'

def run_script(script_path: Path, description: str):
    """Run a Python script and handle errors"""
    print("\n" + "=" * 70)
    print(f"STEP: {description}")
    print("=" * 70)

    try:
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            capture_output=False
        )
        elapsed = time.time() - start_time
        print(f"\n✓ Completed in {elapsed:.2f} seconds")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error running {script_path.name}: {e}")
        return False

def main():
    """Execute the full analysis pipeline"""
    print("=" * 70)
    print("STEEL DISTRIBUTION ANALYSIS - FULL PIPELINE")
    print("=" * 70)
    print(f"Base directory: {BASE_DIR}")
    print()

    pipeline_start = time.time()

    # Define pipeline steps
    steps = [
        (SCRIPTS_DIR / '01_download_data.py', 'Data Acquisition'),
        (SCRIPTS_DIR / '02_clean_data.py', 'Data Cleaning & Transformation'),
        (SCRIPTS_DIR / '03_engineer_features.py', 'Feature Engineering'),
        (MODELS_DIR / 'clustering' / 'clustering_model.py', 'Clustering Analysis'),
        (MODELS_DIR / 'regression' / 'demand_prediction.py', 'Demand Prediction Models'),
        (MODELS_DIR / 'timeseries' / 'momentum_analysis.py', 'Momentum Analysis'),
        (VIZ_DIR / 'spatial_analysis.py', 'Spatial Analysis & Visualizations'),
    ]

    # Execute pipeline
    results = []
    for script_path, description in steps:
        if not script_path.exists():
            print(f"⚠ Warning: Script not found: {script_path}")
            results.append(False)
            continue

        success = run_script(script_path, description)
        results.append(success)

        if not success:
            print(f"\n⚠ Pipeline halted due to error in: {description}")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                break

    # Summary
    print("\n" + "=" * 70)
    print("PIPELINE SUMMARY")
    print("=" * 70)

    for (script_path, description), success in zip(steps, results):
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{status}: {description}")

    total_elapsed = time.time() - pipeline_start
    success_count = sum(results)
    total_count = len(steps)

    print("\n" + "=" * 70)
    print(f"Pipeline completed: {success_count}/{total_count} steps successful")
    print(f"Total time: {total_elapsed:.2f} seconds ({total_elapsed/60:.2f} minutes)")
    print("=" * 70)

    if success_count == total_count:
        print("\n🎉 All pipeline steps completed successfully!")
        print("\nNext steps:")
        print("1. Review visualizations in viz/ directory")
        print("2. Open analysis notebooks in analysis/ directory")
        print("3. Read executive summary in reports/ directory")
    else:
        print("\n⚠ Some pipeline steps failed. Please review errors above.")

if __name__ == "__main__":
    main()
