// Smooth scrolling
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

// Navbar scroll effect
let lastScroll = 0;
const navbar = document.getElementById('navbar');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
    
    lastScroll = currentScroll;
});

// Animated counter for stats
function animateCounter(element) {
    const target = parseFloat(element.dataset.target);
    const isDecimal = target % 1 !== 0;
    const duration = 2000;
    const steps = 60;
    const increment = target / steps;
    const stepDuration = duration / steps;
    
    let current = 0;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
    if (element.dataset.unit === 'percent') {
        element.textContent = isDecimal ? target.toFixed(1) + '%' : Math.round(target) + '%';
    } else {
        element.textContent = Math.round(target);
    }
    clearInterval(timer);
} else {
    if (element.dataset.unit === 'percent') {
        element.textContent = isDecimal ? current.toFixed(1) + '%' : Math.round(current) + '%';
    } else {
        element.textContent = Math.round(current);
    }
}

    }, stepDuration);
}

// Intersection Observer for stats animation
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const statNumbers = entry.target.querySelectorAll('.stat-number');
            statNumbers.forEach(number => {
                if (!number.dataset.animated) {
                    number.dataset.animated = 'true';
                    animateCounter(number);
                }
            });
        }
    });
}, { threshold: 0.5 });

// Observe stats section
const statsSection = document.getElementById('stats');
if (statsSection) {
    statsObserver.observe(statsSection);
}

// Intersection Observer for fade-in animations
const fadeObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, { threshold: 0.1 });

// Observe all feature cards
document.addEventListener('DOMContentLoaded', () => {
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        fadeObserver.observe(card);
    });
    
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        fadeObserver.observe(card);
    });
});

// Parallax effect for background orbs
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const orbs = document.querySelectorAll('.bg-orb');
    
    orbs.forEach((orb, index) => {
        const speed = (index + 1) * 0.1;
        orb.style.transform = `translateY(${scrolled * speed}px)`;
    });
});

// Add hover effect to buttons
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-2px)';
    });
    
    button.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
    });
});

// Floating cards random movement
function addRandomMovement() {
    const floatingCards = document.querySelectorAll('.floating-card');
    
    floatingCards.forEach(card => {
        const randomX = Math.random() * 20 - 10;
        const randomY = Math.random() * 20 - 10;
        
        card.style.transform = `translate(${randomX}px, ${randomY}px)`;
    });
}

// Add subtle random movement to floating cards every 3 seconds
setInterval(addRandomMovement, 3000);

// Cursor glow effect (optional enhancement)
document.addEventListener('mousemove', (e) => {
    const cursor = document.createElement('div');
    cursor.className = 'cursor-glow';
    cursor.style.left = e.pageX + 'px';
    cursor.style.top = e.pageY + 'px';
    document.body.appendChild(cursor);
    
    setTimeout(() => {
        cursor.remove();
    }, 500);
});

// Add loading animation
window.addEventListener('load', () => {
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '1';
    }, 100);
});

window.addEventListener('load', () => {
  const loader = document.getElementById('intro-loader');
  setTimeout(() => {
    loader.classList.add('fade-out');
    setTimeout(() => loader.remove(), 1000);
  }, 2000);
});
