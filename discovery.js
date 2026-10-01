/* Optional local interactions. No analytics SDK, cookies, storage or network transmission. */
(() => {
    'use strict';
    document.querySelectorAll('[data-checklist]').forEach(container => {
        const inputs = Array.from(container.querySelectorAll('input[type="checkbox"]'));
        const toolbar = container.querySelector('.checklist-toolbar');
        const progress = container.querySelector('[data-progress]');
        const status = container.querySelector('[data-copy-status]');
        const fallback = container.querySelector('[data-copy-fallback]');
        const update = () => { progress.textContent = `${inputs.filter(i => i.checked).length} of ${inputs.length} checked`; };
        inputs.forEach(input => input.addEventListener('change', update));
        container.querySelector('[data-reset-list]').addEventListener('click', () => {
            inputs.forEach(input => { input.checked = false; });
            status.textContent = 'Checks reset. Nothing was saved to the app.';
            fallback.hidden = true;
            update();
        });
        container.querySelector('[data-print-list]').addEventListener('click', () => window.print());
        container.querySelector('[data-copy-list]').addEventListener('click', async () => {
            const lines = [container.dataset.checklistTitle, ''];
            container.querySelectorAll('fieldset').forEach(group => {
                lines.push(group.querySelector('legend').textContent.trim());
                group.querySelectorAll('input').forEach(input => lines.push(`${input.checked ? '[x]' : '[ ]'} ${input.value}`));
                lines.push('');
            });
            const text = lines.join('\n');
            try {
                if (!navigator.clipboard || !window.isSecureContext) throw new Error('Clipboard not available');
                await navigator.clipboard.writeText(text);
                fallback.hidden = true;
                status.textContent = 'Checklist copied. Paste it wherever you keep your notes.';
            } catch (_) {
                fallback.value = text;
                fallback.hidden = false;
                fallback.focus();
                fallback.select();
                status.textContent = 'Automatic copying is unavailable. Select and copy the text below.';
            }
        });
        update();
        toolbar.hidden = false;
    });

    // Instrumentation contract, disabled as a collector by design. Listen for these local DOM
    // events only after separately reviewing your analytics provider, privacy notice and consent.
    // Query strings, free text, invitation codes and full referrers never enter the event payload.
    const classifySource = () => {
        const source = (new URLSearchParams(window.location.search).get('utm_source') || '').toLowerCase();
        if (source === 'chatgpt.com' || source === 'chatgpt') return 'chatgpt';
        if (source === 'bing' || source === 'bing.com') return 'bing';
        if (source === 'google' || source === 'google.com') return 'google';
        if (source) return 'other_campaign';
        try {
            const host = new URL(document.referrer).hostname;
            if (host === 'chatgpt.com' || host.endsWith('.chatgpt.com') || host === 'chat.openai.com') return 'chatgpt';
            if (host === 'bing.com' || host.endsWith('.bing.com')) return 'bing';
            if (host === window.location.hostname) return 'internal';
            return 'other_referral';
        } catch (_) { return 'direct_or_unknown'; }
    };
    document.addEventListener('click', event => {
        if (!(event.target instanceof Element)) return;
        const link = event.target.closest('a[data-cta]');
        if (!link) return;
        let destination;
        try { destination = new URL(link.href); } catch (_) { return; }
        if (destination.hostname !== 'apps.apple.com') return;
        const detail = Object.freeze({
            event: 'app_store_click',
            page: document.body.dataset.page || '/',
            placement: link.dataset.cta || 'unspecified',
            source: classifySource(),
            destination: 'app_store'
        });
        window.dispatchEvent(new CustomEvent('readykin:app-store-click', { detail }));
    });
})();
