#!/usr/bin/env python3
"""Dependency-free static checks for generated ReadyKin pages. This is not a search ranking test."""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import date
import argparse,hashlib,json,re,sys
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin,urlsplit,unquote
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True)
        self.tags=defaultdict(list);self.ids=[];self.text=[];self.title='';self.scripts=[];self._script=None;self._in_title=False;self._ignore=0
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);self.tags[tag].append(a)
        if a.get('id'):self.ids.append(a['id'])
        if tag=='title':self._in_title=True
        if tag=='script':self._script={'type':a.get('type'),'text':''}
        if tag in ['script','style','head']:self._ignore+=1
    def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)
    def handle_endtag(self,tag):
        if tag=='title':self._in_title=False
        if tag=='script' and self._script is not None:self.scripts.append(self._script);self._script=None
        if tag in ['script','style','head']:self._ignore=max(0,self._ignore-1)
    def handle_data(self,data):
        if self._in_title:self.title+=data
        if self._script is not None:self._script['text']+=data
        if not self._ignore:self.text.append(data)
    def meta(self,name,prop=False):
        return [x.get('content','') for x in self.tags['meta'] if x.get('property' if prop else 'name')==name]

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--report',default='reports/static-validation.json');args=ap.parse_args()
    manifest=json.loads((ROOT/'site-src/data/build-manifest.json').read_text());base=manifest['site_url'];pages={};errors=[];warnings=[];checks=0;incoming=Counter();titles=defaultdict(list);descs=defaultdict(list)
    def check(condition,message):
        nonlocal checks
        checks+=1
        if not condition:errors.append(message)
    for path,entry in manifest['pages'].items():
        src=ROOT/entry['file'];check(src.is_file(),f'{path}: missing HTML file')
        if not src.is_file():continue
        text=src.read_text();p=Page(text);pages[path]=p
        check(text.lstrip().lower().startswith('<!doctype html>'),f'{path}: doctype or raw front matter problem')
        check(len(p.tags['html'])==1 and p.tags['html'][0].get('lang')=='en',f'{path}: missing document language')
        check(len(p.tags['h1'])==1,f'{path}: expected one h1, found {len(p.tags["h1"])}')
        check(len(p.tags['main'])==1,f'{path}: expected one main landmark')
        check(len(p.ids)==len(set(p.ids)),f'{path}: duplicate IDs')
        check(len(p.tags['title'])==1 and bool(p.title),f'{path}: invalid title')
        check(len(p.meta('description'))==1 and bool(p.meta('description')[0]),f'{path}: missing unique description')
        check('width=device-width' in ''.join(p.meta('viewport')),f'{path}: missing responsive viewport')
        check(not any('google' in x.get('href','') and 'fonts.' in x.get('href','') for x in p.tags['link']),f'{path}: external font request')
        check('$discovery_section' not in text and '$app_store_url' not in text,f'{path}: unrendered template')
        for im in p.tags['img']:
            check('alt' in im,f'{path}: image is missing alt: {im.get("src")}')
            check(str(im.get('width','')).isdigit() and str(im.get('height','')).isdigit(),f'{path}: image missing dimensions: {im.get("src")}')
        robots=','.join(p.meta('robots'))
        if not entry['indexable']:
            check('noindex' in robots,f'{path}: utility page is not noindex')
            check(p.meta('referrer')==['no-referrer'],f'{path}: invite/404 referrer policy is not private')
            continue
        check('noindex' not in robots,f'{path}: accidentally noindexed')
        titles[p.title].append(path);descs[p.meta('description')[0]].append(path)
        if not 25<=len(p.title)<=72:warnings.append(f'{path}: review title length ({len(p.title)} characters); not a ranking rule')
        if not 105<=len(p.meta('description')[0])<=175:warnings.append(f'{path}: review description length ({len(p.meta("description")[0])}); not a ranking rule')
        canon=[x['href'] for x in p.tags['link'] if x.get('rel')=='canonical']
        check(canon==[base+path],f'{path}: wrong canonical: {canon}')
        check(p.meta('og:url',True)==[base+path],f'{path}: wrong og:url')
        for key in ['og:title','og:description','og:image','og:image:width','og:image:height','og:image:alt']:
            check(len(p.meta(key,True))==1,f'{path}: missing {key}')
        check(p.meta('twitter:card')==['summary_large_image'],f'{path}: missing social card')
        check(p.meta('apple-itunes-app')==['app-id=719622441'],f'{path}: incorrect Smart App Banner ID')
        ld=[x for x in p.scripts if x['type']=='application/ld+json'];check(len(ld)==1,f'{path}: expected one JSON-LD graph')
        for script in ld:
            try:
                graph=json.loads(script['text']);nodes=graph['@graph'];ids=[x['@id'] for x in nodes if '@id'in x]
                check(graph['@context']=='https://schema.org',f'{path}: bad JSON-LD context')
                check(len(ids)==len(set(ids)),f'{path}: duplicate JSON-LD node IDs')
                check(any(x.get('@type')=='WebSite' for x in nodes),f'{path}: no WebSite entity')
                if path!='/':check(any(x.get('@type')=='BreadcrumbList' for x in nodes),f'{path}: no breadcrumbs')
                serialized=json.dumps(graph)
                check('aggregateRating' not in serialized and '"review"' not in serialized,f'{path}: rating/review markup needs independent review')
                if path=='/':
                    app=next(x for x in nodes if x.get('@type')=='MobileApplication')
                    check(app.get('name')=='ReadyKin' and app.get('alternateName')=='Before Leaving',f'{path}: disconnected app identity')
                    check(app.get('identifier')=='719622441',f'{path}: wrong app ID')
                if path=='/faq.html':
                    faqs=json.loads((ROOT/'site-src/data/faqs.json').read_text())
                    node=next(x for x in nodes if x.get('@type')=='FAQPage')
                    visible=' '.join(' '.join(p.text).split())
                    check(len(node['mainEntity'])==len(faqs),f'{path}: FAQ schema count differs')
                    for question in node['mainEntity']:
                        check(question['name'] in visible and question['acceptedAnswer']['text'] in visible,f'{path}: FAQ schema does not match visible answers')
            except (ValueError,KeyError,StopIteration,TypeError) as error:check(False,f'{path}: invalid JSON-LD: {error}')
    for title,paths in titles.items():check(len(paths)==1,f'Duplicate title on {paths}')
    for desc,paths in descs.items():check(len(paths)==1,f'Duplicate description on {paths}')
    for path,p in pages.items():
        for tag,attr in [('a','href'),('link','href'),('img','src'),('script','src')]:
            for el in p.tags[tag]:
                value=el.get(attr,'')
                if not value or value.startswith(('mailto:','tel:','beforeleaving:','data:')):continue
                u=urlsplit(urljoin(base+path,value))
                if u.netloc!=urlsplit(base).netloc:continue
                target_path=unquote(u.path)
                target_file=target_path.lstrip('/')
                if not target_file or target_path.endswith('/'):target_file+='index.html'
                target=ROOT/target_file
                check(target.is_file(),f'{path}: broken local {attr}: {value}')
                if tag=='a' and u.path!=path:incoming[u.path]+=1
                if u.fragment and u.path in pages:check(unquote(u.fragment) in pages[u.path].ids,f'{path}: broken anchor: {value}')
        for social in p.meta('og:image',True):check((ROOT/urlsplit(social).path.lstrip('/')).is_file(),f'{path}: missing social image')
    expected={base+p for p,v in manifest['pages'].items() if v['indexable']}
    root=ET.parse(ROOT/'sitemap.xml');actual=[x.text for x in root.findall('.//{*}loc')]
    check(set(actual)==expected,'Sitemap does not match indexable page inventory')
    check(len(actual)==len(set(actual)),'Sitemap has duplicate URLs')
    for t in root.findall('.//{*}lastmod'):
        try:date.fromisoformat(t.text)
        except ValueError:check(False,'Invalid sitemap lastmod')
    robot=RobotFileParser();robot.parse((ROOT/'robots.txt').read_text().splitlines())
    for url in expected:
        for bot in ['OAI-SearchBot','Googlebot','bingbot']:check(robot.can_fetch(bot,url),f'{bot} blocked from {url}')
    for path,v in manifest['pages'].items():
        if v['indexable'] and path!='/':check(incoming[path]>0,f'Orphan page: {path}')
    for name,digest in json.loads((ROOT/'tests/protected-files.json').read_text()).items():
        check(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,f'Protected integration file changed: {name}')
    cfg=json.loads((ROOT/'site-src/data/site.json').read_text())
    check((ROOT/manifest['indexnow_key_file']).read_text()==cfg['indexnow_key'],'IndexNow key mismatch')
    if manifest.get('verification_file'):
        f=manifest['verification_file'];check((ROOT/f).read_text()=='google-site-verification: '+f,'Google verification file format mismatch')
    check('beforeleaving://travel/join/' in (ROOT/'join.html').read_text(),'Travel URL scheme changed')
    check('beforeleaving://join/' in (ROOT/'join.html').read_text(),'Group URL scheme changed')
    if (ROOT/'dist').exists():
        for name in ['site-src','docs','scripts','tests','reports','.git','.github']:
            check(not (ROOT/'dist'/name).exists(),f'Private build material staged: {name}')
        check((ROOT/'dist/.well-known/apple-app-site-association').exists(),'Apple association file missing from dist')
    result={'status':'passed' if not errors else 'failed','checks':checks,'html_pages':len(pages),'indexable_pages':len(expected),'errors':errors,'warnings':warnings,'scope':'Local static checks only; does not assert indexing, rich-result eligibility, ranking, production availability, legal compliance or app feature verification.'}
    report=ROOT/args.report;report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));sys.exit(bool(errors))
if __name__=='__main__':main()
