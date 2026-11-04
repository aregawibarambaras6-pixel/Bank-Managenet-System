/**
 * Apex Bank Management System - Client-side Interactive Script
 * Integrates interactive UI, real-time clock, copy utilities, and polyglot engine helpers
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Real-Time System Clock in Header
    initSystemClock();

    // 2. Smooth Scroll for internal anchor links
    initSmoothScroll();

    // 3. Auto-dismiss alerts after 6 seconds
    initAutoDismissAlerts();
});

/**
 * Updates the system time display in the top bar every second
 */
function initSystemClock() {
    const clockElement = document.getElementById('liveClock');
    if (!clockElement) return;

    function updateClock() {
        const now = new Date();
        const options = { 
            weekday: 'short', 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit',
            hour12: true 
        };
        clockElement.textContent = `System Time: ${now.toLocaleString('en-US', options)}`;
    }

    updateClock();
    setInterval(updateClock, 1000);
}

/**
 * Smooth scrolling configuration for in-page section links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Auto dismiss alerts after timeout
 */
function initAutoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {
                alert.style.display = 'none';
            }
        }, 6000);
    });
}

/**
 * Quick clipboard copy helper with visual indicator
 */
function copyToClipboard(text, label = 'Copied!') {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            alert(`${label}: ${text}`);
        }).catch(err => {
            console.error('Copy error', err);
        });
    }
}
