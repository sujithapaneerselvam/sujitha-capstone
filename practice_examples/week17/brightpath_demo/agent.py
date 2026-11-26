import json, sqlite3, uuid, os
from contextlib import contextmanager
from tools import lookup_policy,send_email
from pathlib import Path
@contextmanager
def connect():
    path=Path(os.getenv("WK17_DB","data/capstone_side.db"))
    path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path)
    db.row_factory=sqlite3.Row
    try:
        db.executescript("""create table if not exists pending(id text primary key,args text);
        create table if not exists outbox(id text primary key,args text);
        create table if not exists approval_log(id text primary key,ts text default current_timestamp,user text,tool text,args text,decision text);""")
        with db: yield db
    finally: db.close()
def records(table):
    if table not in ("pending","outbox","approval_log"): raise ValueError(table)
    with connect() as db: return [dict(r) for r in db.execute("select * from "+table+" order by rowid desc")]
SIMPLE="What is the annual leave entitlement?"
MULTI="Summarize the leave policy and email it to Alice."
def ask(q):
    if q not in (SIMPLE,MULTI):
        yield {"type":"final","text":"Select one of the two demo questions."}
        return
    if q==MULTI: yield {"type":"planning","steps":["Look up leave","Check evidence","Request email approval"]}
    yield {"type":"tool_call","tool":"lookup_policy"}
    body=lookup_policy()
    yield {"type":"tool_result","text":body}
    if q==SIMPLE:
        for word in body.split(): yield {"type":"token","text":word+" "}
        yield {"type":"final","text":body}
        return
    supported="Source:" in body
    yield {"type":"reflection","source_present":supported}
    if not supported:
        yield {"type":"final","text":"Missing evidence; no email drafted."}
        return
    key=uuid.uuid4().hex
    args={"to":"alice@example.com","body":body}
    with connect() as db: db.execute("insert into pending values (?,?)",(key,json.dumps(args)))
    yield {"type":"approval_request","id":key,"tool":"send_email","args":args}
def decide(key,choice):
    if choice not in ("approve","reject"): raise ValueError(choice)
    with connect() as db:
        db.execute("begin immediate")
        row=db.execute("select args from pending where id=?",(key,)).fetchone()
        if row is None: raise KeyError(key)
        if choice=="approve": send_email(db,key,row["args"])
        db.execute("insert into approval_log(id,user,tool,args,decision) values (?,?,?,?,?)",(key,"local-demo-reviewer","send_email",row["args"],choice))
        db.execute("delete from pending where id=?",(key,))
    events=[{"type":"tool_call","tool":"send_email"},{"type":"tool_result","simulated":True}] if choice=="approve" else []
    return events+[{"type":"final","text":"Approved: saved to simulated outbox." if events else "Rejected: no email sent."}]
