import os,json,tempfile
from fastapi.testclient import TestClient
import agent
from app import app
def main():
    with tempfile.TemporaryDirectory() as d, TestClient(app) as c:
        os.environ["WK17_DB"]=d+"/test.db"
        def run(q): return [json.loads(l) for l in c.get("/ask",params={"q":q}).text.splitlines()]
        def decide(k,v): return c.post("/approve",json={"id":k,"decision":v})
        a=run(agent.MULTI)
        assert [e["type"] for e in a]==["planning","tool_call","tool_result","reflection","approval_request"]
        b=run(agent.SIMPLE)
        assert all(e["type"]!="planning" for e in b) and "20 days" in b[-1]["text"]
        k=a[-1]["id"]
        assert c.get("/pending").json()[0]["id"]==k and not agent.records("outbox")
        assert decide(k,"approve").is_success and decide(k,"approve").status_code==409 and len(agent.records("outbox"))==1
        k2=run(agent.MULTI)[-1]["id"]
        assert decide(k2,"reject").is_success and len(agent.records("outbox"))==1 and not agent.records("pending")
        audit=c.get("/audit").json()
        assert [x["decision"] for x in audit]==["reject","approve"] and all(x["ts"] and x["user"] and x["tool"]=="send_email" and json.loads(x["args"])==a[-1]["args"] for x in audit)
        print("6/6 PASS")
if __name__=="__main__": main()
