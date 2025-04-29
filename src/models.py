from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel

class JobManifest(BaseModel):
    """Task definition for a worker agent"""
    chunk: str  # the text/data for the agent to process
    task: str  # the instruction for the agent
    advice: str  # optional guidance on how to perform the task
    chunk_id: Optional[int] = None
    task_id: Optional[int] = None
    job_id: Optional[int] = None

class JobOutput(BaseModel):
    """Output from a worker agent"""
    explanation: str
    citation: Optional[str] = None
    answer: Optional[Union[str, Dict[str, Any]]] = None

class Job(BaseModel):
    """Complete job with manifest and output"""
    manifest: JobManifest
    output: JobOutput
    sample: str  # raw response from the model
    include: Optional[bool] = None  # flag for filtering 