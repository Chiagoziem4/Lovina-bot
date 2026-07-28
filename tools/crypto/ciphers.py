from __future__ import annotations
import base64,codecs,hashlib,html,math,random,re,secrets,string,urllib.parse,uuid

def generate_password(length=20,*,symbols=True,numbers=True):
    chars=string.ascii_letters+(string.digits if numbers else "")+("!@#$%^&*()-_=+[]{}|;:,.<>?" if symbols else "")
    pw="".join(secrets.choice(chars) for _ in range(length)); entropy=math.log2(len(chars))*length
    return {"password":pw,"length":length,"entropy_bits":round(entropy,1),"strength":"Very Strong" if entropy>80 else "Strong" if entropy>60 else "Moderate" if entropy>40 else "Weak"}

def check_password_strength(password):
    score=0; issues=[]
    if len(password)>=12: score+=2
    elif len(password)>=8: score+=1
    else: issues.append("Too short")
    if re.search(r"[A-Z]",password): score+=1
    else: issues.append("No uppercase")
    if re.search(r"[a-z]",password): score+=1
    else: issues.append("No lowercase")
    if re.search(r"\d",password): score+=1
    else: issues.append("No numbers")
    if re.search(r"[^A-Za-z0-9]",password): score+=2
    else: issues.append("No special characters")
    charset=sum([26 if re.search(r"[a-z]",password) else 0,26 if re.search(r"[A-Z]",password) else 0,10 if re.search(r"\d",password) else 0,32 if re.search(r"[^A-Za-z0-9]",password) else 0])
    entropy=math.log2(charset)*len(password) if charset>0 else 0
    labels={0:"Very Weak",1:"Weak",2:"Weak",3:"Moderate",4:"Strong",5:"Strong",6:"Very Strong",7:"Very Strong"}
    return {"password":password,"score":score,"max_score":7,"strength":labels.get(score,"Unknown"),"entropy_bits":round(entropy,1),"length":len(password),"issues":issues}

def generate_token(length=32):
    return {"hex_token":secrets.token_hex(length//2),"url_safe":secrets.token_urlsafe(length),"uuid4":str(uuid.uuid4()),"numeric_pin":"".join(secrets.choice(string.digits) for _ in range(6))}

def caesar_cipher(text,shift,decrypt=False):
    if decrypt: shift=-shift
    r=[]
    for ch in text:
        if ch.isalpha(): base=ord("A") if ch.isupper() else ord("a"); r.append(chr((ord(ch)-base+shift)%26+base))
        else: r.append(ch)
    return {"input":text,"shift":-shift if decrypt else shift,"output":"".join(r),"mode":"decrypt" if decrypt else "encrypt"}

def rot_brute(text):
    results=[]
    for shift in range(1,26):
        out=[]
        for ch in text:
            if ch.isalpha(): base=ord("A") if ch.isupper() else ord("a"); out.append(chr((ord(ch)-base+shift)%26+base))
            else: out.append(ch)
        results.append({"shift":shift,"text":"".join(out)})
    return results

def vigenere_cipher(text,key,decrypt=False):
    key=key.upper(); r=[]; ki=0
    for ch in text:
        if ch.isalpha():
            base=ord("A") if ch.isupper() else ord("a"); k=ord(key[ki%len(key)])-ord("A")
            if decrypt: k=-k
            r.append(chr((ord(ch)-base+k)%26+base)); ki+=1
        else: r.append(ch)
    return {"input":text,"key":key,"output":"".join(r),"mode":"decrypt" if decrypt else "encrypt"}

def atbash_cipher(text):
    r=[]
    for ch in text:
        if ch.isalpha(): base=ord("A") if ch.isupper() else ord("a"); r.append(chr(base+25-(ord(ch)-base)))
        else: r.append(ch)
    return {"input":text,"output":"".join(r)}

def xor_cipher(text,key):
    kb=key.encode(); tb=text.encode()
    xored=bytes(b^kb[i%len(kb)] for i,b in enumerate(tb))
    return {"input":text,"key":key,"output_hex":xored.hex(),"output_base64":base64.b64encode(xored).decode()}

MORSE_ENC={'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..','0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.','.':".-.-.-",",":'--..--','?':'..--..','!':'-.-.--',' ':'/'}
MORSE_DEC={v:k for k,v in MORSE_ENC.items()}
def morse_encode(text): return {"input":text,"output":" ".join(MORSE_ENC.get(c.upper(),c) for c in text)}
def morse_decode(morse): return {"input":morse,"output":" ".join("".join(MORSE_DEC.get(c,"?") for c in w.split()) for w in morse.strip().split(" / "))}

def rail_fence_cipher(text,rails,decrypt=False):
    if decrypt:
        n=len(text); pat=[]
        for i in range(n):
            cycle=(rails-1)*2; pos=i%cycle; rail=pos if pos<rails else cycle-pos; pat.append(rail)
        indices=sorted(range(n),key=lambda x:pat[x]); result=[""]*n
        for i,idx in enumerate(indices): result[idx]=text[i]
        return {"input":text,"rails":rails,"output":"".join(result),"mode":"decrypt"}
    fence=[[] for _ in range(rails)]; rail=0; direction=1
    for ch in text:
        fence[rail].append(ch)
        if rail==0: direction=1
        elif rail==rails-1: direction=-1
        rail+=direction
    return {"input":text,"rails":rails,"output":"".join(ch for r in fence for ch in r),"mode":"encrypt"}

def frequency_analysis(text):
    letters=[ch.upper() for ch in text if ch.isalpha()]; total=len(letters)
    if not total: return {"error":"No alphabetic characters"}
    freq={}
    for ch in letters: freq[ch]=freq.get(ch,0)+1
    sorted_freq=sorted(freq.items(),key=lambda x:x[1],reverse=True)
    return {"total_letters":total,"unique_letters":len(freq),"top_10":[{"char":ch,"count":c,"pct":round(c/total*100,1)} for ch,c in sorted_freq[:10]],"hint":"Most common is likely E, T, or A in English"}

def base_convert(value,from_base,to_base):
    try:
        decimal=int(value,from_base)
        if to_base==2: result=bin(decimal)[2:]
        elif to_base==8: result=oct(decimal)[2:]
        elif to_base==10: result=str(decimal)
        elif to_base==16: result=hex(decimal)[2:].upper()
        else:
            digits=string.digits+string.ascii_uppercase; result=""; n=decimal
            while n: result=digits[n%to_base]+result; n//=to_base
            result=result or "0"
        return {"input":value,"from_base":from_base,"to_base":to_base,"output":result,"decimal":decimal}
    except Exception as e: return {"error":str(e)}

def hex_to_binary(hex_str):
    try:
        clean=hex_str.strip().replace(" ","").replace("0x",""); decimal=int(clean,16)
        return {"hex":clean.upper(),"decimal":decimal,"binary":bin(decimal)[2:],"octal":oct(decimal)[2:],"bytes":len(clean)//2}
    except Exception as e: return {"error":str(e)}

def extended_encode(text,fmt):
    try:
        match fmt.lower():
            case "base32": return {"format":"base32","output":base64.b32encode(text.encode()).decode()}
            case "base85": return {"format":"base85","output":base64.b85encode(text.encode()).decode()}
            case "binary": return {"format":"binary","output":" ".join(format(ord(c),"08b") for c in text)}
            case "decimal": return {"format":"decimal","output":" ".join(str(ord(c)) for c in text)}
            case _: return f"Unknown format: {fmt}. Use: base32, base85, binary, decimal"
    except Exception as e: return f"Encoding failed: {e}"

def uuid_analyse(uuid_str):
    try:
        u=uuid.UUID(uuid_str); info={"uuid":str(u),"version":u.version,"variant":str(u.variant)}
        if u.version==1:
            from datetime import datetime; ts=(u.time-0x01b21dd213814000)*100/1e9
            info["timestamp"]=datetime.utcfromtimestamp(ts).isoformat(); info["node"]=hex(u.node)
        return info
    except Exception as e: return f"Invalid UUID: {e}"
