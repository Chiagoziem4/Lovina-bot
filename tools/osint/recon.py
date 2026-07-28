from __future__ import annotations
import asyncio,re
from urllib.parse import urlparse,quote

async def github_osint(username):
    try:
        import httpx; headers={"Accept":"application/vnd.github+json","User-Agent":"Mozilla/5.0"}
        async with httpx.AsyncClient(timeout=15.0) as c:
            r=await c.get(f"https://api.github.com/users/{username}",headers=headers)
            if r.status_code==404: return f"GitHub user '{username}' not found"
            if r.status_code==403: return "GitHub API rate limit hit — try again in 60 seconds"
            user=r.json(); rr=await c.get(f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated",headers=headers)
            repos=rr.json() if rr.status_code==200 else []
        languages={}
        for repo in repos:
            lang=repo.get("language")
            if lang: languages[lang]=languages.get(lang,0)+1
        top_repos=sorted(repos,key=lambda x:x.get("stargazers_count",0),reverse=True)[:5]
        return {"username":username,"name":user.get("name"),"bio":user.get("bio"),"location":user.get("location"),"email":user.get("email"),"company":user.get("company"),"website":user.get("blog"),"created":user.get("created_at","")[:10],"followers":user.get("followers",0),"following":user.get("following",0),"public_repos":user.get("public_repos",0),"top_languages":dict(sorted(languages.items(),key=lambda x:x[1],reverse=True)[:5]),"top_repos":[{"name":r["name"],"stars":r["stargazers_count"],"url":r["html_url"]} for r in top_repos],"profile_url":f"https://github.com/{username}"}
    except Exception as e: return f"GitHub OSINT failed: {e}"

async def email_check(email):
    try:
        import dns.resolver
        if not re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$",email): return {"email":email,"valid_format":False}
        domain=email.split("@")[1]; has_mx=False; mx=[]
        try:
            loop=asyncio.get_event_loop()
            records=await loop.run_in_executor(None,lambda:list(dns.resolver.resolve(domain,"MX")))
            mx=[str(r.exchange) for r in records]; has_mx=True
        except Exception: pass
        DISPOSABLE=["mailinator.com","guerrillamail.com","tempmail.com","yopmail.com","maildrop.cc","10minutemail.com","trashmail.com","temp-mail.org"]
        is_disposable=domain.lower() in DISPOSABLE
        return {"email":email,"valid_format":True,"domain":domain,"has_mx_record":has_mx,"mx_records":mx[:3],"is_disposable":is_disposable,"deliverable":has_mx and not is_disposable}
    except Exception as e: return f"Email check failed: {e}"

async def archive_search(domain):
    try:
        import httpx; clean=domain.replace("https://","").replace("http://","").strip("/")
        api=f"https://web.archive.org/cdx/search/cdx?url={clean}/*&output=json&limit=20&fl=timestamp,original,statuscode,mimetype&filter=statuscode:200&collapse=urlkey"
        async with httpx.AsyncClient(timeout=20.0) as c: r=await c.get(api); data=r.json()
        if not data or len(data)<2: return {"domain":clean,"found":False,"snapshots":0}
        snaps=[{"date":f"{row[0][:4]}-{row[0][4:6]}-{row[0][6:8]}","url":row[1],"archive":f"https://web.archive.org/web/{row[0]}/{row[1]}"} for row in data[1:]]
        return {"domain":clean,"found":True,"total_snapshots":len(snaps),"earliest":snaps[-1]["date"] if snaps else None,"latest":snaps[0]["date"] if snaps else None,"snapshots":snaps[:10]}
    except Exception as e: return f"Archive search failed: {e}"

def generate_email_patterns(first,last,domain):
    f,l=first.lower(),last.lower(); fi,li=f[0],l[0]
    patterns=[f"{f}@{domain}",f"{l}@{domain}",f"{f}.{l}@{domain}",f"{fi}{l}@{domain}",f"{f}{li}@{domain}",f"{f}_{l}@{domain}",f"{fi}.{l}@{domain}",f"{f}{l}@{domain}",f"{l}.{f}@{domain}",f"{l}{fi}@{domain}",f"{fi}{li}@{domain}",f"{f}-{l}@{domain}"]
    return {"first":first,"last":last,"domain":domain,"patterns":patterns,"total":len(patterns),"note":"Use /emailcheck to validate each pattern"}

def reverse_image_search_links(image_url):
    encoded=quote(image_url,safe="")
    return {"image_url":image_url,"google":f"https://www.google.com/searchbyimage?image_url={encoded}","yandex":f"https://yandex.com/images/search?url={encoded}&rpt=imageview","tineye":f"https://tineye.com/search?url={encoded}","bing":f"https://www.bing.com/images/search?view=detailv2&iss=sbi&q=imgurl:{encoded}"}

async def pastebin_search(keyword):
    try:
        import httpx; from bs4 import BeautifulSoup
        async with httpx.AsyncClient(timeout=15.0,headers={"User-Agent":"Mozilla/5.0"}) as c: r=await c.get(f"https://pastebin.com/search?q={quote(keyword)}")
        soup=BeautifulSoup(r.text,"lxml"); results=[]
        for item in soup.select(".search-result")[:10]:
            t=item.select_one(".search-result-title a")
            if t: results.append({"title":t.get_text(strip=True),"url":"https://pastebin.com"+t.get("href","")})
        return {"keyword":keyword,"results_found":len(results),"results":results}
    except Exception as e: return f"Pastebin search failed: {e}"

def generate_dorks(target):
    domain=target.replace("https://","").replace("http://","").split("/")[0]
    dorks=[f"site:{domain} filetype:pdf",f"site:{domain} filetype:sql OR filetype:db OR filetype:backup",f"site:{domain} inurl:admin OR inurl:login OR inurl:dashboard",f"site:{domain} inurl:config OR inurl:env OR inurl:settings",f'site:{domain} intitle:"index of" OR intitle:"directory listing"',f'site:{domain} "password" OR "passwd" OR "api_key" OR "secret"',f"site:{domain} ext:log OR ext:txt OR ext:bak",f"site:github.com \"{domain}\"",f"site:pastebin.com \"{domain}\"",f"\"{domain}\" \"password\"",f"inurl:\"{domain}\" filetype:php inurl:id=",f"\"{domain}\" site:linkedin.com"]
    return {"target":domain,"dorks":dorks,"total":len(dorks),"note":"For authorised reconnaissance only"}

async def cms_detector(url):
    try:
        import httpx; from bs4 import BeautifulSoup
        async with httpx.AsyncClient(timeout=15.0,verify=False,follow_redirects=True) as c: r=await c.get(url,headers={"User-Agent":"Mozilla/5.0"})
        html=r.text; headers={k.lower():v for k,v in r.headers.items()}; soup=BeautifulSoup(html,"lxml"); detected={}
        CMS={"WordPress":{"html":["/wp-content/","/wp-includes/"],"meta":["generator.*wordpress"]},"Drupal":{"html":["Drupal.settings","/sites/default/files/"],"meta":["generator.*drupal"]},"Joomla":{"html":["/components/com_","joomla"]},"Shopify":{"html":["cdn.shopify.com","Shopify.theme"]},"Wix":{"html":["wix.com","wixsite.com"]},"Magento":{"html":["Mage.Cookies","/skin/frontend/"]},"Ghost":{"html":["ghost.io","content/themes/casper"]}}
        for cms,patterns in CMS.items():
            score=sum(1 for p in patterns.get("html",[]) if p.lower() in html.lower())
            for p in patterns.get("meta",[]):
                for tag in soup.find_all("meta",{"name":"generator"}):
                    if re.search(p,tag.get("content",""),re.I): score+=3
            if score>0: detected[cms]={"confidence":"High" if score>=3 else "Medium" if score>=2 else "Low","score":score}
        return {"url":url,"cms_detected":detected,"primary":max(detected.items(),key=lambda x:x[1]["score"])[0] if detected else "Unknown","server":r.headers.get("server","N/A")}
    except Exception as e: return f"CMS detection failed: {e}"
