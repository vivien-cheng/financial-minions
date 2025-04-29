from typing import Dict, Any
import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class PipelineEvaluator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.expected_data = self._load_expected_data()
    
    def _load_expected_data(self) -> Dict[str, Dict[str, Any]]:
        """Load expected answers and justifications from raw_data.json"""
        with open("src/examples/raw_data.json", "r") as f:
            data = json.load(f)
            return {
                "amcor": {
                    "answer": data[0]["answer"],
                    "justification": data[0]["justification"]
                },
                "aes": {
                    "answer": data[1]["answer"],
                    "justification": data[1]["justification"]
                },
                "3m": {
                    "answer": data[2]["answer"],
                    "justification": data[2]["justification"]
                }
            }
    
    async def evaluate(self, company: str, pipeline_output: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate pipeline output against expected answer using LLM"""
        expected = self.expected_data[company.lower()]
        
        # Extract the final answer from the pipeline output
        pipeline_answer = pipeline_output["final_answer"]
        pipeline_justification = "\n".join([
            f"Step {i+1} ({step['agent']}): {step['output'].explanation}"
            for i, step in enumerate(pipeline_output["steps"])
        ])
        
        prompt = f"""
        You are a financial analysis evaluator. Compare the following two analyses:

        EXPECTED ANALYSIS:
        Answer: {expected['answer']}
        Justification: {expected['justification']}

        PIPELINE ANALYSIS:
        Answer: {pipeline_answer}
        Justification: {pipeline_justification}

        Evaluate if:
        1. The final answer is equivalent (they may use different wording but convey the same meaning)
        2. The justification is similar (they may use different calculations but arrive at the same conclusion)

        Return your evaluation as a JSON object with these fields:
        - answer_match: boolean (true if answers are equivalent)
        - justification_match: boolean (true if justifications are similar)
        - explanation: string (brief explanation of your evaluation)
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content) 