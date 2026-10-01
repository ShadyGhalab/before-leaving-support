#!/usr/bin/env python3
"""Prepare or submit an IndexNow notification. Dry-run unless --submit is explicitly set.
This notifies participating search engines, not Google or a special ChatGPT ranking API.
The ownership key is intentionally public. The live key file is checked before submission.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]

def request(req: Request, attempts=3):
    for attempt in range(attempts):
        try:
            with urlopen(req,timeout=25) as response:return response.status,response.read(1024*1024)
        except HTTPError as error:
            if error.code not in [429,500,502,503,504] or attempt==attempts-1:raise
        except (URLError,TimeoutError):
            if attempt==attempts-1:raise
        time.sleep(2**attempt)
    raise RuntimeError('Request did not complete')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--submit',action='store_true',help='Perform the live ownership check and POST. Default: print only.')
    ap.add_argument('--changed-only',action='store_true',help='Notify only URLs changed in the most recent local build.')
    args=ap.parse_args()
    cfg=json.loads((ROOT/'site-src/data/site.json').read_text())
    base=cfg['site_url'].rstrip('/');host=urlsplit(base).hostname;key=cfg['indexnow_key']
    if args.changed_only:urls=json.loads((ROOT/'site-src/data/build-manifest.json').read_text())['changed_urls']
    else:urls=[n.text for n in ET.parse(ROOT/'sitemap.xml').findall('.//{*}loc')]
    urls=list(dict.fromkeys(urls))
    if not urls:print('No changed URLs to submit.');return
    for u in urls:
        parsed=urlsplit(u)
        if parsed.scheme!='https' or parsed.hostname!=host or parsed.query or parsed.fragment:raise SystemExit(f'Unsafe or off-domain URL: {u}')
    payload={'host':host,'key':key,'keyLocation':base+'/'+key+'.txt','urlList':urls}
    if not args.submit:
        print(json.dumps(payload,indent=2));print('\nDRY RUN. No request was sent. Deploy first, then use --submit.');return
    try:
        status,body=request(Request(payload['keyLocation'],headers={'User-Agent':'ReadyKin-DeploymentCheck/1.0'}))
        if status!=200 or body.decode('utf-8').strip()!=key:raise RuntimeError('Live key file does not match. Deploy it before submitting.')
        # Batches follow the documented 10,000-URL limit.
        for start in range(0,len(urls),10000):
            batch=dict(payload,urlList=urls[start:start+10000])
            status,response=request(Request('https://api.indexnow.org/indexnow',data=json.dumps(batch).encode(),method='POST',headers={'Content-Type':'application/json; charset=utf-8','User-Agent':'ReadyKin-IndexNow/1.0'}))
            if status not in [200,202]:raise RuntimeError(f'Unexpected IndexNow status: {status}')
            print(f'IndexNow HTTP {status}: {len(batch["urlList"])} URL notifications accepted. Indexing is not guaranteed.')
    except (HTTPError,URLError,TimeoutError,RuntimeError,UnicodeError) as error:
        raise SystemExit(f'IndexNow did not complete: {error}') from error
if __name__=='__main__':main()
