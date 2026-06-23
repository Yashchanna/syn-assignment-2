import os
import json
import yaml
from judge.pipeline import LLMJudgePipeline

def test_retest_consistency():
    pipeline = LLMJudgePipeline()
    rubric_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/rubric.yaml')
    suite_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/suite.json')
    
    print("Running Suite Pass 1...")
    report1 = pipeline.run_suite(suite_path, rubric_path)
    
    print("Running Suite Pass 2...")
    report2 = pipeline.run_suite(suite_path, rubric_path)
    
    print("\n--- Validation Results ---")
    print(f"Run 1 Win Rates: Model A: {report1['model_a_win_rate']}, Model B: {report1['model_b_win_rate']}")
    print(f"Run 2 Win Rates: Model A: {report2['model_a_win_rate']}, Model B: {report2['model_b_win_rate']}")
    
    if report1['model_a_win_rate'] == report2['model_a_win_rate']:
        print("Consistency: Perfect match between runs.")
    else:
        print("Consistency: Verdicts flipped on identical inputs (Check temperature/model variability).")

if __name__ == "__main__":
    from dotenv import load_dotenv
    # Setup paths relative to script
    root_env = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(root_env)
    test_retest_consistency()
