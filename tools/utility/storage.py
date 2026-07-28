from __future__ import annotations
import json,os,tempfile
from datetime import datetime,timezone
from pathlib import Path

DATA_DIR=Path(os.getenv("SPIDER_DATA_DIR","data/spider"))

def _user_file(user_id,name):
    p=DATA_DIR/"users"/str(user_id); p.mkdir(parents=True,exist_ok=True); return p/name

def _atomic_write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile("w",dir=path.parent,suffix=".tmp",delete=False,encoding="utf-8") as f:
        json.dump(data,f,indent=2); tmp=f.name
    os.replace(tmp,path)

def _load(path):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception: return {}

def _now(): return datetime.now(timezone.utc).isoformat()

def kv_set(user_id,key,value): path=_user_file(user_id,"kv_store.json"); store=_load(path); store[key]={"value":value,"updated":_now()}; _atomic_write(path,store); return {"key":key,"value":value,"status":"saved"}
def kv_get(user_id,key): path=_user_file(user_id,"kv_store.json"); store=_load(path); return f"Key '{key}' not found" if key not in store else {"key":key,"value":store[key]["value"],"updated":store[key]["updated"]}
def kv_delete(user_id,key): path=_user_file(user_id,"kv_store.json"); store=_load(path); return f"Key '{key}' not found" if key not in store else (store.pop(key),_atomic_write(path,store),{"key":key,"status":"deleted"})[2]
def kv_list(user_id): path=_user_file(user_id,"kv_store.json"); store=_load(path); return {"count":len(store),"keys":[{"key":k,"preview":str(v["value"])[:40],"updated":v["updated"]} for k,v in store.items()]}

def _get_fernet(user_id):
    try:
        from cryptography.fernet import Fernet; import hashlib,base64
        key=base64.urlsafe_b64encode(hashlib.sha256(f"lovina_note_{user_id}_2024".encode()).digest()); return Fernet(key)
    except ImportError: return None

def note_save(user_id,note_id,content):
    path=_user_file(user_id,"notes.json"); notes=_load(path); f=_get_fernet(user_id)
    stored=f.encrypt(content.encode()).decode() if f else content
    notes[note_id]={"content":stored,"encrypted":f is not None,"created":_now(),"length":len(content)}; _atomic_write(path,notes)
    return {"note_id":note_id,"encrypted":f is not None,"length":len(content),"status":"saved"}

def note_get(user_id,note_id):
    path=_user_file(user_id,"notes.json"); notes=_load(path)
    if note_id not in notes: return f"Note '{note_id}' not found"
    entry=notes[note_id]; content=entry["content"]
    if entry.get("encrypted"):
        f=_get_fernet(user_id)
        if f:
            try: content=f.decrypt(content.encode()).decode()
            except Exception: content="[Decryption failed]"
    return {"note_id":note_id,"content":content,"created":entry["created"]}

def note_list(user_id): path=_user_file(user_id,"notes.json"); notes=_load(path); return {"count":len(notes),"notes":[{"id":k,"encrypted":v.get("encrypted",False),"length":v.get("length",0),"created":v.get("created","")} for k,v in notes.items()]}
def note_delete(user_id,note_id): path=_user_file(user_id,"notes.json"); notes=_load(path); return f"Note '{note_id}' not found" if note_id not in notes else (notes.pop(note_id),_atomic_write(path,notes),{"note_id":note_id,"status":"deleted"})[2]

def timeline_add(user_id,event,tag=None):
    path=_user_file(user_id,"timeline.json"); tl=_load(path); events=tl.get("events",[])
    entry={"id":len(events)+1,"timestamp":_now(),"event":event,"tag":tag or "general"}
    events.append(entry); _atomic_write(path,{"events":events}); return {"status":"added","entry":entry}

def timeline_view(user_id,limit=20):
    path=_user_file(user_id,"timeline.json"); tl=_load(path); events=tl.get("events",[])
    return {"total":len(events),"showing":min(limit,len(events)),"events":events[-limit:][::-1]}

def timeline_clear(user_id): path=_user_file(user_id,"timeline.json"); _atomic_write(path,{"events":[]}); return {"status":"cleared"}

def history_add(user_id,command):
    path=_user_file(user_id,"history.json"); hist=_load(path); entries=hist.get("commands",[])
    entries.append({"command":command,"timestamp":_now()})
    if len(entries)>200: entries=entries[-200:]
    _atomic_write(path,{"commands":entries})

def history_view(user_id,limit=20):
    path=_user_file(user_id,"history.json"); hist=_load(path); commands=hist.get("commands",[])
    return {"total":len(commands),"recent":commands[-limit:][::-1]}

def scope_add(user_id,target):
    path=_user_file(user_id,"scope.json"); scope=_load(path); targets=scope.get("targets",[])
    if target in targets: return {"target":target,"status":"already in scope"}
    targets.append(target); _atomic_write(path,{"targets":targets,"updated":_now()}); return {"target":target,"status":"added","total_targets":len(targets)}

def scope_remove(user_id,target):
    path=_user_file(user_id,"scope.json"); scope=_load(path); targets=scope.get("targets",[])
    if target not in targets: return f"'{target}' not in scope"
    targets.remove(target); _atomic_write(path,{"targets":targets,"updated":_now()}); return {"target":target,"status":"removed"}

def scope_list(user_id): path=_user_file(user_id,"scope.json"); scope=_load(path); return {"targets":scope.get("targets",[]),"count":len(scope.get("targets",[]))}
def scope_check(user_id,target):
    from urllib.parse import urlparse; path=_user_file(user_id,"scope.json"); scope=_load(path); targets=scope.get("targets",[])
    parsed=urlparse(target if "://" in target else f"http://{target}"); domain=parsed.netloc or parsed.path
    in_scope=any(t in domain or domain in t or t==target for t in targets)
    return {"target":target,"in_scope":in_scope,"scope_list":targets}

def alias_set(user_id,name,command): path=_user_file(user_id,"aliases.json"); aliases=_load(path); aliases[name]={"command":command,"created":_now()}; _atomic_write(path,aliases); return {"alias":name,"command":command,"status":"saved"}
def alias_get(user_id,name): path=_user_file(user_id,"aliases.json"); aliases=_load(path); return f"Alias '{name}' not found" if name not in aliases else {"alias":name,"command":aliases[name]["command"]}
def alias_list(user_id): path=_user_file(user_id,"aliases.json"); aliases=_load(path); return {"count":len(aliases),"aliases":[{"name":k,"command":v["command"]} for k,v in aliases.items()]}
def alias_delete(user_id,name): path=_user_file(user_id,"aliases.json"); aliases=_load(path); return f"Alias '{name}' not found" if name not in aliases else (aliases.pop(name),_atomic_write(path,aliases),{"alias":name,"status":"deleted"})[2]
