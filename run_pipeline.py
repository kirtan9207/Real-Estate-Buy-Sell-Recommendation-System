"""
Full Pipeline Runner
=====================
Executes the entire ML pipeline in order:
Data Generation → Cleaning → Feature Engineering → EDA →
Baseline → Training → Evaluation → Clustering → Recommendations → Report

Usage: python run_pipeline.py
"""

import sys
import os
import time

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)


def run_step(name, func, *args, **kwargs):
 """Run a pipeline step with timing."""
 print(f"\n{'='*60}")
 print(f" STEP: {name}")
 print(f"{'='*60}")
 start = time.time()
 try:
 result = func(*args, **kwargs)
 elapsed = time.time() - start
 print(f" {name} completed in {elapsed:.1f}s")
 return result
 except Exception as e:
 elapsed = time.time() - start
 print(f" {name} FAILED after {elapsed:.1f}s: {e}")
 import traceback
 traceback.print_exc()
 return None


def main():
 total_start = time.time()

 print(" BANGALORE REAL ESTATE INTELLIGENCE PIPELINE")
 print("=" * 60)

 # Step 1: Data Generation
 from data.generate_data import generate_production_data
 run_step("Data Generation (20,000 records)", generate_production_data)

 # Step 2: Data Cleaning
 from ml.scripts.cleaning_pipeline import run_cleaning_pipeline
 run_step("Data Cleaning Pipeline", run_cleaning_pipeline)

 # Step 3: Feature Engineering
 from ml.scripts.feature_engineering import engineer_features
 run_step("Feature Engineering", engineer_features)

 # Step 4: EDA Report
 from ml.scripts.generate_eda import generate_eda_report
 run_step("EDA Report Generation", generate_eda_report)

 # Step 5: Baseline Models
 from ml.scripts.baseline_model import run_baselines
 run_step("Baseline Model Evaluation", run_baselines)

 # Step 6: Model Training
 from ml.scripts.train_models import train_all_models
 run_step("Model Training (6 models)", train_all_models)

 # Step 7: Model Evaluation
 from ml.scripts.evaluate_models import evaluate_models
 run_step("Model Evaluation & Diagnostics", evaluate_models)

 # Step 8: Clustering
 from ml.scripts.clustering import run_clustering
 run_step("Market Clustering & Segmentation", run_clustering)

 # Step 9: Recommendation Engine
 from ml.scripts.recommendation_engine import run_recommendation_engine
 run_step("Recommendation Engine", run_recommendation_engine)

 # Step 10: Executive Report
 from ml.scripts.generate_report import generate_executive_report
 run_step("Executive Report Generation", generate_executive_report)

 total_elapsed = time.time() - total_start

 print(f"\n{'='*60}")
 print(f" PIPELINE COMPLETE — {total_elapsed:.1f}s total")
 print(f"{'='*60}")
 print(f"\n Output files:")
 print(f" Data: data/raw/bangalore_properties.csv")
 print(f" Cleaned: data/processed/cleaned_properties.csv")
 print(f" Features: data/processed/feature_engineered.csv")
 print(f" Final: data/processed/production_final.csv")
 print(f" Models: ml/models/*.pkl")
 print(f" Reports: ml/reports/")
 print(f" Executive: ml/reports/executive_report.html")
 print(f"\n Launch dashboard:")
 print(f" streamlit run dashboard/app.py")


if __name__ == '__main__':
 main()
