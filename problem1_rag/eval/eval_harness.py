import json
import time
import requests
import os

def evaluate():
    print("Starting evaluation...")
    questions_file = os.path.join(os.path.dirname(__file__), 'questions.json')
    if not os.path.exists(questions_file):
        print(f"Dataset not found at {questions_file}")
        return
        
    with open(questions_file, 'r') as f:
        dataset = json.load(f)
    
    results = []
    total_latency = 0
    hit_rate_count = 0
    
    for item in dataset:
        start = time.time()
        # Call the local API
        try:
            res = requests.post("http://127.0.0.1:8000/query", json={"query": item["question"], "k": 5})
            if res.status_code != 200:
                print(f"API Error: {res.text}")
                continue
                
            data = res.json()
            latency = (time.time() - start) * 1000
            total_latency += latency
            
            # Simple retrieval metric: Hit Rate (if the expected source is in retrieved sources)
            sources = [c.get('source', '') for c in data.get('citations', [])]
            hit = 1 if item["relevant_document_source"] in sources else 0
            hit_rate_count += hit
            
            # For brevity, LLM-as-a-judge for faithfulness/relevance is mock implemented
            # In production, we'd prompt GPT-4 to score the data["answer"] against context
            
            results.append({
                "question": item["question"],
                "latency_ms": latency,
                "hit": hit,
                "answer": data.get("answer")
            })
            
        except Exception as e:
            print(f"Error querying for {item['question']}: {e}")
            
    avg_latency = total_latency / len(dataset) if dataset else 0
    hit_rate = hit_rate_count / len(dataset) if dataset else 0
    
    report = {
        "metrics": {
            "average_latency_ms": avg_latency,
            "hit_rate": hit_rate
        },
        "details": results
    }
    
    results_file = os.path.join(os.path.dirname(__file__), 'results.json')
    with open(results_file, 'w') as f:
        json.dump(report, f, indent=4)
        
    print(f"Evaluation complete. Hit Rate: {hit_rate}, Avg Latency: {avg_latency:.2f}ms")
    print(f"Results saved to {results_file}")

if __name__ == "__main__":
    evaluate()
