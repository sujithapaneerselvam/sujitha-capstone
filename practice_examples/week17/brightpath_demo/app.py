import json
from typing import Literal
from fastapi import FastAPI,HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import agent
app=FastAPI()
def stream(events):
    return StreamingResponse((json.dumps(x)+"\n" for x in events),media_type="application/x-ndjson")
@app.get("/ask")
def ask(q:str): return stream(agent.ask(q))
class Decision(BaseModel):
    id:str
    decision:Literal["approve","reject"]
@app.post("/approve")
def approve(d:Decision):
    try: return stream(agent.decide(d.id,d.decision))
    except KeyError: raise HTTPException(409,"Unknown or already decided")
@app.get("/pending")
def pending(): return agent.records("pending")
@app.get("/audit")
def audit(): return agent.records("approval_log")
