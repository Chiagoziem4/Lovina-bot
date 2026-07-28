from __future__ import annotations
import asyncio,re,xml.etree.ElementTree as ET
from urllib.parse import urlparse,urljoin

async def _fetch(url,method="GET",headers=None,follow=True,timeout=15.0):
    import httpx
    hdrs={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36","Accept":"text/html,application/xhtml+xml,*/*;q=0.8",**(headers or {})}
    async with httpx.AsyncClient(follow_redirects=follow,timeout=timeout,verify=False) as c:
        r=await (c.options(url,headers=hdrs) if method=="OPTIONS" else c.get(url,headers=hdrs))
    return r.status_code,dict(r.headers),r.text

async def analyse_security_headers(url):
    try:
        status,headers,_=await _fetch(url)
        checks={"Strict-Transport-Security":headers.get("strict-transport-security"),"Content-Security-Policy":headers.get("content-security-policy"),"X-Frame-Options":headers.get("x-frame-options"),"X-Content-Type-Options":headers.get("x-content-type-options"),"Referrer-Policy":headers.get("referrer-policy"),"Permissions-Policy":headers.get("permissions-policy"),"X-XSS-Protection":headers.get("x-xss-protection")}
        present={k:v for k,v in checks.items() if v}; missing=[k for k,v in checks.items() if not v]; score=len(present)
        grade="A" if score>=6 else "B" if score>=4 else "C" if score>=3 else "D" if score>=2 else "F"
        return {"url":url,"grade":grade,"score":f"{score}/{len(checks)}","present":present,"missing":missing,"server":headers.get("server","Not disclosed")}
    except Exception as e: return f"Header analysis failed: {e}"

async def check_cors(url):
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0,verify=False) as c:
            r=await c.get(url,headers={"Origin":"https://evil.com","User-Agent":"Mozilla/5.0"})
        acao=r.headers.get("access-control-allow-origin",""); acac=r.headers.get("access-control-allow-credentials","")
        vulnerable=acao in ("*","https://evil.com"); critical=vulnerable and acac.lower()=="true"
        return {"url":url,"access_control_allow_origin":acao or "Not set","access_control_allow_credentials":acac or "Not set","vulnerable":vulnerable,"critical":critical,"severity":"CRITICAL" if critical else "HIGH" if vulnerable else "LOW"}
    except Exception as e: return f"CORS check failed: {e}"

async def fetch_robots(url):
    try:
        parsed=urlparse(url); robots_url=f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        status,_,text=await _fetch(robots_url)
        if status!=200: return {"url":robots_url,"found":False}
        disallowed=[l.split(":",1)[1].strip() for l in text.splitlines() if l.lower().startswith("disallow:")]
        sitemaps=[l.split(":",1)[1].strip() for l in text.splitlines() if l.lower().startswith("sitemap:")]
        interesting=[p for p in disallowed if any(k in p.lower() for k in ["admin","api","backup","config","secret","private","internal","db","sql"])]
        return {"url":robots_url,"found":True,"disallowed_count":len(disallowed),"disallowed":disallowed[:20],"sitemaps":sitemaps,"interesting_paths":interesting,"raw":text[:1000]}
    except Exception as e: return f"Robots.txt failed: {e}"

async def parse_sitemap(url):
    try:
        parsed=urlparse(url)
        if not url.endswith(".xml"): url=f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
        status,_,text=await _fetch(url)
        if status!=200: return {"url":url,"found":False}
        root=ET.fromstring(text)
        urls=[loc.text for loc in root.findall(".//{*}loc") if loc.text]
        return {"url":url,"found":True,"total_urls":len(urls),"urls":urls[:50]}
    except Exception as e: return f"Sitemap parse failed: {e}"

async def detect_tech_stack(url):
    try:
        status,headers,html=await _fetch(url)
        tech={}
        if headers.get("server"): tech["Server"]=headers["server"]
        if headers.get("x-powered-by"): tech["Powered-By"]=headers["x-powered-by"]
        SIGS={"WordPress":["/wp-content/","/wp-includes/"],"Drupal":["Drupal.settings","/sites/default/files/"],"Joomla":["/components/com_","Joomla!"],"Shopify":["cdn.shopify.com","Shopify.theme"],"Wix":["wix.com","wixsite.com"],"Next.js":["__NEXT_DATA__","_next/static"],"React":["__reactFiber","react.development.js"],"Vue.js":["vue.min.js","__vue__"],"Angular":["ng-version=","angular.js"],"Bootstrap":["bootstrap.min.css"],"jQuery":["jquery.min.js"],"Cloudflare":["CF-Ray","cloudflare"],"Google Analytics":["google-analytics.com","gtag/js"],"PHP":[".php"],"WordPress Login":["/wp-login.php"]}
        for name,patterns in SIGS.items():
            if any(p.lower() in html.lower() or p.lower() in str(headers).lower() for p in patterns): tech[name]="Detected"
        return {"url":url,"status":status,"technologies":tech,"total_detected":len(tech)}
    except Exception as e: return f"Tech stack detection failed: {e}"

async def extract_page_meta(url):
    try:
        from bs4 import BeautifulSoup; _,_,html=await _fetch(url); soup=BeautifulSoup(html,"lxml")
        title=soup.find("title"); metas={}
        for tag in soup.find_all("meta"):
            name=tag.get("name") or tag.get("property") or tag.get("http-equiv"); content=tag.get("content")
            if name and content: metas[name]=content[:200]
        links_rel={(tag.get("rel",[""])[0]):tag.get("href","") for tag in soup.find_all("link") if tag.get("rel")}
        return {"url":url,"title":title.get_text(strip=True) if title else None,"meta":metas,"canonical":links_rel.get("canonical"),"favicon":links_rel.get("icon") or links_rel.get("shortcut icon")}
    except Exception as e: return f"Page meta extraction failed: {e}"

async def extract_links_from_page(url):
    try:
        from bs4 import BeautifulSoup; _,_,html=await _fetch(url); soup=BeautifulSoup(html,"lxml")
        parsed=urlparse(url); base=f"{parsed.scheme}://{parsed.netloc}"; internal=[]; external=[]
        for tag in soup.find_all(["a","link","script","img"]):
            href=tag.get("href") or tag.get("src","")
            if not href or href.startswith(("#","javascript:","mailto:")): continue
            if href.startswith("http"):
                (internal if parsed.netloc in href else external).append(href)
            elif href.startswith("/"): internal.append(base+href)
        return {"url":url,"internal_links":len(set(internal)),"external_links":len(set(external)),"internal":list(set(internal))[:30],"external":list(set(external))[:20]}
    except Exception as e: return f"Link extraction failed: {e}"

async def harvest_emails(url):
    try:
        _,_,html=await _fetch(url)
        emails=list(set(re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",html)))
        emails=[e for e in emails if not any(s in e.lower() for s in ["example.com","test@","noreply"])]
        return {"url":url,"count":len(emails),"emails":emails[:30]}
    except Exception as e: return f"Email harvesting failed: {e}"

async def analyse_cookies(url):
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0,verify=False) as c: r=await c.get(url,headers={"User-Agent":"Mozilla/5.0"})
        cookie_str=str(r.headers.get("set-cookie","")).lower(); cookies=[]
        for name,val in r.cookies.items():
            issues=[]
            if "secure" not in cookie_str: issues.append("Missing Secure flag")
            if "httponly" not in cookie_str: issues.append("Missing HttpOnly flag")
            if "samesite" not in cookie_str: issues.append("Missing SameSite flag")
            cookies.append({"name":name,"value":val[:30],"issues":issues})
        return {"url":url,"cookie_count":len(cookies),"cookies":cookies}
    except Exception as e: return f"Cookie analysis failed: {e}"

async def check_redirect_chain(url):
    try:
        import httpx; chain=[]; current=url
        async with httpx.AsyncClient(follow_redirects=False,timeout=10.0,verify=False) as c:
            for _ in range(10):
                r=await c.get(current,headers={"User-Agent":"Mozilla/5.0"}); chain.append({"url":current,"status":r.status_code})
                if r.status_code not in (301,302,303,307,308): break
                loc=r.headers.get("location","")
                if not loc: break
                current=loc if loc.startswith("http") else url[:url.find("/",8)]+loc
        return {"original_url":url,"hops":len(chain)-1,"final_url":chain[-1]["url"],"chain":chain}
    except Exception as e: return f"Redirect chain check failed: {e}"

async def wayback_lookup(url):
    try:
        import httpx; parsed=urlparse(url); domain=parsed.netloc
        api=f"https://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&limit=10&fl=timestamp,original,statuscode&filter=statuscode:200"
        async with httpx.AsyncClient(timeout=15.0) as c: r=await c.get(api); data=r.json()
        if not data or len(data)<2: return {"domain":domain,"snapshots":0,"note":"No snapshots found"}
        snaps=[]
        for row in data[1:]:
            ts=row[0]; snaps.append({"date":f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}","url":row[1],"archive":f"https://web.archive.org/web/{ts}/{row[1]}"})
        return {"domain":domain,"snapshots_found":len(snaps),"latest":snaps[0] if snaps else None,"history":snaps}
    except Exception as e: return f"Wayback lookup failed: {e}"

async def find_forms(url):
    try:
        from bs4 import BeautifulSoup; _,_,html=await _fetch(url); soup=BeautifulSoup(html,"lxml"); forms=[]
        for form in soup.find_all("form"):
            inputs=[{"name":inp.get("name",""),"type":inp.get("type","text")} for inp in form.find_all(["input","textarea","select"])]
            forms.append({"action":form.get("action",""),"method":form.get("method","GET").upper(),"inputs":inputs,"has_password":any(i["type"]=="password" for i in inputs)})
        return {"url":url,"form_count":len(forms),"forms":forms}
    except Exception as e: return f"Form finder failed: {e}"

async def extract_comments(url):
    try:
        _,_,html=await _fetch(url)
        comments=re.findall(r"<!--(.*?)-->",html,re.DOTALL)
        interesting=[c.strip() for c in comments if any(k in c.lower() for k in ["todo","fixme","password","key","secret","api","admin","debug","remove"])]
        return {"url":url,"total_comments":len(comments),"interesting_count":len(interesting),"all_comments":[c.strip()[:200] for c in comments[:15]],"interesting":interesting[:10]}
    except Exception as e: return f"Comment extraction failed: {e}"

async def list_js_files(url):
    try:
        from bs4 import BeautifulSoup; _,_,html=await _fetch(url); soup=BeautifulSoup(html,"lxml")
        parsed=urlparse(url); base=f"{parsed.scheme}://{parsed.netloc}"; scripts=[]
        for tag in soup.find_all("script"):
            src=tag.get("src","")
            if src:
                full=src if src.startswith("http") else base+src if src.startswith("/") else base+"/"+src
                scripts.append({"src":full,"async":tag.has_attr("async"),"defer":tag.has_attr("defer")})
        return {"url":url,"script_count":len(scripts),"scripts":scripts}
    except Exception as e: return f"JS file listing failed: {e}"

async def detect_cdn(url):
    try:
        import httpx,socket; parsed=urlparse(url); domain=parsed.netloc
        CDN_HEADERS={"cloudflare":["cf-ray","cf-cache-status"],"akamai":["x-akamai-request-id"],"fastly":["x-fastly-request-id"],"cloudfront":["x-amz-cf-id"],"sucuri":["x-sucuri-id"]}
        async with httpx.AsyncClient(timeout=10.0,verify=False) as c: r=await c.get(url,headers={"User-Agent":"Mozilla/5.0"})
        hl={k.lower():v for k,v in r.headers.items()}; detected=[cdn.title() for cdn,sigs in CDN_HEADERS.items() if any(s in hl for s in sigs)]
        try: ip=socket.gethostbyname(domain)
        except Exception: ip="N/A"
        return {"domain":domain,"ip":ip,"cdn_detected":detected or ["None detected"],"server":r.headers.get("server","N/A")}
    except Exception as e: return f"CDN detection failed: {e}"

async def detect_waf(url):
    try:
        import httpx
        WAF_SIGS={"Cloudflare":["cloudflare","cf-ray","attention required"],"Akamai":["akamai","reference #"],"Incapsula":["incapsula","visid_incap"],"Sucuri":["sucuri"],"ModSecurity":["mod_security","modsecurity"],"AWS WAF":["x-amzn-requestid"]}
        found=[]
        async with httpx.AsyncClient(timeout=10.0,verify=False,follow_redirects=True) as c:
            for payload in [f"{url}?id=1'",f"{url}?q=<script>alert(1)</script>"]:
                try:
                    r=await c.get(payload,headers={"User-Agent":"Mozilla/5.0"}); combined=(str(r.headers)+r.text).lower()
                    for waf,sigs in WAF_SIGS.items():
                        if any(s.lower() in combined for s in sigs) and waf not in found: found.append(waf)
                except Exception: pass
        return {"url":url,"waf_detected":found or ["None detected"],"protected":len(found)>0}
    except Exception as e: return f"WAF detection failed: {e}"
