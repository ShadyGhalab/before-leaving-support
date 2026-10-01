#!/usr/bin/env python3
"""Build ReadyKin's static pages and search metadata using only the Python standard library.

Generated HTML is checked into the repository so existing branch-based hosting still works.
For a clean deployment artifact run stage-site.py after this command. Source files live under
site-src/. No credentials, analytics network calls or backend are required for this build.
"""
from __future__ import annotations
import argparse
from datetime import date
from html import escape
import hashlib
import json
from pathlib import Path
import re
from string import Template
from urllib.parse import urlencode, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'site-src/data'
TEMPLATES = ROOT / 'site-src/templates'
CONFIG = json.loads((DATA / 'site.json').read_text(encoding='utf-8'))
PAGES = json.loads((DATA / 'landing-pages.json').read_text(encoding='utf-8'))
GUIDES = json.loads((DATA / 'guides.json').read_text(encoding='utf-8'))
FAQS = json.loads((DATA / 'faqs.json').read_text(encoding='utf-8'))
IMAGES = json.loads((DATA / 'images.json').read_text(encoding='utf-8'))
BASE = CONFIG['site_url'].rstrip('/')
INDEX: dict[str, dict] = {}
BY_SLUG = {p['slug']: p for p in PAGES}


def e(value: object) -> str:
    return escape(str(value), quote=True)


def json_script(value: dict) -> str:
    # Safe even if future editorial content contains closing script sequences.
    return json.dumps(value, ensure_ascii=False, indent=2).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


def app_url(campaign: str = 'website') -> str:
    """Apple campaign provider token must come from the owner's App Store Connect account."""
    token = CONFIG.get('app_store_provider_token')
    if not token:
        return CONFIG['app_store_url']
    if not re.fullmatch(r'\d+', str(token)):
        raise ValueError('app_store_provider_token must be the numeric token from App Store Connect, or null')
    campaign = re.sub(r'[^a-zA-Z0-9_-]', '-', campaign)[:32]
    return CONFIG['app_store_url'] + '?' + urlencode({'pt': str(token), 'ct': 'readykin-' + campaign, 'mt': '8'})


def image(src: str, alt: str, *, eager: bool = False, css: str = '', hidden: bool = False) -> str:
    dim = IMAGES.get(src)
    if not dim:
        raise ValueError(f'Image dimensions missing from site-src/data/images.json: {src}')
    attrs = f' class="{e(css)}"' if css else ''
    priority = ' fetchpriority="high"' if eager else ''
    accessibility = ' aria-hidden="true"' if hidden else ''
    return f'<img src="{e(src)}" alt="{e(alt)}" width="{dim["width"]}" height="{dim["height"]}" loading="{"eager" if eager else "lazy"}" decoding="async"{priority}{accessibility}{attrs}>'


def button(placement: str = 'hero', label: str = 'View ReadyKin on the App Store', campaign: str = 'website') -> str:
    return f'<a class="app-store-button" href="{e(app_url(campaign))}" data-cta="{e(placement)}">{e(label)} <span aria-hidden="true">↗</span></a>'


def nav() -> str:
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<nav class="site-nav" id="siteNav" aria-label="Primary navigation"><div class="nav-inner">
<a class="brand" href="/" aria-label="ReadyKin home">{image('/images/readykin/brand-icon-88.webp','ReadyKin app icon',css='brand-icon',hidden=True)}<span>ReadyKin</span></a>
<button class="menu-button" type="button" id="menuButton" aria-label="Open menu" aria-controls="navLinks" aria-expanded="false"><span></span><span></span><span></span></button>
<div class="nav-links" id="navLinks"><a href="/features/">Features</a><a href="/guides/">Checklists</a><a href="/faq.html">Help &amp; FAQ</a><a href="/about/">About</a></div>
<a class="app-store-button nav-cta" href="{e(app_url())}" data-cta="navigation">App Store <span aria-hidden="true">↗</span></a>
</div></nav>'''


def footer() -> str:
    return f'''<footer class="site-footer"><div class="footer-inner">
<div class="footer-brand-row"><a class="brand footer-brand" href="/">{image('/images/readykin/brand-icon-88.webp','ReadyKin app icon',css='brand-icon',hidden=True)}<span>ReadyKin</span></a><p>Formerly Before Leaving. A little more ready for your day.</p></div>
<div class="footer-directory"><div><h2>Prepare</h2><a href="/packing-list-app/">Packing lists</a><a href="/ai-packing-list/">AI packing ideas</a><a href="/weather-packing-list/">Weather-aware suggestions</a><a href="/before-leaving-checklist/">Before-leaving checklists</a></div>
<div><h2>Plan together</h2><a href="/family-packing-list/">Family packing</a><a href="/shared-travel-checklist/">Shared travel checklists</a><a href="/location-reminders/">Location reminders</a><a href="/apple-watch-reminders/">Apple Watch reminders</a></div>
<div><h2>Explore</h2><a href="/guides/">Practical checklists</a><a href="/features/">All features</a><a href="/about/">About ReadyKin</a><a href="/press.html">Press kit</a></div>
<div><h2>Support</h2><a href="/faq.html">Help &amp; FAQ</a><a href="/changelog.html">Release notes</a><a href="mailto:{e(CONFIG['support_email'])}">Email support</a><a href="/site-map/">Site map</a></div></div>
<div class="footer-links-row"><div class="footer-links"><a href="/privacy.html">Privacy policy</a><a href="/terms.html">Terms of service</a></div><p>© 2026 {e(CONFIG['developer'])}. All rights reserved.</p></div>
</div></footer>'''


def crumbs(path: str, label: str, parent: tuple[str,str] | None = None) -> tuple[str,list[dict]]:
    items = [('/', 'Home')]
    if parent:
        items.append(parent)
    items.append((path,label))
    parts = []
    for i, (p, t) in enumerate(items):
        if i == len(items) - 1:
            content = '<span aria-current="page">' + e(t) + '</span>'
        else:
            content = '<a href="' + e(p) + '">' + e(t) + '</a>'
        parts.append('<li>' + content + '</li>')
    visible = '<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>' + ''.join(parts) + '</ol></nav>'
    schema = [{'@type':'ListItem','position':i+1,'name':t,'item':BASE+p} for i,(p,t) in enumerate(items)]
    return visible,schema


def head(path: str, title: str, description: str, breadcrumb: list[dict] | None = None,
         extra: list[dict] | None = None, *, noindex: bool = False, page_type: str = 'WebPage', homepage: bool = False) -> str:
    canonical = BASE + path
    graph = [
        {'@type':'WebSite','@id':BASE+'/#website','name':CONFIG['name'],'alternateName':CONFIG['alternate_name'],'url':BASE+'/', 'inLanguage':'en'},
        {'@type':page_type,'@id':canonical+'#webpage','url':canonical,'name':title,'description':description,'inLanguage':'en','isPartOf':{'@id':BASE+'/#website'},'about':{'@id':BASE+'/#app'}}
    ]
    if homepage:
        graph += [
            {'@type':'Person','@id':BASE+'/#developer','name':CONFIG['developer'],'url':BASE+'/about/'},
            {'@type':'MobileApplication','@id':BASE+'/#app','name':CONFIG['name'],'alternateName':CONFIG['alternate_name'],
             'url':BASE+'/', 'installUrl':CONFIG['app_store_url'],'identifier':CONFIG['app_store_id'],
             'applicationCategory':CONFIG['category'],'operatingSystem':CONFIG['operating_systems'],
             'description':CONFIG['description'],'image':BASE+'/images/readykin/brand-icon.png',
             'screenshot':[BASE+'/images/readykin/story-travel.webp',BASE+'/images/readykin/story-location.webp'],
             'author':{'@id':BASE+'/#developer'},'featureList':CONFIG['features'],
             'sameAs':[CONFIG['app_store_url']], 'softwareHelp':{'@id':BASE+'/faq.html#webpage'}}
        ]
    if breadcrumb:
        bid = canonical+'#breadcrumb'
        graph[1]['breadcrumb']={'@id':bid}
        graph.append({'@type':'BreadcrumbList','@id':bid,'itemListElement':breadcrumb})
    if extra:
        graph.extend(extra)
    robots='noindex, follow' if noindex else 'index, follow, max-image-preview:large'
    verify=''
    if path == '/':
        for key,name in [('google_verification_meta','google-site-verification'),('bing_verification_meta','msvalidate.01')]:
            if CONFIG.get(key):verify += f'<meta name="{name}" content="{e(CONFIG[key])}">\n'
    social = BASE+'/images/social/readykin-social.jpg'
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#2d1736">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="apple-itunes-app" content="app-id={e(CONFIG['app_store_id'])}">
<link rel="canonical" href="{e(canonical)}">
<link rel="icon" type="image/png" href="/favicon.png" sizes="64x64">
<link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180">
<meta property="og:type" content="website">
<meta property="og:site_name" content="ReadyKin">
<meta property="og:locale" content="en_US">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:image" content="{social}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:alt" content="ReadyKin, formerly Before Leaving — reminders, packing lists and shared trips">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(description)}">
<meta name="twitter:image" content="{social}">
<meta name="twitter:image:alt" content="ReadyKin — reminders, packing lists and shared trips">
{verify}<link rel="stylesheet" href="/readykin.css">
<link rel="stylesheet" href="/discovery.css">
<script type="application/ld+json">{json_script({'@context':'https://schema.org','@graph':graph})}</script>
<script src="/readykin.js" defer></script>
<script src="/discovery.js" defer></script>'''


def save_page(path: str, title: str, description: str, body: str, *, breadcrumb=None, extra=None, page_type='WebPage', homepage=False, noindex=False) -> None:
    html=f'''<!DOCTYPE html>
<html lang="en"><head>
{head(path,title,description,breadcrumb,extra,noindex=noindex,page_type=page_type,homepage=homepage)}
</head><body data-page="{e(path)}">
{nav()}
{body}
{footer()}
</body></html>\n'''
    file = 'index.html' if path=='/' else path.lstrip('/')+('index.html' if path.endswith('/') else '')
    target = ROOT/file;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(html,encoding='utf-8')
    INDEX[path]={'file':file,'title':title,'indexable':not noindex,'sha256':hashlib.sha256(html.encode()).hexdigest()}


def intro(path: str, title: str, lede: str, label: str, *, kicker: str = 'ReadyKin', parent=None) -> tuple[str,list[dict]]:
    breadcrumb, schema = crumbs(path,label,parent)
    return f'<header class="content-hero section-shell">{breadcrumb}<p class="section-kicker">{e(kicker)}</p><h1>{e(title)}</h1><p class="page-lede">{e(lede)}</p></header>',schema


def page_cards(slugs: list[str] | None = None) -> str:
    selected = [BY_SLUG[s] for s in slugs] if slugs else PAGES
    return '<div class="topic-grid">'+''.join(
        f'<a class="topic-card" href="/{p["slug"]}/"><span class="topic-kicker">{e(p["kicker"])}</span><h3>{e(p["title"].split(" | ")[0])}</h3><p>{e(p["lede"])}</p><span class="topic-arrow" aria-hidden="true">↗</span></a>' for p in selected)+'</div>'


def faq_html(faqs: list[dict]) -> str:
    return '<div class="faq-list">'+''.join(f'<details><summary>{e(q["question"])}</summary><p>{e(q["answer"])}</p></details>' for q in faqs)+'</div>'


def closing(campaign='website') -> str:
    return f'''<section class="section-shell ending-cta"><div class="cta-panel"><div><p class="section-kicker light">Make the next step easier</p><h2>A little more ready.</h2><p>Choose the reminders and lists that fit your day.</p></div><div>{button('closing',campaign=campaign)}<p class="cta-note">Pricing, purchases and compatibility are listed in the App Store.</p></div></div></section>'''


def build_home() -> None:
    topics=f'<section class="section-shell topic-section" id="explore"><div class="section-heading"><p class="section-kicker">Find your starting point</p><h2>What are you getting ready for?</h2><p>Practical ways to use ReadyKin, with examples and the details that matter.</p></div>{page_cards()}<p class="reading-link"><a href="/guides/">Try a practical packing or leaving-home checklist <span aria-hidden="true">→</span></a></p></section>'
    html=Template((TEMPLATES/'home.html').read_text(encoding='utf-8')).substitute(discovery_section=topics,app_store_url=e(app_url('homepage')))
    # Width/height in original template reserve the correct aspect ratio for optimized assets.
    html=html.replace('src="/images/readykin/brand-icon-220.webp"', 'src="/images/readykin/brand-icon-220.webp"')
    save_page('/', 'ReadyKin | Smart Reminders, Packing Lists & Shared Trips',
        'ReadyKin, formerly Before Leaving, helps you plan packing lists, share trips and set time or location reminders. Get ready for everyday life on iPhone.', html, homepage=True)


def build_landing_pages() -> None:
    for p in PAGES:
        path='/'+p['slug']+'/'
        breadcrumb,bcs=crumbs(path,p['title'].split(' | ')[0],('/features/','Features'))
        steps='<ol class="how-steps">'+''.join(f'<li><span class="step-number" aria-hidden="true">0{i+1}</span><div><h3>{e(t)}</h3><p>{e(d)}</p></div></li>' for i,(t,d) in enumerate(p['steps']))+'</ol>'
        sections=''.join(f'<section class="prose-block"><h2>{e(title)}</h2>'+''.join(f'<p>{e(t)}</p>' for t in paras)+'</section>' for title,paras in p['sections'])
        ex=p['example']
        example=f'<aside class="example-panel" aria-labelledby="example-heading"><p class="section-kicker">A practical starting point</p><h2 id="example-heading">{e(ex["title"])}</h2><p>{e(ex["text"])}</p><ul>'+''.join(f'<li>{e(x)}</li>' for x in ex['items'])+'</ul></aside>'
        limits='<aside class="expectations"><h2>Good to know</h2><ul>'+''.join(f'<li>{e(t)}</li>' for t in p['limitations'])+'</ul></aside>'
        body=f'''<main id="main"><header class="landing-hero section-shell">{breadcrumb}<div class="landing-grid"><div class="landing-copy"><p class="section-kicker">{e(p['kicker'])}</p><h1>{e(p['h1'])}</h1><p class="page-lede">{e(p['lede'])}</p><div class="landing-actions">{button('feature-hero',campaign=p['slug'])}<a class="text-link" href="#how-it-works">See how it works <span aria-hidden="true">↓</span></a></div><p class="small-note">ReadyKin · formerly Before Leaving</p></div><figure class="landing-visual">{image(p['image'],p['alt'],eager=True)}<figcaption>ReadyKin app preview. Screens and options may vary by version.</figcaption></figure></div></header>
<section class="section-shell answer-section"><div class="answer-box"><h2>What can you do with ReadyKin?</h2><p>{e(p['intro'])}</p></div></section>
<section class="section-shell article-layout"><div class="article-column"><section id="how-it-works" class="prose-block"><p class="section-kicker">From idea to action</p><h2>Make it part of your routine.</h2>{steps}</section>{sections}{limits}</div>{example}</section>
<section class="section-shell landing-faq"><h2>Your questions, answered.</h2>{faq_html(p['faqs'])}</section>
<section class="section-shell topic-section"><p class="section-kicker">Keep preparing</p><h2>There is a little more to explore.</h2>{page_cards(p['related'])}</section>{closing(p['slug'])}</main>'''
        save_page(path,p['title'],p['description'],body,breadcrumb=bcs)


def build_hubs() -> None:
    header,bc=intro('/features/','A clearer plan, whatever is next.','Explore ReadyKin’s reminders, packing lists, shared trips and preparation tools. Find a workflow, see an example and check the details before you start.','Features',kicker='Find your starting point')
    body=f'<main id="main">{header}<section class="section-shell topic-section hub-topics"><h2>Choose what you are preparing for.</h2>{page_cards()}</section><section class="section-shell prose-block"><h2>And the everyday care around it.</h2><p>ReadyKin also includes tools for errands, pet care and plant routines. Keep the daily tasks around your plans visible, and review the features available in your app version.</p><p><a href="/faq.html">Read the help and compatibility FAQ</a> or <a href="/about/">learn about ReadyKin, formerly Before Leaving</a>.</p></section>{closing()}</main>'
    save_page('/features/','ReadyKin Features | Reminders, Packing & Shared Planning','Explore ReadyKin features for smart reminders, packing lists, shared trips, location alerts and everyday preparation. Find the workflow that fits your day.',body,breadcrumb=bc,page_type='CollectionPage')
    header,bc=intro('/guides/','Small checklists. Less to keep in your head.','Practical examples you can check in your browser, copy or print. No account needed. Adapt them to your day, then build your own routine in ReadyKin.','Checklists',kicker='ReadyKin guides')
    cards='<div class="topic-grid guide-grid">'+''.join(f'<a class="topic-card" href="/guides/{g["slug"]}/"><span class="topic-kicker">Practical checklist</span><h2>{e(g["h1"])}</h2><p>{e(g["description"])}</p><span class="topic-arrow" aria-hidden="true">↗</span></a>' for g in GUIDES)+'</div>'
    save_page('/guides/','Practical Packing & Leaving-Home Checklists | ReadyKin','Find practical packing and leaving-home checklists from ReadyKin. Check items in your browser, copy a list or print it, then adapt it to your own routine.',f'<main id="main">{header}<section class="section-shell topic-section hub-topics"><h2>Try a checklist.</h2>{cards}</section>{closing()}</main>',breadcrumb=bc,page_type='CollectionPage')


def build_guides() -> None:
    for g in GUIDES:
        path='/guides/'+g['slug']+'/'
        header,bc=intro(path,g['h1'],g['description'],g['title'].split(' | ')[0],kicker='A practical ReadyKin guide',parent=('/guides/','Checklists'))
        groups=[];n=0
        for title,items in g['sections']:
            lis=[]
            for item in items:
                n+=1;lis.append(f'<li><label><input type="checkbox" name="item-{n}" value="{e(item)}"><span>{e(item)}</span></label></li>')
            groups.append(f'<fieldset><legend>{e(title)}</legend><ul class="interactive-list">{"".join(lis)}</ul></fieldset>')
        prose=''.join(f'<section class="prose-block"><h2>{e(t)}</h2><p>{e(d)}</p></section>' for t,d in g['paragraphs'])
        body=f'''<main id="main">{header}<article class="section-shell guide-article"><p class="guide-intro">{e(g['intro'])}</p>
<section class="browser-checklist" data-checklist data-checklist-title="{e(g['title'].split(' | ')[0])}"><h2>Your starting list</h2><p class="checklist-disclosure">This browser checklist is separate from the app. Checks last only while this page stays open; nothing is saved to ReadyKin or sent to a server.</p><div class="checklist-toolbar" hidden><p data-progress aria-live="polite">0 of {n} checked</p><div><button type="button" class="secondary-button" data-copy-list>Copy list</button><button type="button" class="secondary-button" data-print-list>Print</button><button type="button" class="text-button" data-reset-list>Reset checks</button></div></div><div class="checklist-groups">{''.join(groups)}</div><p data-copy-status class="small-note" role="status"></p><textarea data-copy-fallback hidden aria-label="Checklist text — select and copy" rows="12" readonly></textarea></section>{prose}<section class="prose-block"><h2>Make the list part of your routine.</h2><p>Use this example as a starting point, then create the reminders or packing list you need in ReadyKin. The buttons above copy or print the website checklist; they do not import it automatically into the app.</p>{button('guide',campaign=g['slug'])}</section></article><section class="section-shell topic-section"><h2>Find the right tool for the next step.</h2>{page_cards(g['related'])}</section></main>'''
        save_page(path,g['title'],g['description'],body,breadcrumb=bc)


def build_faq() -> None:
    header,bc=intro('/faq.html','A little help, when you need it.','Answers about reminders, shared packing, compatibility and support. For current prices, available languages and system requirements, check the App Store.','Help & FAQ',kicker='Support')
    cats=list(dict.fromkeys(q['category'] for q in FAQS))
    sections=''.join(f'<section class="faq-group"><h2>{e(c)}</h2>{faq_html([q for q in FAQS if q["category"]==c])}</section>' for c in cats)
    extra=[{'@type':'FAQPage','@id':BASE+'/faq.html#questions','isPartOf':{'@id':BASE+'/faq.html#webpage'},'mainEntity':[{'@type':'Question','name':q['question'],'acceptedAnswer':{'@type':'Answer','text':q['answer']}} for q in FAQS]}]
    body=f'<main id="main">{header}<div class="section-shell faq-document">{sections}<section class="answer-box"><h2>Still need help?</h2><p>Email <a href="mailto:{e(CONFIG["support_email"])}">{e(CONFIG["support_email"])}</a>. Include your device, operating system and app version, plus a description of the problem. Remove private information from screenshots.</p></section></div>{closing()}</main>'
    save_page('/faq.html','ReadyKin Help & FAQ | Reminders, Trips and App Support','Get help with ReadyKin reminders, shared trips, packing lists, device compatibility and data questions. Find clear answers and contact app support.',body,breadcrumb=bc,extra=extra)


def build_about_press() -> None:
    header,bc=intro('/about/','Before Leaving grew into ReadyKin.','The same idea at the heart of a broader app: help people remember, prepare and feel a little more ready for everyday life.','About ReadyKin',kicker='One app. A clearer name.')
    facts=f'<dl class="facts"><div><dt>Current app name</dt><dd>ReadyKin</dd></div><div><dt>Former name</dt><dd>Before Leaving</dd></div><div><dt>Developer</dt><dd>{e(CONFIG["developer"])}</dd></div><div><dt>App Store ID</dt><dd>{e(CONFIG["app_store_id"])}</dd></div><div><dt>Official website</dt><dd>beforeleaving.app</dd></div><div><dt>Support</dt><dd><a href="mailto:{e(CONFIG["support_email"])}">{e(CONFIG["support_email"])}</a></dd></div></dl>'
    body=f'<main id="main">{header}<article class="section-shell prose-document"><section><h2>One product, connected names.</h2><p>ReadyKin is the current name of Before Leaving. The official website continues to use the beforeleaving.app domain, and the App Store app ID remains 719622441. You may still see the former name in older links or coverage.</p><p>ReadyKin brings reminders, packing lists, shared trips and everyday care together. Start with the preparation you need today, whether that is a bag for work, a weekend away or a shared family plan.</p></section>{facts}<section><h2>Choose a practical starting point.</h2><p>Explore the <a href="/features/">feature guides</a>, try a <a href="/guides/">packing or leaving-home checklist</a>, or visit the <a href="/faq.html">FAQ</a> for help. Current compatibility and purchase options are listed in the App Store.</p></section><section><h2>Writing about ReadyKin?</h2><p>The <a href="/press.html">press kit</a> includes the app name, short descriptions, the app icon and supplied screenshots. For questions, contact the developer through the support address above.</p></section>{button("about")}</article>{closing()}</main>'
    save_page('/about/','About ReadyKin | Formerly the Before Leaving App','Learn how ReadyKin connects to its former name, Before Leaving. Find the official app ID, developer details, support contact and practical feature guides.',body,breadcrumb=bc,page_type='AboutPage')
    header,bc=intro('/press.html','Everything you need to introduce ReadyKin.','App facts, a short description and downloadable artwork for editorial coverage. Please use ReadyKin as the current name and Before Leaving as its former name.','Press kit',kicker='For writers and reviewers')
    descriptions=[('One sentence','ReadyKin, formerly Before Leaving, is an iPhone app for reminders, packing lists, shared trips and location-based preparation.'),('Short description','ReadyKin helps people organize what to bring and what to do before everyday departures and trips. The app combines reminders, packing lists, shared planning and an in-app AI assistant, with support across Apple devices. It was previously called Before Leaving. Review current compatibility, purchase options and available features in the App Store.')]
    screenshots=[('story-reminders.webp','Reminders'),('story-travel.webp','Packing lists'),('story-groups.webp','Shared planning'),('story-assistant.webp','AI assistant'),('story-location.webp','Location reminders'),('ipad-ecosystem.webp','Apple devices')]
    assets='<div class="press-assets">'+''.join(f'<article class="press-asset">{image("/images/readykin/"+src,"ReadyKin "+title.lower()+" screenshot")}<h3>{e(title)}</h3><a href="/images/readykin/{src}" download>Download screenshot</a></article>' for src,title in screenshots)+'</div>'
    press=f'<main id="main">{header}<article class="section-shell prose-document wide-document">{facts}<section><h2>Descriptions you can use.</h2>'+''.join(f'<h3>{e(t)}</h3><p>{e(d)}</p>' for t,d in descriptions)+f'</section><section><h2>App icon</h2><div class="press-icon-row">{image("/images/readykin/brand-icon-220.webp","ReadyKin app icon")}<div><p>Use the supplied artwork without changing the app identity.</p><a href="/images/readykin/brand-icon.png" download>Download the 1024 × 1024 PNG app icon</a></div></div></section><section><h2>App screenshots</h2><p>These supplied screenshots illustrate the app experience. Screens and available options can change with releases.</p>{assets}</section><section><h2>Current product details</h2><p>Use the <a href="{e(CONFIG["app_store_url"])}">App Store listing</a> for current pricing, compatibility, language availability and release notes. This kit does not claim awards, ratings, download counts or a published ChatGPT integration.</p><p>For an interview, review question or additional information, contact <a href="mailto:{e(CONFIG["support_email"])}">{e(CONFIG["support_email"])}</a>.</p></section></article>{closing()}</main>'
    save_page('/press.html','ReadyKin Press Kit | App Facts, Icons & Screenshots','Download ReadyKin app artwork and screenshots for editorial coverage. Find official app facts, descriptions, the former Before Leaving name and press contact.',press,breadcrumb=bc)


def build_changelog_legal() -> None:
    header,bc=intro('/changelog.html','The app keeps moving forward.','Check the App Store for the release available to you and its current notes. Older website notes are retained separately as a historical archive.','Release notes',kicker='ReadyKin updates')
    release=CONFIG.get('release')
    live='<section class="answer-box"><h2>Current release</h2><p>The current version and release notes are published in the App Store. A version number is not repeated here until its details have been checked, so an old website entry is not mistaken for the latest update.</p>'+button('release-notes',label='See current App Store release notes')+'</section>'
    if release:
        for k in ['version','date','notes','source_url']:
            if not release.get(k):raise ValueError('A reviewed release requires version, date, notes and source_url')
        date.fromisoformat(release['date'])
        live='<section class="answer-box"><h2>Version '+e(release['version'])+'</h2><p><time datetime="'+e(release['date'])+'">'+e(release['date'])+'</time></p>'+''.join('<p>'+e(n)+'</p>' for n in release['notes'])+'<p><a href="'+e(release['source_url'])+'">Release source</a></p></section>'
    archive=(TEMPLATES/'changelog-archive.html').read_text(encoding='utf-8')
    archive=re.sub(r'<span[^>]*>\s*LATEST\s*</span>','',archive,flags=re.I)
    archive=archive.replace('Initial release of ReadyKin!','Initial release under the former Before Leaving name.')
    archive=archive.replace('class="legal-content"','class="historical-content"')
    # Archive is visible on demand and excluded from snippets; no fresh release dates invented.
    body=f'<main id="main">{header}<article class="section-shell prose-document">{live}<details class="history-archive" data-nosnippet><summary>Historical website notes · 2013–January 2026</summary><p>These are archived entries from the previous website. They are not the current feature, language or system-requirements list. Refer to the App Store for current information.</p>{archive}</details><p>Need help with an update? <a href="/faq.html">Read the FAQ</a> or <a href="mailto:{e(CONFIG["support_email"])}">contact support</a>.</p></article>{closing()}</main>'
    save_page('/changelog.html','ReadyKin Release Notes & Historical Website Updates','Find the current ReadyKin release notes through the App Store and browse clearly labeled historical website updates from the former Before Leaving app.',body,breadcrumb=bc)
    for slug,title,desc in [('privacy','Privacy Policy','Read the ReadyKin privacy policy, including the app’s data handling, third-party services, storage, sharing and available contact and deletion options.'),('terms','Terms of Service','Read the ReadyKin terms of service covering app use, accounts, purchases and responsibilities. Find the official terms and contact information here.')]:
        header,bc=intro('/'+slug+'.html',title,'Official information for the ReadyKin app.',title,kicker='ReadyKin')
        legal=(ROOT/'site-src/legal'/f'{slug}.html').read_text(encoding='utf-8')
        # No substantive legal changes are made by the site build.
        legal=legal.replace('class="legal-content"','class="legal-content section-shell"')
        save_page('/'+slug+'.html',f'{title} | ReadyKin',desc,f'<main id="main">{header}{legal}</main>',breadcrumb=bc)


def build_utility_pages() -> None:
    # Keep existing URL scheme and invitation routing; these are app contracts, not brand copy.
    for name in ['join','404']:
        text=(TEMPLATES/f'{name}-original.html').read_text(encoding='utf-8')
        text=re.sub(r'<link[^>]*href="https://fonts\.(?:googleapis|gstatic)\.com[^>]*>\s*','',text)
        text=text.replace('<head>','<head>\n    <meta name="robots" content="noindex, follow">\n    <meta name="referrer" content="no-referrer">')
        text=text.replace(CONFIG['app_store_url'].replace('/app/id','/app/before-leaving/id'),CONFIG['app_store_url'])
        # Add accessibility and progressive behavior without changing the deep-link logic.
        if name=='join':
            text=text.replace('class="invitation-icon"','class="invitation-icon" width="72" height="72"')
            text=text.replace('<main class="invitation-page">','<main class="invitation-page" id="main">')
            text=text.replace('<div id="valid-invite">','<noscript><p>Enable JavaScript to open this invitation, or ask the sender for the invitation code and enter it in ReadyKin.</p></noscript>\n            <div id="valid-invite">')
            text=text.replace('<h1>Invitation unavailable</h1>','<h2>Invitation unavailable</h2>')
        else:
            text=text.replace('class="nav-icon"','class="nav-icon" width="44" height="44"')
            text=text.replace('<main class="error-page">','<main class="error-page" id="main">')
            text=text.replace('<footer class="footer" style="position: absolute; bottom: 0; width: 100%;">','<footer class="footer">')
            text=text.replace('href="/#contact"','href="mailto:'+CONFIG['support_email']+'"')
        (ROOT/f'{name}.html').write_text(text,encoding='utf-8')
        INDEX[f'/{name}.html']={'file':f'{name}.html','title':'Invitation' if name=='join' else 'Page not found','indexable':False,'sha256':hashlib.sha256(text.encode()).hexdigest()}


def build_site_map() -> None:
    path='/site-map/'
    header,bc=intro(path,'Find your way around ReadyKin.','A simple directory of the app’s feature guides, practical checklists, support information and official pages.','Site map',kicker='Explore the website')
    links=''.join(f'<li><a href="{e(p)}">{e(v["title"])}</a></li>' for p,v in INDEX.items() if v['indexable'])
    save_page(path,'ReadyKin Site Map | Features, Checklists & Support','Browse the ReadyKin website: packing and reminder features, practical checklists, app support, press information, release notes and official legal pages.',f'<main id="main">{header}<section class="section-shell prose-document"><h2>Website pages</h2><ul class="site-map-links">{links}</ul></section></main>',breadcrumb=bc,page_type='CollectionPage')


def build_crawler_files(build_date: str) -> None:
    history_path=DATA/'page-history.json'
    previous=json.loads(history_path.read_text()) if history_path.exists() else {}
    current={};changed=[]
    for path,data in INDEX.items():
        old=previous.get(path,{})
        modified=old.get('lastmod',build_date) if old.get('sha256')==data['sha256'] else build_date
        current[path]={'sha256':data['sha256'],'lastmod':modified}
        if data['indexable'] and old.get('sha256')!=data['sha256']:changed.append(BASE+path)
    history_path.write_text(json.dumps(current,indent=2)+'\n',encoding='utf-8')
    ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    urlset=ET.Element('{http://www.sitemaps.org/schemas/sitemap/0.9}urlset')
    for path,data in INDEX.items():
        if not data['indexable']:continue
        node=ET.SubElement(urlset,'url');ET.SubElement(node,'loc').text=BASE+path;ET.SubElement(node,'lastmod').text=current[path]['lastmod']
    ET.indent(urlset,space='  ')
    (ROOT/'sitemap.xml').write_bytes(ET.tostring(urlset,encoding='utf-8',xml_declaration=True)+b'\n')
    # OAI-specific groups must repeat restrictions: robots groups are not automatically merged.
    excludes=['/site-src/','/scripts/','/tests/','/docs/','/reports/','/.github/','/dist/']
    rules='\n'.join('Disallow: '+x for x in excludes)
    robots=f'''# Public search access. No ranking or recommendation is guaranteed.
# The GPTBot training policy is unchanged from the previously unrestricted site.
# Invitation and 404 pages use noindex; do not block their crawl here.
User-agent: OAI-SearchBot
Allow: /
{rules}

User-agent: *
Allow: /
{rules}

Sitemap: {BASE}/sitemap.xml
'''
    (ROOT/'robots.txt').write_text(robots,encoding='utf-8')
    key=CONFIG['indexnow_key']
    if not re.fullmatch(r'[A-Za-z0-9-]{8,128}',key):raise ValueError('Invalid IndexNow key')
    (ROOT/(key+'.txt')).write_text(key,encoding='utf-8')
    # This is the conventional HTML-file verification format, not an HTML-meta token.
    # The owner must confirm this exact filename still belongs to their Search Console property.
    filename=CONFIG.get('google_verification_file')
    if filename:
        if not re.fullmatch(r'google[a-f0-9]+\.html',filename):raise ValueError('Unexpected Google verification filename')
        (ROOT/filename).write_text('google-site-verification: '+filename,encoding='utf-8')
    (ROOT/'CNAME').write_text(urlsplit(BASE).hostname+'\n',encoding='utf-8')
    manifest={'site_url':BASE,'pages':INDEX,'indexnow_key_file':key+'.txt','verification_file':filename,'changed_urls':changed}
    (DATA/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(f'Built {len(INDEX)} HTML pages ({sum(x["indexable"] for x in INDEX.values())} indexable), sitemap, robots.txt and verification files.')
    print(f'{len(changed)} indexable page(s) changed. No URLs have been submitted and nothing has been deployed.')


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--date',default=date.today().isoformat(),help='Actual content-change date for new/changed pages (YYYY-MM-DD). Unchanged pages retain lastmod.')
    args=ap.parse_args();date.fromisoformat(args.date)
    if not BASE.startswith('https://') or urlsplit(BASE).path:
        raise ValueError('site_url must be an HTTPS origin, without a path')
    build_home();build_landing_pages();build_hubs();build_guides();build_faq();build_about_press();build_changelog_legal();build_utility_pages();build_site_map();build_crawler_files(args.date)

if __name__ == '__main__':
    main()
