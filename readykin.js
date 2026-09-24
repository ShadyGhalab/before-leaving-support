(() => {
    const nav = document.getElementById('siteNav');
    const menuButton = document.getElementById('menuButton');
    const navLinks = document.getElementById('navLinks');

    const updateNav = () => nav?.classList.toggle('scrolled', window.scrollY > 18);
    updateNav();
    window.addEventListener('scroll', updateNav, { passive: true });

    if (menuButton && navLinks) {
        menuButton.addEventListener('click', () => {
            const open = navLinks.classList.toggle('open');
            menuButton.setAttribute('aria-expanded', String(open));
            menuButton.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
        });
        navLinks.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
            navLinks.classList.remove('open');
            menuButton.setAttribute('aria-expanded', 'false');
            menuButton.setAttribute('aria-label', 'Open menu');
        }));
    }

    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const reveals = document.querySelectorAll('.reveal');
    if (reduced || !('IntersectionObserver' in window)) {
        reveals.forEach(el => el.classList.add('visible'));
    } else {
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
        reveals.forEach(el => observer.observe(el));
    }

    const track = document.getElementById('storyTrack');
    const prev = document.getElementById('storyPrev');
    const next = document.getElementById('storyNext');
    if (track && prev && next) {
        const amount = () => Math.max(320, Math.min(track.clientWidth * 0.72, 440));
        prev.addEventListener('click', () => track.scrollBy({ left: -amount(), behavior: reduced ? 'auto' : 'smooth' }));
        next.addEventListener('click', () => track.scrollBy({ left: amount(), behavior: reduced ? 'auto' : 'smooth' }));
    }
})();
