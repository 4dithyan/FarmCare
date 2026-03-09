/* ============================================================
   FarmCare – Main JavaScript
   Parallax, Scroll Animations, Navbar, Mobile Menu
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initScrollAnimations();
    initParallax();
    initMobileMenu();
    initMessages();
    initSmoothScroll();
    initHeroSlideshow();
});

/* ── Navbar ─────────────────────────────────────────────────── */
function initNavbar() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    const onScroll = () => {
        navbar.classList.toggle('scrolled', window.scrollY > 40);
    };
    window.addEventListener('scroll', onScroll, { passive: true });

    // Active link highlighting
    const links = document.querySelectorAll('.nav-links a');
    const currentPath = window.location.pathname;
    links.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        }
    });
}

/* ── Scroll Animations (IntersectionObserver) ───────────────── */
function initScrollAnimations() {

    // ① Apply stagger classes FIRST so they exist when we query targets
    document.querySelectorAll('[data-stagger]').forEach(parent => {
        Array.from(parent.children).forEach((child, i) => {
            child.classList.add('fade-in');
            child.dataset.delay = i * 100;
        });
    });

    // ② Now collect ALL animated elements (including freshly-staggered ones)
    const targets = document.querySelectorAll('.fade-in, .fade-in-left, .fade-in-right, .scale-in');
    if (!targets.length) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                const delay = parseInt(entry.target.dataset.delay) || 0;
                setTimeout(() => {
                    entry.target.classList.add('visible');
                }, delay);
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.08,
        rootMargin: '0px 0px -30px 0px'
    });

    targets.forEach(t => observer.observe(t));
}

/* ── Parallax Engine ────────────────────────────────────────── */
function initParallax() {
    const hero = document.querySelector('.hero');
    const parallaxImg = document.querySelector('.hero-parallax-img');
    if (!hero || !parallaxImg) return;

    let ticking = false;

    const onScroll = () => {
        if (!ticking) {
            requestAnimationFrame(() => {
                const scrollY = window.scrollY;
                // Move image up slowly as page scrolls down (true parallax)
                // inset:-10% gives ~20% extra height — cap travel so image always covers
                const travel = scrollY * 0.35;
                parallaxImg.style.transform = `translateY(${travel}px)`;
                ticking = false;
            });
            ticking = true;
        }
    };

    window.addEventListener('scroll', onScroll, { passive: true });
}

/* ── Mobile Menu ────────────────────────────────────────────── */
function initMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const mobileMenu = document.querySelector('.mobile-menu');
    if (!hamburger || !mobileMenu) return;

    hamburger.addEventListener('click', () => {
        mobileMenu.classList.toggle('open');
        document.body.style.overflow = mobileMenu.classList.contains('open') ? 'hidden' : '';
        const spans = hamburger.querySelectorAll('span');
        if (mobileMenu.classList.contains('open')) {
            spans[0].style.transform = 'translateY(7px) rotate(45deg)';
            spans[1].style.opacity = '0';
            spans[2].style.transform = 'translateY(-7px) rotate(-45deg)';
        } else {
            spans.forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
        }
    });

    // Close on link click
    mobileMenu.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', () => {
            mobileMenu.classList.remove('open');
            document.body.style.overflow = '';
        });
    });
}

/* ── Django Messages Auto-dismiss ───────────────────────────── */
function initMessages() {
    const alerts = document.querySelectorAll('.alert[data-auto-dismiss]');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity .5s, transform .5s';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-8px)';
            setTimeout(() => alert.remove(), 500);
        }, 4000);
    });

    // Close button
    document.querySelectorAll('.alert-close').forEach(btn => {
        btn.addEventListener('click', () => {
            const alert = btn.closest('.alert');
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        });
    });
}

/* ── Smooth Scroll ──────────────────────────────────────────── */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', e => {
            const target = document.querySelector(a.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

/* ── Counter Animation ──────────────────────────────────────── */
function animateCounter(el, target, duration = 1500) {
    let start = 0;
    const step = (timestamp) => {
        if (!start) start = timestamp;
        const progress = Math.min((timestamp - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.floor(eased * target).toLocaleString();
        if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
}

// Trigger counters when in view
document.addEventListener('DOMContentLoaded', () => {
    const counters = document.querySelectorAll('[data-counter]');
    const obs = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target, parseInt(entry.target.dataset.counter));
                obs.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    counters.forEach(c => obs.observe(c));
});

/* ── Utility: Show Spinner ──────────────────────────────────── */
function showSpinner(msg = 'Analyzing your image with AI...') {
    let overlay = document.querySelector('.spinner-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'spinner-overlay';
        overlay.innerHTML = `<div class="spinner"></div><p style="color:var(--primary);font-weight:600;">${msg}</p>`;
        document.body.appendChild(overlay);
    }
    overlay.querySelector('p').textContent = msg;
    setTimeout(() => overlay.classList.add('show'), 10);
}

function hideSpinner() {
    const overlay = document.querySelector('.spinner-overlay');
    if (overlay) {
        overlay.classList.remove('show');
        setTimeout(() => overlay.remove(), 300);
    }
}

/* ── Hero Slideshow ─────────────────────────────────────────── */
function initHeroSlideshow() {
    const slides = document.querySelectorAll('.hero-slide');
    const dots = document.querySelectorAll('.hero-dot');
    const prevBtn = document.getElementById('heroPrev');
    const nextBtn = document.getElementById('heroNext');
    if (!slides.length) return;

    let currentSlide = 0;
    const totalSlides = slides.length;
    let slideInterval;

    const goToSlide = (n) => {
        slides[currentSlide].classList.remove('active');
        if (dots[currentSlide]) dots[currentSlide].classList.remove('active');

        currentSlide = (n + totalSlides) % totalSlides;

        slides[currentSlide].classList.add('active');
        if (dots[currentSlide]) dots[currentSlide].classList.add('active');
    };

    const nextSlide = () => goToSlide(currentSlide + 1);
    const prevSlide = () => goToSlide(currentSlide - 1);

    // Controls
    if (prevBtn) prevBtn.addEventListener('click', () => { prevSlide(); resetInterval(); });
    if (nextBtn) nextBtn.addEventListener('click', () => { nextSlide(); resetInterval(); });

    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            goToSlide(index);
            resetInterval();
        });
    });

    // Auto cycle
    const startInterval = () => {
        slideInterval = setInterval(nextSlide, 5000);
    };
    const resetInterval = () => {
        clearInterval(slideInterval);
        startInterval();
    };

    startInterval();
}
