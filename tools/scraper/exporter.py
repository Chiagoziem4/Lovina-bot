from __future__ import annotations
import csv,io,json
def to_json_bytes(items): return json.dumps(items,indent=2,ensure_ascii=False).encode("utf-8")
def to_jsonl_bytes(items): return "\n".join(json.dumps(i,ensure_ascii=False) for i in items).encode("utf-8")
def to_csv_bytes(items):
    if not items: return b""
    fields=sorted({k for i in items for k in i.keys()}); buf=io.StringIO()
    w=csv.DictWriter(buf,fieldnames=fields,extrasaction="ignore"); w.writeheader()
    for item in items: w.writerow({k:(json.dumps(v) if isinstance(v,(list,dict)) else v) for k,v in item.items()})
    return buf.getvalue().encode("utf-8")
def export_items(items,format="json"):
    if format=="json": return to_json_bytes(items),"results.json"
    elif format=="jsonl": return to_jsonl_bytes(items),"results.jsonl"
    elif format=="csv": return to_csv_bytes(items),"results.csv"
    raise ValueError(f"Unsupported: {format}")
