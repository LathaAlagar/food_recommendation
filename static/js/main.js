// FoodieFinds AI - Main JavaScript Utilities

document.addEventListener('DOMContentLoaded', () => {
    initDarkMode();
    initLocationHelpers();
    initFavoriteButtons();
});

// 1. Dark Mode Toggle
function initDarkMode() {
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (!themeToggleBtn) return;
    
    // Check local storage or system preference
    if (localStorage.getItem('color-theme') === 'dark' || 
        (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
        themeToggleBtn.setAttribute('checked', 'true');
    } else {
        document.documentElement.classList.remove('dark');
    }
    
    themeToggleBtn.addEventListener('change', () => {
        if (document.documentElement.classList.contains('dark')) {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('color-theme', 'light');
        } else {
            document.documentElement.classList.add('dark');
            localStorage.setItem('color-theme', 'dark');
        }
    });
}

// 2. Geolocation & Location Services
const CHENNAI_ZONES = [
    { name: "Adyar", lat: 13.0012, lon: 80.2565 },
    { name: "T. Nagar", lat: 13.0405, lon: 80.2337 },
    { name: "Velachery", lat: 12.9802, lon: 80.2228 },
    { name: "Nungambakkam", lat: 13.0587, lon: 80.2458 },
    { name: "OMR", lat: 12.9654, lon: 80.2461 }
];

function initLocationHelpers() {
    const detectBtn = document.getElementById('detect-location-btn');
    if (!detectBtn) return;
    
    detectBtn.addEventListener('click', () => {
        detectBtn.disabled = true;
        const originalText = detectBtn.innerHTML;
        detectBtn.innerHTML = `
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg> Detecting...
        `;
        
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    
                    // Find closest Chennai zone
                    let closestZone = CHENNAI_ZONES[0];
                    let minDistance = calculateDistance(lat, lon, closestZone.lat, closestZone.lon);
                    
                    for (let i = 1; i < CHENNAI_ZONES.length; i++) {
                        const dist = calculateDistance(lat, lon, CHENNAI_ZONES[i].lat, CHENNAI_ZONES[i].lon);
                        if (dist < minDistance) {
                            minDistance = dist;
                            closestZone = CHENNAI_ZONES[i];
                        }
                    }
                    
                    // Show notification & redirect
                    showToast(`Detected location near ${closestZone.name}!`, 'success');
                    setTimeout(() => {
                        window.location.href = `/set-location?location=${encodeURIComponent(closestZone.name)}`;
                    }, 1200);
                },
                (error) => {
                    detectBtn.disabled = false;
                    detectBtn.innerHTML = originalText;
                    showToast('Could not autodetect location. Please select manually.', 'error');
                    console.error('Geolocation error:', error);
                }
            );
        } else {
            detectBtn.disabled = false;
            detectBtn.innerHTML = originalText;
            showToast('Geolocation is not supported by your browser.', 'warning');
        }
    });
}

// Distance helper using Haversine formula
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
        Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
        Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

// 3. Favorites Interactive Handler
function initFavoriteButtons() {
    const favButtons = document.querySelectorAll('.fav-toggle-btn');
    favButtons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const foodId = btn.dataset.foodId;
            const restaurantId = btn.dataset.restaurantId;
            const payload = {};
            if (foodId) payload.food_id = foodId;
            if (restaurantId) payload.restaurant_id = restaurantId;
            
            try {
                const response = await fetch('/api/favorites/toggle', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                
                if (response.status === 401) {
                    showToast('Please log in to add favorites!', 'warning');
                    return;
                }
                
                const data = await response.json();
                
                // Toggle active style
                if (data.is_favorite) {
                    btn.classList.add('text-red-500');
                    btn.classList.remove('text-gray-400');
                    // If heart icon, fill it
                    btn.querySelector('svg')?.setAttribute('fill', 'currentColor');
                    showToast(data.message || 'Added to favorites!', 'success');
                } else {
                    btn.classList.remove('text-red-500');
                    btn.classList.add('text-gray-400');
                    // Empty heart
                    btn.querySelector('svg')?.setAttribute('fill', 'none');
                    showToast(data.message || 'Removed from favorites', 'info');
                }
            } catch (err) {
                console.error('Error toggling favorite:', err);
                showToast('Something went wrong. Try again.', 'error');
            }
        });
    });
}

// 4. Custom Toast Notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `glass-panel shadow-lg rounded-xl p-4 mb-3 max-w-sm flex items-center justify-between border-l-4 translate-x-5 opacity-0 transition-all duration-300 animate-slide-right`;
    
    let colorClass = 'border-blue-500 text-blue-800 dark:text-blue-200';
    let icon = 'ℹ️';
    if (type === 'success') {
        colorClass = 'border-green-500 text-green-800 dark:text-green-200';
        icon = '✅';
    } else if (type === 'warning') {
        colorClass = 'border-yellow-500 text-yellow-800 dark:text-yellow-200';
        icon = '⚠️';
    } else if (type === 'error') {
        colorClass = 'border-red-500 text-red-800 dark:text-red-200';
        icon = '❌';
    }
    
    toast.classList.add(...colorClass.split(' '));
    toast.innerHTML = `
        <div class="flex items-center space-x-3">
            <span class="text-xl">${icon}</span>
            <span class="text-sm font-medium">${message}</span>
        </div>
        <button class="ml-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 focus:outline-none" onclick="this.parentElement.remove()">
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
        </button>
    `;
    
    container.appendChild(toast);
    
    // Auto-remove toast after 4 seconds
    setTimeout(() => {
        toast.classList.add('opacity-0', '-translate-x-5');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'fixed top-5 right-5 z-50 flex flex-col space-y-2';
    document.body.appendChild(container);
    return container;
}
