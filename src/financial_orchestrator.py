from typing import List, Dict, Any, Optional  
from src.models import JobManifest, JobOutput, Job  
from src.agent import Agent  
from src.tools.registry import ToolRegistry  
import json  
import asyncio  
  
class FinancialOrchestrator:  
    def __init__(  
        self,   
        supervisor_model,  # Large model like Claude Haiku or GPT-4o  
        agents: Dict[str, Agent],  
        tool_registry: ToolRegistry,  
        max_rounds: int = 3  
    ):  
        self.supervisor_model = supervisor_model  
        self.agents = agents  
        self.tool_registry = tool_registry  
        self.max_rounds = max_rounds  
          
    async def run_financial_analysis(self, task: str, context: str, workflow: List[Dict[str, str]]) -> Dict[str, Any]:  
        """Run a financial analysis using the predefined workflow"""  
        results = {}  
        intermediate_outputs = []  
          
        print(f"Starting financial analysis for task: {task}")  
        print(f"Using {len(workflow)} workflow steps")  
          
        for step_idx, step in enumerate(workflow):  
            agent_name = step["agent"]  
            task_description = step["task"]  
              
            # Format the task with previous results if needed  
            formatted_task = task_description  
            if "{" in task_description:  
                try:  
                    formatted_task = task_description.format(**results)  
                except KeyError as e:  
                    print(f"Warning: Could not format task with results. Missing key: {e}")  
              
            print(f"\nStep {step_idx + 1}: Running {agent_name}")  
            print(f"Task: {formatted_task}")  
              
            # Execute the agent  
            agent = self.agents[agent_name]  
            output = await agent.execute(formatted_task, context)  
              
            # Store the result  
            step_key = step.get("output_key", agent_name)  
            results[step_key] = output.answer  
              
            # Store intermediate output for final synthesis  
            intermediate_outputs.append({  
                "agent": agent_name,  
                "task": formatted_task,  
                "output": output  
            })  
              
            # Update context with the result if specified  
            if step.get("update_context", False):  
                context_update = f"\n\nPrevious analysis result:\n{agent_name}: {output.answer}\n"  
                context += context_update  
                  
            print(f"Output: {output.answer}")  
          
        # Final synthesis  
        final_answer = await self.synthesize_results(task, intermediate_outputs)  
          
        return {  
            "task": task,  
            "steps": intermediate_outputs,  
            "final_answer": final_answer  
        }  
      
    async def synthesize_results(self, task: str, intermediate_outputs: List[Dict[str, Any]]) -> str:  
        """Synthesize the results from all agents into a final answer"""  
        # Format intermediate outputs for the supervisor  
        outputs_text = ""  
        for idx, output in enumerate(intermediate_outputs):  
            outputs_text += f"Step {idx + 1}: {output['agent']}\n"  
            outputs_text += f"Task: {output['task']}\n"  
            outputs_text += f"Explanation: {output['output'].explanation}\n"  
            if output['output'].citation:  
                outputs_text += f"Citation: {output['output'].citation}\n"  
            outputs_text += f"Answer: {output['output'].answer}\n\n"  
          
        prompt = f"""  
        Task: {task}  
          
        The following analyses were performed by specialized agents:  
          
        {outputs_text}  
          
        Synthesize these results to provide a comprehensive answer to the original task.  
        Your answer should be clear, concise, and based solely on the information provided.  
        """  
          
        print("\nSynthesizing final answer...")  
        messages = [{"role": "user", "content": prompt}]  
        response = await self.supervisor_model.generate(messages)  
          
        print(f"Final answer: {response}")  
        return response