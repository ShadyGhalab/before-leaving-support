/* Progressive enhancement only: all public content is readable without JavaScript. */
(() => {
    'use strict';
    const nav = document.getElementById('siteNav');
    const menuButton = document.getElementById('menuButton');
    const navLinks = document.getElementById('navLinks');
    if (nav && menuButton && navLinks) {
        const mobile = window.matchMedia('(max-width: 860px)');
        let open = false;
        const renderMenu = () => {
            navLinks.hidden = mobile.matches && !open;
            navLinks.classList.toggle('open', mobile.matches && open);
            menuButton.setAttribute('aria-expanded', String(mobile.matches && open));
            menuButton.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
        };
        const closeMenu = (restoreFocus = false) => {
            open = false;
            renderMenu();
            if (restoreFocus) menuButton.focus();
        };
        menuButton.addEventListener('click', () => { open = !open; renderMenu(); });
        navLinks.addEventListener('click', (event) => {
            if (event.target instanceof Element && event.target.closest('a')) closeMenu();
        });
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && open) closeMenu(true);
        });
        document.addEventListener('click', (event) => {
            if (open && event.target instanceof Node && !nav.contains(event.target)) closeMenu();
        });
        const onViewportChange = () => {
            const focusWasInMenu = navLinks.contains(document.activeElement);
            closeMenu(mobile.matches && focusWasInMenu);
        };
        if (mobile.addEventListener) mobile.addEventListener('change', onViewportChange);
        else mobile.addListener(onViewportChange);
        renderMenu();
        document.body.classList.add('js-enhanced');
        const updateNav = () => nav.classList.toggle('scrolled', window.scrollY > 18);
        updateNav();
        window.addEventListener('scroll', updateNav, { passive: true });
    }
    // The source CSS reveal treatment is intentionally overridden: no JS-dependent hidden text.
    document.querySelectorAll('.reveal').forEach(element => element.classList.add('visible'));
    const track = document.getElementById('storyTrack');
    const prev = document.getElementById('storyPrev');
    const next = document.getElementById('storyNext');
    if (track && prev && next) {
        const distance = () => Math.max(280, Math.min(track.clientWidth * 0.72, 440));
        const scroll = (direction) => track.scrollBy({
            left: direction * distance(),
            behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'
        });
        prev.addEventListener('click', () => scroll(-1));
        next.addEventListener('click', () => scroll(1));
    }
})();
