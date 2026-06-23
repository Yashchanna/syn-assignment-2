import os
import json
import yaml
from openai import OpenAI
import time

class LLMJudgePipeline:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", os.getenv("OPENAI_API_KEY"))
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.model = model or os.getenv("LLM_MODEL", "gemini-2.5-flash")
        self.token_usage = {"prompt_tokens": 0, "completion_tokens": 0}
        
    def load_rubric(self, rubric_path):
        with open(rubric_path, 'r') as f:
            return yaml.safe_load(f)

    def build_prompt(self, test_case, rubric, order_ab=True):
        ans1 = test_case['model_a_output'] if order_ab else test_case['model_b_output']
        ans2 = test_case['model_b_output'] if order_ab else test_case['model_a_output']
        model1_label = "Model A" if order_ab else "Model B"
        model2_label = "Model B" if order_ab else "Model A"
        
        system_prompt = (
            "You are an expert LLM judge. Evaluate the two models based on the criteria.\n"
            f"Rubric: {json.dumps(rubric)}\n"
            "Output valid JSON ONLY with the following schema: "
            "{\"criteria_scores\": {\"Model A\": {\"correctness\": int, ...}, \"Model B\": {...}}, \"rationale\": \"string\", \"winner\": \"Model A\" | \"Model B\" | \"Tie\"}"
        )
        
        user_prompt = (
            f"Input: {test_case['input']}\n"
            f"Output 1 ({model1_label}): {ans1}\n"
            f"Output 2 ({model2_label}): {ans2}\n"
        )
        return system_prompt, user_prompt
        
    def judge_pair(self, test_case, rubric, order_ab=True):
        system_prompt, user_prompt = self.build_prompt(test_case, rubric, order_ab)
        start = time.time()
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        latency = time.time() - start
        self.token_usage["prompt_tokens"] += response.usage.prompt_tokens
        self.token_usage["completion_tokens"] += response.usage.completion_tokens
        
        try:
            verdict = json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            verdict = {"error": "Malformed JSON"}
            
        return {
            "verdict": verdict,
            "latency": latency,
            "raw_prompt": user_prompt,
            "raw_response": response.choices[0].message.content
        }

    def run_suite(self, suite_path, rubric_path):
        with open(suite_path, 'r') as f:
            suite = json.load(f)
            
        rubric = self.load_rubric(rubric_path)
        results = []
        
        for case in suite:
            # Run A/B order
            res_ab = self.judge_pair(case, rubric, order_ab=True)
            # Run B/A order (Position bias mitigation)
            res_ba = self.judge_pair(case, rubric, order_ab=False)
            
            # Require agreement or average
            winner_ab = res_ab['verdict'].get('winner')
            winner_ba = res_ba['verdict'].get('winner')
            
            agreed = winner_ab == winner_ba
            final_winner = winner_ab if agreed else "Tie"
            
            results.append({
                "case_id": case.get("id"),
                "agreed": agreed,
                "winner_ab": winner_ab,
                "winner_ba": winner_ba,
                "final_winner": final_winner
            })
            
            # Log full response
            log_path = os.path.join(os.path.dirname(__file__), f"log_{case.get('id')}.json")
            with open(log_path, "w") as f_log:
                json.dump({"ab": res_ab, "ba": res_ba}, f_log, indent=2)
                
        # Aggregate
        model_a_wins = sum(1 for r in results if r["final_winner"] == "Model A")
        model_b_wins = sum(1 for r in results if r["final_winner"] == "Model B")
        ties = sum(1 for r in results if r["final_winner"] == "Tie")
        
        report = {
            "total_cases": len(suite),
            "model_a_win_rate": model_a_wins / len(suite),
            "model_b_win_rate": model_b_wins / len(suite),
            "tie_rate": ties / len(suite),
            "position_bias_flip_rate": sum(1 for r in results if not r["agreed"]) / len(suite),
            "tokens": self.token_usage
        }
        
        report_path = os.path.join(os.path.dirname(__file__), 'suite_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=4)
            
        return report

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))
    pipeline = LLMJudgePipeline()
    report = pipeline.run_suite(
        os.path.join(os.path.dirname(__file__), '../tests/suite.json'),
        os.path.join(os.path.dirname(__file__), 'rubric.yaml')
    )
    print("Report:", report)
