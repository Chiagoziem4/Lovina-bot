from __future__ import annotations
import csv,difflib,io,ipaddress,json,re,time,xml.etree.ElementTree as ET
from datetime import datetime,timezone

def regex_test(pattern,text):
    try:
        c=re.compile(pattern); matches=c.findall(text); spans=[(m.start(),m.end()) for m in c.finditer(text)]
        return {"pattern":pattern,"match_count":len(matches),"matches":[str(m) for m in matches[:20]],"spans":spans[:20],"valid_pattern":True}
    except re.error as e: return f"Invalid regex: {e}"

def text_stats(text):
    words=text.split(); sentences=[s.strip() for s in re.split(r"[.!?]+",text) if s.strip()]
    return {"characters":len(text),"characters_no_spaces":len(text.replace(" ","")),"words":len(words),"sentences":len(sentences),"paragraphs":len([p for p in text.split("\n\n") if p.strip()]),"unique_words":len(set(w.lower() for w in words)),"avg_word_length":round(sum(len(w) for w in words)/len(words),1) if words else 0}

def diff_texts(t1,t2):
    diff=list(difflib.unified_diff(t1.splitlines(keepends=True),t2.splitlines(keepends=True),fromfile="Text A",tofile="Text B",lineterm=""))
    ratio=difflib.SequenceMatcher(None,t1,t2).ratio()
    added=sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
    removed=sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
    return {"similarity":f"{round(ratio*100,1)}%","lines_added":added,"lines_removed":removed,"identical":ratio==1.0,"diff":"\n".join(diff[:60])}

def format_json(raw):
    try:
        parsed=json.loads(raw); pretty=json.dumps(parsed,indent=2,ensure_ascii=False)
        return {"valid":True,"type":type(parsed).__name__,"keys":list(parsed.keys()) if isinstance(parsed,dict) else None,"length":len(parsed) if isinstance(parsed,(dict,list)) else None,"formatted":pretty[:2000]}
    except json.JSONDecodeError as e: return f"Invalid JSON: {e}"

def json_to_csv(raw):
    try:
        data=json.loads(raw)
        if isinstance(data,dict): data=[data]
        if not isinstance(data,list): return "JSON must be array or object"
        keys=list(data[0].keys()); buf=io.StringIO(); w=csv.DictWriter(buf,fieldnames=keys,extrasaction="ignore")
        w.writeheader(); w.writerows(data)
        return {"rows":len(data),"columns":keys,"csv":buf.getvalue()[:2000]}
    except Exception as e: return f"JSON to CSV failed: {e}"

def csv_to_json(raw):
    try:
        reader=csv.DictReader(io.StringIO(raw)); rows=list(reader)
        return {"rows":len(rows),"columns":list(rows[0].keys()) if rows else [],"json":json.dumps(rows[:20],indent=2)[:2000]}
    except Exception as e: return f"CSV to JSON failed: {e}"

def parse_xml(raw):
    try:
        root=ET.fromstring(raw)
        def e2d(el):
            r={"tag":el.tag,"attributes":el.attrib,"text":(el.text or "").strip()}
            children=[e2d(c) for c in el]
            if children: r["children"]=children
            return r
        return {"root_tag":root.tag,"attributes":root.attrib,"tree":e2d(root)}
    except ET.ParseError as e: return f"Invalid XML: {e}"

def convert_timestamp(value):
    try:
        ts=float(value)
        if ts>1e12: ts/=1000
        dt=datetime.fromtimestamp(ts,tz=timezone.utc)
        return {"unix_timestamp":int(ts),"unix_ms":int(ts*1000),"utc":dt.strftime("%Y-%m-%d %H:%M:%S UTC"),"iso8601":dt.isoformat(),"date_only":dt.strftime("%Y-%m-%d")}
    except Exception as e: return f"Timestamp conversion failed: {e}"

def current_epoch():
    now=time.time(); dt=datetime.now(timezone.utc)
    return {"unix_seconds":int(now),"unix_milliseconds":int(now*1000),"utc":dt.strftime("%Y-%m-%d %H:%M:%S UTC"),"iso8601":dt.isoformat()}

def ip_calculator(cidr):
    try:
        network=ipaddress.ip_network(cidr,strict=False); hosts=list(network.hosts())
        return {"network":str(network),"network_address":str(network.network_address),"broadcast":str(network.broadcast_address) if network.version==4 else "N/A","netmask":str(network.netmask) if network.version==4 else str(network.prefixlen),"prefix_length":network.prefixlen,"total_hosts":network.num_addresses,"usable_hosts":len(hosts),"first_host":str(hosts[0]) if hosts else "N/A","last_host":str(hosts[-1]) if hosts else "N/A","version":f"IPv{network.version}","private":network.is_private}
    except Exception as e: return f"IP calculator failed: {e}"

def expand_cidr(cidr,limit=50):
    try:
        network=ipaddress.ip_network(cidr,strict=False); hosts=[str(h) for h in network.hosts()]
        return {"cidr":cidr,"total":len(hosts),"showing":min(limit,len(hosts)),"hosts":hosts[:limit],"truncated":len(hosts)>limit}
    except Exception as e: return f"CIDR expansion failed: {e}"

def extract_ips_from_text(text):
    ipv4=list(set(re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b",text)))
    valid=[ip for ip in ipv4 if all(0<=int(o)<=255 for o in ip.split("."))]
    return {"ipv4_count":len(valid),"ipv4":valid[:30]}

def mac_lookup(mac):
    OUI={"00:50:56":"VMware","00:0C:29":"VMware","08:00:27":"VirtualBox","52:54:00":"QEMU/KVM","00:1A:2B":"Cisco","3C:5A:B4":"Google","B8:27:EB":"Raspberry Pi","DC:A6:32":"Raspberry Pi","00:17:F2":"Apple","A4:C3:F0":"Apple","00:15:5D":"Microsoft","FC:15:B4":"Samsung","78:31:C1":"Intel"}
    try:
        clean=mac.upper().replace("-",":").replace(".",":")
        if len(clean.replace(":",""))==12 and ":" not in clean: clean=":".join(clean[i:i+2] for i in range(0,12,2))
        prefix=":".join(clean.split(":")[:3]); vendor=OUI.get(prefix,"Unknown vendor")
        is_local=int(clean.split(":")[0],16)&0x02!=0
        return {"mac":clean,"oui_prefix":prefix,"vendor":vendor,"locally_administered":is_local,"note":"Randomised/locally administered MAC" if is_local else None}
    except Exception as e: return f"MAC lookup failed: {e}"
