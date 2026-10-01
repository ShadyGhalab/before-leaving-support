#!/usr/bin/env python3
"""Fetch a reviewable Apple lookup snapshot. No local changes without --apply-release.
Updates only release notes in site config, never silently changes identity, prices or features.
Network failure leaves the existing source untouched. Build after reviewing a successful update.
"""
import argparse,json
from datetime import date
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError,URLError
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--country',default='us');ap.add_argument('--apply-release',action='store_true');args=ap.parse_args()
    cfgpath=ROOT/'site-src/data/site.json';cfg=json.loads(cfgpath.read_text())
    url='https://itunes.apple.com/lookup?'+urlencode({'id':cfg['app_store_id'],'country':args.country})
    try:
        with urlopen(Request(url,headers={'User-Agent':'ReadyKin-MetadataReview/1.0'}),timeout=25) as response:data=json.load(response)
        results=[x for x in data.get('results',[]) if str(x.get('trackId'))==cfg['app_store_id']]
        if len(results)!=1:raise ValueError('Apple did not return exactly the requested app. No changes made.')
        app=results[0]
        snapshot={k:app.get(k) for k in ['trackId','trackName','sellerName','version','currentVersionReleaseDate','releaseNotes','minimumOsVersion','languageCodesISO2A','price','currency','trackViewUrl']}
        print(json.dumps(snapshot,ensure_ascii=False,indent=2))
        if not args.apply_release:print('\nReview this snapshot. No file was changed.');return
        if 'readykin' not in str(app.get('trackName','')).lower():raise ValueError('Listing still has a different product name. Review the snapshot manually before changing release notes.')
        if not all(app.get(k) for k in ['version','currentVersionReleaseDate','releaseNotes']):raise ValueError('Release fields are incomplete. No changes made.')
        release_date=app['currentVersionReleaseDate'][:10];date.fromisoformat(release_date)
        if release_date>date.today().isoformat():raise ValueError('Release date is in the future. Review manually.')
        cfg['release']={'version':app['version'],'date':release_date,'notes':[app['releaseNotes']],'source_url':cfg['app_store_url']}
        cfgpath.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
        print('Updated the reviewed release fields. Run build-site.py and validate-site.py before deploying.')
    except (HTTPError,URLError,TimeoutError,ValueError,KeyError) as error:raise SystemExit(str(error)) from error
if __name__=='__main__':main()
