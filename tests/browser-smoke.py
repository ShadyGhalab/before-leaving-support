#!/usr/bin/env python3
"""Exercise staged ReadyKin pages with Chromium. Start scripts/serve.py first.
Install optional test dependency: python -m pip install -r tests/requirements.txt
Then: python -m playwright install chromium
"""
from __future__ import annotations
import argparse,asyncio,json,shutil,base64,mimetypes,re,os
from urllib.parse import urlsplit
from urllib.request import urlopen
from urllib.error import HTTPError
from types import SimpleNamespace
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]

async def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--base-url',default='http://127.0.0.1:8765');ap.add_argument('--full',action='store_true');ap.add_argument('--offline-render',action='store_true',help='Render local served HTML using set_content when browser navigation is restricted. URL reads are fixture-injected; HTTP is checked separately.');args=ap.parse_args()
    manifest=json.loads((ROOT/'site-src/data/build-manifest.json').read_text());results=[];failures=[];captures=ROOT/'reports/previews';captures.mkdir(parents=True,exist_ok=True)
    async def load(page, path):
        if not args.offline_render:
            return await page.goto(args.base_url+path, wait_until='networkidle')
        # Only read the user's own local preview server, never arbitrary external pages.
        if urlsplit(args.base_url).hostname not in ['127.0.0.1','localhost']:
            raise ValueError('Offline rendering is restricted to the local preview server')
        try:
            with urlopen(args.base_url+path, timeout=10) as response:
                status=response.status; html=response.read().decode('utf-8')
        except HTTPError as error:
            status=error.code;html=error.read().decode('utf-8')
        def css(match):
            file=ROOT/'dist'/match.group(1).lstrip('/')
            return '<style>'+file.read_text()+'</style>'
        html=re.sub(r'<link[^>]*href="(/[^"?]+\.css)"[^>]*>',css,html)
        deferred_scripts=[]
        def script(match):
            file=ROOT/'dist'/match.group(1).lstrip('/')
            deferred_scripts.append(file.read_text())
            return ''
        html=re.sub(r'<script[^>]*src="(/[^"?]+\.js)"[^>]*></script>',script,html)
        # External defer scripts execute after parsing in production. Keep that order here.
        html=html.replace('</body>', '<script>'+ '\n'.join(deferred_scripts) +'</script></body>')
        def bitmap(match):
            tag=match.group(0);src=re.search(r'src="([^"]+)"',tag)
            if src and src.group(1).startswith('/'):
                file=ROOT/'dist'/src.group(1).lstrip('/')
                mime=mimetypes.guess_type(file)[0] or 'application/octet-stream'
                data='data:'+mime+';base64,'+base64.b64encode(file.read_bytes()).decode()
                tag=tag.replace(src.group(0),'src="'+data+'"')
            return tag
        html=re.sub(r'<img\b[^>]*>',bitmap,html)
        # Fixture-inject location reads; do not alter production files or browser policies.
        html=html.replace('window.location.search',json.dumps(('?'+urlsplit(path).query) if urlsplit(path).query else ''))
        html=html.replace('window.location.pathname',json.dumps(urlsplit(path).path))
        html=html.replace('window.location.replace(', 'window.__recordReadyKinRedirect(')
        html=html.replace('<head>','<head><script>window.__readykinRedirect=null;window.__recordReadyKinRedirect=u=>window.__readykinRedirect=u;</script>',1)
        # Favicon links are metadata; inline them too to avoid unnecessary browser fetches.
        html=re.sub(r'<link[^>]*rel="(?:icon|apple-touch-icon)"[^>]*>','',html)
        await page.set_content(html,wait_until='load')
        redirect=await page.evaluate('window.__readykinRedirect')
        if redirect:
            return await load(page,redirect)
        return SimpleNamespace(status=status)

    async with async_playwright() as pw:
        options={'headless':True,'args':['--disable-dev-shm-usage']}
        if hasattr(os,'geteuid') and os.geteuid()==0:options['args'].append('--no-sandbox')
        if shutil.which('chromium'):options['executable_path']=shutil.which('chromium')
        browser=await pw.chromium.launch(**options)
        widths=[320,390,768,1366] if args.full else [390,1366]
        for width in widths:
            ctx=await browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1,reduced_motion='reduce')
            page=await ctx.new_page();errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            for path,entry in manifest['pages'].items():
                errors.clear();response=await load(page,path)
                # Load lazy images for an asset-health check, not a performance measurement.
                await page.evaluate("document.querySelectorAll('img').forEach(i => i.loading='eager')")
                await page.evaluate("Promise.all([...document.images].map(i => i.decode().catch(() => {})))")
                print(f'Checked {width}px {path}', flush=True)
                stats=await page.evaluate('''() => ({
                  overflow:document.documentElement.scrollWidth > innerWidth + 1,
                  missingImages:[...document.images].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.getAttribute('src')),
                  main:!!document.querySelector('main'),
                  h1:[...document.querySelectorAll('h1')].filter(h=>getComputedStyle(h).display!=='none' && h.getBoundingClientRect().width>0).length,
                  clippedText:[...document.querySelectorAll('main h1,main h2,main p')].filter(el=>!el.closest('.story-track') && !el.closest('details:not([open])') && el.getBoundingClientRect().width>0 && (el.getBoundingClientRect().right>innerWidth+2 || el.getBoundingClientRect().left < -2)).map(el=>el.textContent.trim().slice(0,80))
                })''')
                passed=response.status==200 and not errors and not stats['overflow'] and not stats['missingImages'] and stats['main'] and not stats['clippedText']
                row={'path':path,'width':width,'passed':passed,'status':response.status,'page_errors':list(errors),**stats};results.append(row)
                if not passed:failures.append(row)
                (ROOT/'reports/browser-page-checks.json').write_text(json.dumps({'status':'partial until browser-validation.json completes','results':results,'failures':failures},indent=2)+'\n')
                capture_key=(path,width)
                keys={('/',1366):'homepage-desktop',('/packing-list-app/',1366):'packing-desktop',('/packing-list-app/',390):'packing-mobile',('/guides/weekend-trip-packing-checklist/',390):'checklist-mobile'}
                if capture_key in keys:await page.screenshot(path=str(captures/(keys[capture_key]+'.png')),full_page=True)
            await ctx.close()
        # The mobile disclosure must be operable by keyboard and hide inactive links from focus.
        ctx=await browser.new_context(viewport={'width':390,'height':844},reduced_motion='reduce');page=await ctx.new_page()
        await load(page,'/packing-list-app/')
        await page.locator('#menuButton').click();assert await page.locator('#navLinks').is_visible()
        await page.keyboard.press('Tab');assert await page.locator('#navLinks a').first.evaluate('(a)=>a===document.activeElement')
        await page.keyboard.press('Escape');assert not await page.locator('#navLinks').is_visible()
        assert await page.locator('#menuButton').evaluate('(b)=>b===document.activeElement')
        results.append({'test':'mobile menu, keyboard focus and Escape','passed':True})
        # Clipboard fallback is intentional and does not require permissive browser settings.
        await load(page,'/guides/weekend-trip-packing-checklist/')
        await page.locator('input[type=checkbox]').first.check()
        assert (await page.locator('[data-progress]').inner_text()).startswith('1 of')
        await page.evaluate("Object.defineProperty(navigator, 'clipboard', {configurable:true, value:{writeText:()=>Promise.reject(new Error('blocked'))}})")
        await page.locator('[data-copy-list]').click();assert await page.locator('[data-copy-fallback]').is_visible()
        assert '[x]' in await page.locator('[data-copy-fallback]').input_value()
        await page.locator('[data-reset-list]').click();assert (await page.locator('[data-progress]').inner_text()).startswith('0 of')
        await page.evaluate('window.print=()=>{window.__printCalled=true}')
        await page.locator('[data-print-list]').click();assert await page.evaluate('window.__printCalled')
        await page.emulate_media(media='print');assert not await page.locator('.checklist-toolbar').is_visible()
        await page.emulate_media(media='screen')
        results.append({'test':'checklist progress, copy fallback, reset and print CSS','passed':True})
        # Externally supplied invite paths retain their exact native URL scheme.
        for path,expected in [('/travel/join/Ab12','beforeleaving://travel/join/AB12'),('/join/Ab12','beforeleaving://join/AB12')]:
            await load(page,path)

            if not args.offline_render:await page.wait_for_url('**/join.html?**')
            assert await page.locator('#open-app-button').get_attribute('href')==expected
            assert 'noindex' in await page.locator('meta[name=robots]').get_attribute('content')
        await load(page,'/join.html');assert await page.locator('#invalid-invite').is_visible()
        missing=await load(page,'/this-page-does-not-exist');assert missing.status==404
        results.append({'test':'group/trip invite fallbacks, invalid invite and genuine HTTP 404','passed':True})
        # Local attribution hook: no query text, email or invite code enters the payload.
        await load(page,'/?utm_source=chatgpt.com&private=do-not-collect')
        await page.evaluate("window.addEventListener('readykin:app-store-click',e=>window.__outbound=e.detail);document.addEventListener('click',e=>{if(e.target.closest('a[data-cta]'))e.preventDefault()},true)")
        await page.locator('a[data-cta]:visible').first.click()
        payload=await page.evaluate('window.__outbound');assert payload['source']=='chatgpt' and payload['page']=='/' and 'do-not-collect' not in json.dumps(payload)
        if not args.offline_render:
            assert await page.evaluate('localStorage.length===0 && sessionStorage.length===0 && document.cookie===\'\'')
        else:
            assert not await ctx.cookies()
            assert not re.search(r'\b(?:localStorage|sessionStorage)\b|document\.cookie\s*=', (ROOT/'discovery.js').read_text())
        results.append({'test':'source classification and non-persistent local event payload','passed':True})
        await ctx.close()
        # JavaScript-disabled content must remain visible, including links on small screens.
        ctx=await browser.new_context(viewport={'width':320,'height':900},java_script_enabled=False)
        page=await ctx.new_page()
        for path in ['/','/packing-list-app/','/faq.html','/guides/weekend-trip-packing-checklist/']:
            await load(page,path)
            assert await page.locator('main h1').is_visible()
            assert await page.locator('#navLinks').is_visible()
            assert await page.locator('main').inner_text()
        results.append({'test':'JavaScript-disabled mobile content and navigation','passed':True})
        await ctx.close();await browser.close()
    report={'mode':'offline-render-with-local-http-and-url-fixtures' if args.offline_render else 'browser-http-navigation','status':'passed' if not failures else 'failed','page_viewport_runs':len(manifest['pages'])*len(widths),'additional_scenarios':len(results)-len(manifest['pages'])*len(widths),'results':results,'failures':failures,'scope':'Local Chromium only; not Safari/native-device certification, an accessibility certification, a Lighthouse score, or proof of indexing.'}
    (ROOT/'reports/browser-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
    if failures:raise SystemExit(1)
if __name__=='__main__':asyncio.run(main())
