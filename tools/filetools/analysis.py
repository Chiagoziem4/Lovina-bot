from __future__ import annotations
import asyncio,hashlib,io,math,zipfile

FILE_SIGS={b"\x89PNG\r\n\x1a\n":"PNG Image",b"\xff\xd8\xff":"JPEG Image",b"GIF87a":"GIF Image",b"GIF89a":"GIF Image",b"PK\x03\x04":"ZIP/DOCX/XLSX",b"%PDF":"PDF Document",b"\x7fELF":"ELF Executable",b"MZ":"PE Executable (Windows)",b"\xd0\xcf\x11\xe0":"MS Office (legacy)",b"SQLite format 3":"SQLite Database",b"#!/":"Shell Script",b"<!DOCTYPE html":"HTML Document",b"<?xml":"XML Document"}

def detect_file_type(data):
    for sig,name in FILE_SIGS.items():
        if data[:len(sig)]==sig: return name
    printable=sum(1 for b in data[:512] if 32<=b<127 or b in (9,10,13))
    return "Text File" if printable/min(len(data),512)>0.85 else "Unknown Binary"

def compute_entropy(data):
    if not data: return 0.0
    freq=[0]*256
    for b in data: freq[b]+=1
    length=len(data); e=0.0
    for f in freq:
        if f>0: p=f/length; e-=p*math.log2(p)
    return round(e,4)

def _entropy_note(e):
    if e>7.5: return "Very high — likely encrypted or compressed"
    elif e>6.5: return "High — possibly obfuscated"
    elif e>5.0: return "Medium — mixed content"
    return "Low — plain text or structured data"

def _human_size(size):
    for unit in ["B","KB","MB","GB"]:
        if size<1024: return f"{size:.1f} {unit}"
        size/=1024
    return f"{size:.1f} TB"

def extract_strings_from_bytes(data,min_len=4):
    result=[]; current=[]
    for b in data:
        if 32<=b<127: current.append(chr(b))
        else:
            if len(current)>=min_len: result.append("".join(current))
            current=[]
    if len(current)>=min_len: result.append("".join(current))
    return result[:100]

def hex_dump(data,width=16):
    lines=[]
    for i in range(0,min(len(data),256),width):
        chunk=data[i:i+width]; hex_part=" ".join(f"{b:02x}" for b in chunk); ascii_part="".join(chr(b) if 32<=b<127 else "." for b in chunk)
        lines.append(f"{i:08x}  {hex_part:<{width*3}}  |{ascii_part}|")
    if len(data)>256: lines.append(f"... ({len(data)-256} more bytes)")
    return "\n".join(lines)

def analyse_file_bytes(data,filename="unknown"):
    ft=detect_file_type(data); e=compute_entropy(data)
    hashes={"md5":hashlib.md5(data).hexdigest(),"sha1":hashlib.sha1(data).hexdigest(),"sha256":hashlib.sha256(data).hexdigest()}
    strings=extract_strings_from_bytes(data)
    suspicious=[s for s in strings if any(k in s.lower() for k in ["password","secret","api_key","token","admin","exec","eval","powershell","cmd.exe","/bin/sh","wget","curl","base64"])]
    return {"filename":filename,"size_bytes":len(data),"size_human":_human_size(len(data)),"file_type":ft,"entropy":e,"entropy_note":_entropy_note(e),"hashes":hashes,"printable_strings":len(strings),"suspicious_strings":suspicious[:10],"hex_preview":data[:32].hex()}

def inspect_zip(data):
    try:
        with zipfile.ZipFile(io.BytesIO(data),"r") as zf:
            entries=[{"name":i.filename,"size":i.file_size,"compressed":i.compress_size,"encrypted":bool(i.flag_bits&0x1)} for i in zf.infolist()]
        enc=sum(1 for e in entries if e["encrypted"])
        return {"total_files":len(entries),"encrypted_files":enc,"is_encrypted":enc>0,"total_size":sum(e["size"] for e in entries),"files":entries[:30]}
    except zipfile.BadZipFile: return "Not a valid ZIP file"
    except Exception as e: return f"ZIP inspection failed: {e}"

async def fetch_and_analyse_file(url):
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30.0,verify=False) as c: r=await c.get(url,headers={"User-Agent":"Mozilla/5.0"})
        data=r.content; filename=url.split("/")[-1].split("?")[0] or "file"
        result=analyse_file_bytes(data,filename); result["url"]=url; result["http_status"]=r.status_code; result["content_type"]=r.headers.get("content-type","N/A")
        if filename.lower().endswith(".zip"): result["zip_info"]=inspect_zip(data)
        result["hex_dump"]=hex_dump(data)
        return result
    except Exception as e: return f"File fetch failed: {e}"

async def extract_exif(data,filename="image"):
    try:
        import re
        from PIL import Image; from PIL.ExifTags import TAGS,GPSTAGS
        img=Image.open(io.BytesIO(data)); exif_data=img._getexif()
        if not exif_data: return {"filename":filename,"format":img.format,"size":img.size,"mode":img.mode,"exif":"No EXIF data"}
        parsed={}; gps_info={}
        for tag_id,value in exif_data.items():
            tag=TAGS.get(tag_id,str(tag_id))
            if tag=="GPSInfo":
                for gid,gval in value.items(): gps_info[GPSTAGS.get(gid,str(gid))]=str(gval)
            else: parsed[tag]=str(value)[:100]
        gps_link=None
        if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
            try:
                def dms(dms_str,ref):
                    vals=[float(x) for x in re.findall(r"[\d.]+",str(dms_str))]; dd=vals[0]+vals[1]/60+vals[2]/3600
                    return -dd if ref in ("S","W") else dd
                lat=round(dms(gps_info["GPSLatitude"],gps_info.get("GPSLatitudeRef","N")),6)
                lon=round(dms(gps_info["GPSLongitude"],gps_info.get("GPSLongitudeRef","E")),6)
                gps_link=f"https://www.google.com/maps?q={lat},{lon}"
            except Exception: pass
        return {"filename":filename,"format":img.format,"size":f"{img.size[0]}x{img.size[1]}","mode":img.mode,"exif":parsed,"gps":gps_info,"gps_maps_link":gps_link}
    except ImportError: return "Pillow not installed"
    except Exception as e: return f"EXIF extraction failed: {e}"
