from __future__ import annotations
import asyncio,random,socket,sys

async def ping_host(host,count=4):
    try:
        flag="-n" if sys.platform=="win32" else "-c"
        proc=await asyncio.create_subprocess_exec("ping",flag,str(count),"-W","2",host,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
        stdout,_=await asyncio.wait_for(proc.communicate(),timeout=20)
        output=stdout.decode(errors="replace")
        lines=[l for l in output.splitlines() if l.strip()]
        return {"host":host,"alive":proc.returncode==0,"output":output[:800],"summary":lines[-1] if lines else ""}
    except asyncio.TimeoutError: return f"Ping timed out for {host}"
    except Exception as e: return f"Ping failed: {e}"

async def traceroute_host(host):
    try:
        cmd=["tracert","-d",host] if sys.platform=="win32" else ["traceroute","-n","-m","20",host]
        proc=await asyncio.create_subprocess_exec(*cmd,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
        stdout,_=await asyncio.wait_for(proc.communicate(),timeout=60)
        output=stdout.decode(errors="replace")
        hops=[l.strip() for l in output.splitlines() if l.strip() and (l.strip()[0].isdigit() or l.strip().startswith(" "))]
        return {"host":host,"hops":len(hops),"output":output[:1500]}
    except asyncio.TimeoutError: return f"Traceroute timed out for {host}"
    except Exception as e: return f"Traceroute failed: {e}"

async def banner_grab(host,port,timeout=5.0):
    try:
        reader,writer=await asyncio.wait_for(asyncio.open_connection(host,port),timeout=timeout)
        try: banner=await asyncio.wait_for(reader.read(1024),timeout=timeout); text=banner.decode(errors="replace").strip()
        except asyncio.TimeoutError: text="(no banner)"
        finally: writer.close(); await writer.wait_closed()
        return {"host":host,"port":port,"banner":text[:500],"length":len(text)}
    except Exception as e: return f"Banner grab failed: {e}"

async def reverse_dns(ip):
    try:
        loop=asyncio.get_event_loop()
        hostname,aliases,_=await loop.run_in_executor(None,socket.gethostbyaddr,ip)
        return {"ip":ip,"hostname":hostname,"aliases":aliases}
    except socket.herror: return {"ip":ip,"hostname":None,"aliases":[],"note":"No PTR record"}
    except Exception as e: return f"Reverse DNS failed: {e}"

async def asn_lookup(ip):
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as c:
            r=await c.get(f"https://ipinfo.io/{ip}/json"); d=r.json()
        return {"ip":ip,"org":d.get("org","N/A"),"asn":(d.get("org","") or "").split()[0] or "N/A","country":d.get("country","N/A"),"region":d.get("region","N/A"),"city":d.get("city","N/A"),"hostname":d.get("hostname","N/A")}
    except Exception as e: return f"ASN lookup failed: {e}"

async def dns_zone_transfer(domain):
    try:
        import dns.resolver,dns.zone,dns.query
        loop=asyncio.get_event_loop()
        def _try():
            results=[]
            for ns in dns.resolver.resolve(domain,"NS"):
                ns_str=str(ns).rstrip(".")
                try:
                    ns_ip=socket.gethostbyname(ns_str)
                    zone=dns.zone.from_xfr(dns.query.xfr(ns_ip,domain,timeout=5))
                    for name,node in zone.nodes.items(): results.append(f"{name}.{domain}")
                    return {"domain":domain,"nameserver":ns_str,"records":results,"vulnerable":True}
                except Exception: continue
            return {"domain":domain,"vulnerable":False,"note":"All nameservers refused"}
        return await loop.run_in_executor(None,_try)
    except Exception as e: return f"Zone transfer failed: {e}"

async def dns_brute(domain,wordlist=None):
    if wordlist is None: wordlist=["www","mail","ftp","remote","blog","webmail","server","ns1","ns2","smtp","secure","vpn","m","shop","portal","api","dev","staging","admin","test","dashboard","app","cdn","static","assets","media"]
    import dns.resolver; found=[]
    async def check(sub):
        try:
            loop=asyncio.get_event_loop()
            answers=await loop.run_in_executor(None,lambda:dns.resolver.resolve(f"{sub}.{domain}","A"))
            found.append({"subdomain":f"{sub}.{domain}","ips":[str(r) for r in answers]})
        except Exception: pass
    await asyncio.gather(*[check(w) for w in wordlist])
    return {"domain":domain,"checked":len(wordlist),"found":len(found),"results":sorted(found,key=lambda x:x["subdomain"])}

async def http_methods(url):
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0,verify=False) as c: r=await c.options(url)
        allow=r.headers.get("Allow",r.headers.get("allow","Not disclosed"))
        dangerous=[m for m in ["PUT","DELETE","TRACE","CONNECT","PATCH"] if m in allow.upper()]
        return {"url":url,"status":r.status_code,"allow_header":allow,"dangerous_methods":dangerous,"risk":"HIGH" if dangerous else "LOW"}
    except Exception as e: return f"HTTP methods check failed: {e}"

async def open_redirect_check(url):
    try:
        import httpx; payloads=["https://evil.com","//evil.com","/\\evil.com"]; findings=[]
        async with httpx.AsyncClient(timeout=10.0,follow_redirects=False,verify=False) as c:
            for p in payloads:
                r=await c.get(f"{url}?url={p}&next={p}&redirect={p}")
                loc=r.headers.get("location","")
                if "evil.com" in loc: findings.append({"payload":p,"location":loc})
        return {"url":url,"vulnerable":len(findings)>0,"findings":findings}
    except Exception as e: return f"Open redirect check failed: {e}"
