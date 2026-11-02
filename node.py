#!/usr/bin/env python3
"""Generic sealed-record reader."""
from pathlib import Path
from getpass import getpass
import hashlib, json, io, zipfile, struct, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
ROOT=Path(__file__).resolve().parent
MAGIC=b'\x89KSL\x05'
def normalized(s):return ''.join(ch for ch in s.upper() if ch.isalnum())
def open_record(path,access,receipt):
    src=path.read_bytes()
    if len(src)<54 or src[:5]!=MAGIC:raise ValueError('invalid record')
    rounds=struct.unpack('>I',src[5:9])[0]
    if not 100000<=rounds<=500000:raise ValueError('invalid parameters')
    salt,nonce,encrypted=src[9:25],src[25:37],src[37:]
    key=hashlib.pbkdf2_hmac('sha256',(normalized(access)+'|'+receipt).encode(),salt,rounds,32)
    plain=AESGCM(key).decrypt(nonce,encrypted,b'KSL5|capsule')
    size=struct.unpack('>I',plain[:4])[0]
    if size>len(plain)-4:raise ValueError('invalid payload')
    return plain[4:4+size]
def main():
    if len(sys.argv)!=2 or not (len(sys.argv[1])==24 and all(ch in '0123456789abcdef' for ch in sys.argv[1])):
        raise SystemExit('Usage: python3 node.py <record-id>')
    ident=sys.argv[1]
    path=ROOT/'store'/(ident+'.bin')
    if not path.is_file():raise SystemExit('NO RECORD')
    access=getpass('Access phrase: ')
    state=ROOT/'.ktp'; state.mkdir(exist_ok=True)
    receipts=state/'.state'
    known=[]
    if receipts.exists():
        try:known=json.loads(receipts.read_text())
        except (ValueError,OSError):known=[]
    if not isinstance(known,list):known=[]
    raw=None
    for prior in ['']+[x for x in known if isinstance(x,str) and len(x)==64]:
        try: raw=open_record(path,access,prior);break
        except Exception:continue
    if raw is None:raise SystemExit('LOCKED / authentication failed')
    target=state/ident
    # Verify the complete archive before writing any files.
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        entries=[]
        for member in z.infolist():
            fp=Path(member.filename)
            if fp.is_absolute() or '..' in fp.parts or member.is_dir() or member.file_size>3000000:
                raise SystemExit('INVALID PAYLOAD')
            entries.append((fp,z.read(member)))
    target.mkdir(parents=True,exist_ok=True)
    for fp,data in entries:
        dest=target/fp;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    digest=hashlib.sha256(raw).hexdigest()
    if digest not in known:known.append(digest)
    receipts.write_text(json.dumps(known))
    print('OPEN => .ktp/'+ident)
    for fp,_ in entries: print('   '+str(fp))
if __name__=='__main__':main()
