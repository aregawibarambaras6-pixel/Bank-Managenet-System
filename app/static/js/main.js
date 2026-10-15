/**
 * Apex Bank Management System - Client-side Interactive Script
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Real-Time System Clock in Header
    initSystemClock();

    // 2. Smooth Scroll for internal anchor links
    initSmoothScroll();
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
 * Interactive Feedback for Portal login buttons in Phase 1
 * @param {string} roleName 
 */
function showPortalNotice(roleName) {
    const message = `Welcome to the ${roleName} Portal!\n\nAuthentication & dashboard features for ${roleName} will be unlocked in Phase 2.`;
    alert(message);
}
