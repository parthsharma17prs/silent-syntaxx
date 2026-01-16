/* ============================================
   SILENT SYNTAX PORTAL - PREMIUM EFFECTS JS
   ============================================ */

// Initialize effects when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  initCursorEffects();
  initScrollReveal();
  initParallaxEffect();
  initMagneticButtons();
  initRippleEffect();
  initCounterAnimation();
  initCardTilt();
  initSmoothScroll();
  initFloatingParticles();
  initTypewriterEffect();
  addLoadingAnimation();
  initSpotlightEffect();
});

// === CUSTOM CURSOR EFFECTS ===
function initCursorEffects() {
  // Check if user prefers reduced motion
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  
  // Only on desktop
  if (window.innerWidth < 768) return;
  
  // Create cursor elements
  const cursorGlow = document.createElement('div');
  cursorGlow.className = 'cursor-glow';
  document.body.appendChild(cursorGlow);
  
  const cursorDot = document.createElement('div');
  cursorDot.className = 'cursor-dot';
  document.body.appendChild(cursorDot);
  
  let mouseX = 0, mouseY = 0;
  let glowX = 0, glowY = 0;
  let dotX = 0, dotY = 0;
  
  // Track mouse position
  document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });
  
  // Smooth cursor animation
  function animateCursor() {
    // Smooth follow for glow
    glowX += (mouseX - glowX) * 0.08;
    glowY += (mouseY - glowY) * 0.08;
    cursorGlow.style.left = glowX + 'px';
    cursorGlow.style.top = glowY + 'px';
    
    // Faster follow for dot
    dotX += (mouseX - dotX) * 0.2;
    dotY += (mouseY - dotY) * 0.2;
    cursorDot.style.left = dotX + 'px';
    cursorDot.style.top = dotY + 'px';
    
    requestAnimationFrame(animateCursor);
  }
  animateCursor();
  
  // Add hover effect for interactive elements
  const interactiveElements = document.querySelectorAll('a, button, .card, input, select, textarea, .btn');
  interactiveElements.forEach(el => {
    el.addEventListener('mouseenter', () => {
      cursorDot.classList.add('hover');
      cursorGlow.style.width = '400px';
      cursorGlow.style.height = '400px';
    });
    el.addEventListener('mouseleave', () => {
      cursorDot.classList.remove('hover');
      cursorGlow.style.width = '300px';
      cursorGlow.style.height = '300px';
    });
  });
  
  // Hide cursor when leaving window
  document.addEventListener('mouseleave', () => {
    cursorGlow.style.opacity = '0';
    cursorDot.style.opacity = '0';
  });
  
  document.addEventListener('mouseenter', () => {
    cursorGlow.style.opacity = '1';
    cursorDot.style.opacity = '1';
  });
}

// === SCROLL REVEAL ANIMATIONS ===
function initScrollReveal() {
  const revealElements = document.querySelectorAll('.card, .grid > *, section > *, .feature-card, .stat-chip-landing');
  
  const observerOptions = {
    root: null,
    rootMargin: '0px 0px -100px 0px',
    threshold: 0.1
  };
  
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
      if (entry.isIntersecting) {
        // Add staggered delay
        setTimeout(() => {
          entry.target.classList.add('reveal-active');
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }, index * 100);
        revealObserver.unobserve(entry.target);
      }
    });
  }, observerOptions);
  
  revealElements.forEach((el, index) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(40px)';
    el.style.transition = `all 0.8s cubic-bezier(0.16, 1, 0.3, 1) ${index * 0.05}s`;
    revealObserver.observe(el);
  });
}

// === PARALLAX SCROLLING ===
function initParallaxEffect() {
  const parallaxElements = document.querySelectorAll('.hero-landing, .page-shell header, .landing-title');
  
  window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    
    parallaxElements.forEach(el => {
      const speed = el.dataset.parallaxSpeed || 0.3;
      el.style.transform = `translateY(${scrolled * speed}px)`;
    });
  }, { passive: true });
}

// === MAGNETIC BUTTON EFFECT ===
function initMagneticButtons() {
  const buttons = document.querySelectorAll('.btn-primary, .btn-hero');
  
  buttons.forEach(btn => {
    btn.addEventListener('mousemove', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      
      btn.style.transform = `translate(${x * 0.2}px, ${y * 0.2}px) scale(1.05)`;
    });
    
    btn.addEventListener('mouseleave', () => {
      btn.style.transform = 'translate(0, 0) scale(1)';
    });
    
    // Reset on click
    btn.addEventListener('click', () => {
      btn.style.transform = 'translate(0, 0) scale(0.95)';
      setTimeout(() => {
        btn.style.transform = 'translate(0, 0) scale(1)';
      }, 150);
    });
  });
}

// === RIPPLE EFFECT ===
function initRippleEffect() {
  const rippleElements = document.querySelectorAll('.btn, .card, .nav a');
  
  rippleElements.forEach(el => {
    el.addEventListener('click', function(e) {
      const rect = this.getBoundingClientRect();
      const ripple = document.createElement('span');
      
      ripple.style.cssText = `
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.4);
        transform: scale(0);
        animation: rippleAnimation 0.6s linear;
        pointer-events: none;
      `;
      
      const size = Math.max(rect.width, rect.height);
      ripple.style.width = ripple.style.height = size + 'px';
      ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
      ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
      
      this.style.position = 'relative';
      this.style.overflow = 'hidden';
      this.appendChild(ripple);
      
      setTimeout(() => ripple.remove(), 600);
    });
  });
  
  // Add ripple keyframes
  const style = document.createElement('style');
  style.textContent = `
    @keyframes rippleAnimation {
      to {
        transform: scale(4);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(style);
}

// === NUMBER COUNTER ANIMATION ===
function initCounterAnimation() {
  const counters = document.querySelectorAll('.stat-number, .card h3, .stat-chip-landing .stat-number');
  
  const observerOptions = {
    threshold: 0.5
  };
  
  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const text = el.innerText;
        
        // Check if it's a number
        const numMatch = text.match(/^(\d+)([%+]?)$/);
        if (numMatch) {
          const target = parseInt(numMatch[1]);
          const suffix = numMatch[2] || '';
          let current = 0;
          const increment = target / 50;
          const duration = 1500;
          const stepTime = duration / 50;
          
          const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
              clearInterval(timer);
              current = target;
            }
            el.innerText = Math.floor(current) + suffix;
          }, stepTime);
        }
        
        counterObserver.unobserve(el);
      }
    });
  }, observerOptions);
  
  counters.forEach(counter => {
    counterObserver.observe(counter);
  });
}

// === 3D CARD TILT ===
function initCardTilt() {
  const cards = document.querySelectorAll('.card, .feature-card, .job-card');
  
  cards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateX = (y - centerY) / 20;
      const rotateY = (centerX - x) / 20;
      
      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
      card.style.transition = 'transform 0.1s ease';
      
      // Add shine effect
      const shine = card.querySelector('.card-shine') || createShineElement(card);
      shine.style.left = x + 'px';
      shine.style.top = y + 'px';
    });
    
    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
      card.style.transition = 'transform 0.5s ease';
      
      const shine = card.querySelector('.card-shine');
      if (shine) shine.style.opacity = '0';
    });
    
    card.addEventListener('mouseenter', () => {
      const shine = card.querySelector('.card-shine');
      if (shine) shine.style.opacity = '1';
    });
  });
}

function createShineElement(card) {
  const shine = document.createElement('div');
  shine.className = 'card-shine';
  shine.style.cssText = `
    position: absolute;
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 70%);
    transform: translate(-50%, -50%);
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s ease;
    z-index: 1;
  `;
  card.style.position = 'relative';
  card.style.overflow = 'hidden';
  card.appendChild(shine);
  return shine;
}

// === SMOOTH SCROLL WITH EASING ===
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      
      const target = document.querySelector(targetId);
      if (target) {
        const targetPosition = target.getBoundingClientRect().top + window.pageYOffset;
        const startPosition = window.pageYOffset;
        const distance = targetPosition - startPosition;
        let startTime = null;
        
        function animation(currentTime) {
          if (startTime === null) startTime = currentTime;
          const timeElapsed = currentTime - startTime;
          const duration = 1000;
          const run = easeInOutCubic(timeElapsed, startPosition, distance, duration);
          window.scrollTo(0, run);
          if (timeElapsed < duration) requestAnimationFrame(animation);
        }
        
        function easeInOutCubic(t, b, c, d) {
          t /= d / 2;
          if (t < 1) return c / 2 * t * t * t + b;
          t -= 2;
          return c / 2 * (t * t * t + 2) + b;
        }
        
        requestAnimationFrame(animation);
      }
    });
  });
}

// === FLOATING PARTICLES ===
function initFloatingParticles() {
  // Check for reduced motion preference
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  
  const container = document.createElement('div');
  container.className = 'particles-container';
  document.body.prepend(container);
  
  for (let i = 0; i < 15; i++) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    particle.style.left = Math.random() * 100 + '%';
    particle.style.animationDelay = -Math.random() * 15 + 's';
    particle.style.animationDuration = (15 + Math.random() * 10) + 's';
    
    // Random colors
    const colors = ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#8b5cf6'];
    particle.style.background = colors[Math.floor(Math.random() * colors.length)];
    particle.style.width = (3 + Math.random() * 5) + 'px';
    particle.style.height = particle.style.width;
    
    container.appendChild(particle);
  }
}

// === TYPEWRITER EFFECT ===
function initTypewriterEffect() {
  const typewriterElements = document.querySelectorAll('.landing-title');
  
  typewriterElements.forEach(el => {
    const text = el.innerText;
    el.innerText = '';
    el.style.visibility = 'visible';
    
    let i = 0;
    function type() {
      if (i < text.length) {
        el.innerHTML += text.charAt(i);
        i++;
        setTimeout(type, 50);
      }
    }
    
    // Start typing when element is in view
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          setTimeout(type, 500);
          observer.unobserve(el);
        }
      });
    });
    
    observer.observe(el);
  });
}

// === LOADING ANIMATION ===
function addLoadingAnimation() {
  // Add a nice loading transition when page loads
  document.body.style.opacity = '0';
  
  window.addEventListener('load', () => {
    document.body.style.transition = 'opacity 0.5s ease';
    document.body.style.opacity = '1';
  });
}

// === SPOTLIGHT EFFECT ===
function initSpotlightEffect() {
  const spotlightElements = document.querySelectorAll('.card, .glass, .feature-card');
  
  spotlightElements.forEach(el => {
    el.addEventListener('mousemove', (e) => {
      const rect = el.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      el.style.setProperty('--x', x + 'px');
      el.style.setProperty('--y', y + 'px');
    });
  });
}

// === SCROLL PROGRESS BAR ===
function initScrollProgress() {
  const progressBar = document.createElement('div');
  progressBar.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 0%;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #06b6d4, #10b981);
    z-index: 10000;
    transition: width 0.1s ease;
  `;
  document.body.appendChild(progressBar);
  
  window.addEventListener('scroll', () => {
    const scrollTop = window.pageYOffset;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollPercent = (scrollTop / docHeight) * 100;
    progressBar.style.width = scrollPercent + '%';
  }, { passive: true });
}

// Initialize scroll progress on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initScrollProgress);
} else {
  initScrollProgress();
}

// === TOAST ANIMATION ENHANCEMENT ===
function enhanceToasts() {
  const originalShowToast = window.showToast;
  if (typeof originalShowToast === 'function') {
    window.showToast = function(msg, type) {
      originalShowToast(msg, type);
      
      // Add entrance animation to newest toast
      const toasts = document.querySelectorAll('.toast');
      const newest = toasts[toasts.length - 1];
      if (newest) {
        newest.style.animation = 'slideInRight 0.5s cubic-bezier(0.16, 1, 0.3, 1)';
      }
    };
  }
  
  // Add the animation keyframes
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideInRight {
      from {
        opacity: 0;
        transform: translateX(100px);
      }
      to {
        opacity: 1;
        transform: translateX(0);
      }
    }
  `;
  document.head.appendChild(style);
}

enhanceToasts();

// === BUTTON CLICK EFFECT ===
document.addEventListener('click', (e) => {
  if (e.target.matches('.btn-primary, .btn-success, .btn-warning, .btn-error')) {
    e.target.style.transform = 'scale(0.95)';
    setTimeout(() => {
      e.target.style.transform = '';
    }, 100);
  }
});

// === FOCUS ANIMATION ===
document.addEventListener('focusin', (e) => {
  if (e.target.matches('input, textarea, select')) {
    e.target.style.transform = 'scale(1.02)';
    e.target.style.boxShadow = '0 0 0 3px rgba(99, 102, 241, 0.2), 0 0 30px rgba(99, 102, 241, 0.15)';
  }
});

document.addEventListener('focusout', (e) => {
  if (e.target.matches('input, textarea, select')) {
    e.target.style.transform = '';
    e.target.style.boxShadow = '';
  }
});

// === NAVBAR SCROLL EFFECT ===
window.addEventListener('scroll', () => {
  const navbar = document.querySelector('.navbar-lite');
  if (navbar) {
    if (window.pageYOffset > 50) {
      navbar.style.backdropFilter = 'blur(30px)';
      navbar.style.boxShadow = '0 10px 40px rgba(0, 0, 0, 0.3)';
    } else {
      navbar.style.backdropFilter = 'blur(20px)';
      navbar.style.boxShadow = '';
    }
  }
}, { passive: true });

console.log('✨ Silent Syntax Premium Effects v2.0 loaded successfully!');
