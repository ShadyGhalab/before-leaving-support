#!/usr/bin/env python3
"""Read-only HTTP smoke checks. Defaults to localhost; --production explicitly checks the live origin.
Checks served resources, not indexing, crawler IP access, native iOS association or ranking.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]

def fetch(base: str,path: str,cache_bust: str | None = None):
    suffix=('?readykin_check='+cache_bust) if cache_bust else ''
    req=Request(base+path+suffix,headers={'User-Agent':'ReadyKin-DeploymentCheck/1.0'})
    try:
        with urlopen(req,timeout=15) as r:
            return r.status,{k.lower():v for k,v in r.headers.items()},r.read(8*1024*1024),r.geturl()
    except HTTPError as e:
        return e.code,{k.lower():v for k,v in e.headers.items()},e.read(8*1024*1024),e.geturl()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--production',action='store_true')
    ap.add_argument('--cache-bust',help='Production-only deployment identifier used to bypass stale CDN objects.')
    ap.add_argument('--base-url',default='http://127.0.0.1:8765',help='Local preview origin; use --production for live checks.')
    args=ap.parse_args()
    manifest=json.loads((ROOT/'site-src/data/build-manifest.json').read_text())
    base=(manifest['site_url'] if args.production else args.base_url).rstrip('/')
    u=urlsplit(base)
    if u.username or u.password or u.query or u.fragment or u.path or (not args.production and u.hostname not in ['127.0.0.1','localhost']):
        raise SystemExit('Use a local HTTP origin, or --production for the configured HTTPS production origin.')
    if args.production and u.scheme!='https':raise SystemExit('Production checks require HTTPS.')
    if args.cache_bust and (not args.production or not re.fullmatch(r'[A-Za-z0-9._-]{1,80}',args.cache_bust)):
        raise SystemExit('--cache-bust requires --production and a short deployment identifier.')
    checks=[]
    def record(name,passed,detail=''):
        checks.append({'check':name,'passed':bool(passed),'detail':detail})
    try:
        for path,p in manifest['pages'].items():
            status,headers,body,final=fetch(base,path,args.cache_bust);text=body.decode('utf-8')
            record(path+' status',status==200,f'HTTP {status}')
            record(path+' html','text/html' in headers.get('content-type',''))
            if p['indexable']:
                record(path+' canonical',f'href="{manifest["site_url"]+path}"' in text)
                record(path+' current generated HTML',hashlib.sha256(body).hexdigest()==p['sha256'],'Exact file hash check; host HTML rewriting may need manual review.')
            else:record(path+' noindex','name="robots" content="noindex' in text)
        for path in ['/robots.txt','/sitemap.xml','/'+manifest['indexnow_key_file'],'/images/social/readykin-social.jpg']:
            status,headers,body,final=fetch(base,path,args.cache_bust)
            record(path+' status',status==200,f'HTTP {status}')
            record(path+' content',body==(ROOT/path.lstrip('/')).read_bytes())
        for filename,expected in json.loads((ROOT/'tests/protected-files.json').read_text()).items():
            status,headers,body,final=fetch(base,'/'+filename,args.cache_bust)
            record(filename+' preserved',status==200 and hashlib.sha256(body).hexdigest()==expected)
            if filename.endswith('apple-app-site-association'):
                record('Apple association content type','application/json' in headers.get('content-type','') or 'application/pkcs7-mime' in headers.get('content-type',''),headers.get('content-type',''))
                clean_final=urlsplit(final)._replace(query='',fragment='').geturl()
                record('Apple association no redirect',clean_final==base+'/'+filename)
        if manifest.get('verification_file'):
            path='/'+manifest['verification_file'];status,headers,body,final=fetch(base,path,args.cache_bust)
            record('Verification file exact content',status==200 and body==(ROOT/path.lstrip('/')).read_bytes(),'Does not confirm account verification.')
        status,headers,body,final=fetch(base,'/readykin-this-path-must-not-exist',args.cache_bust)
        record('Unknown URL is genuine HTTP 404',status==404,f'HTTP {status}')
        record('Custom 404 is noindex','noindex' in body.decode('utf-8','replace'))
        for path in ['/site-src/data/site.json','/scripts/build-site.py','/tests/protected-files.json','/docs/CONTENT_REVIEW.md']:
            status,headers,body,final=fetch(base,path,args.cache_bust)
            record('Source not published: '+path,status==404,f'HTTP {status}')
    except (URLError,TimeoutError,UnicodeError,OSError) as e:
        record('HTTP check completed',False,str(e))
    report={'checked_at':datetime.now(timezone.utc).isoformat(),'base_url':base,'mode':'production' if args.production else 'local','status':'passed' if all(x['passed'] for x in checks) else 'failed','checks':len(checks),'failures':[x for x in checks if not x['passed']],'results':checks,'scope':'Read-only HTTP checks. Not a crawl/indexing, security, privacy, performance or native-device certification.'}
    out=ROOT/'reports'/('production-http-validation.json' if args.production else 'http-validation.json');out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
    return 0 if report['status']=='passed' else 1
if __name__=='__main__':sys.exit(main())
