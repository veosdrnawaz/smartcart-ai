/**
 * CrossSell AI - Frontend Interaction Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. API Configuration
    // Dynamically detect local vs. production environment for API calls
    const getApiBaseUrl = () => {
        const hostname = window.location.hostname;
        const protocol = window.location.protocol;
        
        if (hostname === 'localhost' || hostname === '127.0.0.1' || protocol === 'file:') {
            return 'http://127.0.0.1:5000';
        }
        return ''; // In production (Vercel), routes are relative
    };

    const API_BASE = getApiBaseUrl();
    console.log(`[CrossSell AI] Configured API Base URL: ${API_BASE || 'Relative (Production)'}`);

    // 2. DOM Elements
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const productSelect = document.getElementById('product-select');
    const getRecsBtn = document.getElementById('get-recommendations-btn');
    
    // States
    const stateIdle = document.getElementById('state-idle');
    const stateLoading = document.getElementById('state-loading');
    const stateError = document.getElementById('state-error');
    const stateEmpty = document.getElementById('state-empty');
    const stateSuccess = document.getElementById('state-success');
    
    // Success Details
    const recommendationsGrid = document.getElementById('recommendations-grid');
    const queriedProductLabel = document.getElementById('queried-product-label');
    const resultsCountBadge = document.getElementById('results-count-badge');
    const errorTitle = document.getElementById('error-title');
    const errorMessage = document.getElementById('error-message');
    
    // Status indicator
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');

    // 3. Theme Toggle Setup (Light/Dark Mode)
    const initTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
        } else if (savedTheme === 'light') {
            document.body.classList.remove('dark-theme');
        } else {
            // Fallback to system preference
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            if (prefersDark) {
                document.body.classList.add('dark-theme');
                localStorage.setItem('theme', 'dark');
            }
        }
    };

    themeToggleBtn.addEventListener('click', () => {
        document.body.classList.toggle('dark-theme');
        const isDark = document.body.classList.contains('dark-theme');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });

    initTheme();

    // 4. Backend Health Check
    const checkBackendHealth = async () => {
        statusIndicator.className = 'status-indicator';
        statusText.innerText = 'Connecting to backend...';
        
        try {
            const response = await fetch(`${API_BASE}/health`);
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'healthy') {
                    statusIndicator.className = 'status-indicator connected';
                    statusText.innerText = 'Backend: Online (Model Ready)';
                } else {
                    statusIndicator.className = 'status-indicator error';
                    statusText.innerText = 'Backend: Degraded (Model Missing)';
                }
            } else {
                throw new Error('Health check response not OK');
            }
        } catch (err) {
            statusIndicator.className = 'status-indicator error';
            statusText.innerText = 'Backend: Offline';
            console.warn('[CrossSell AI] Flask backend appears offline. Local url is:', `${API_BASE}/health`);
        }
    };

    // Run health check initially
    checkBackendHealth();
    // Poll health status every 30 seconds
    setInterval(checkBackendHealth, 30000);

    // 5. Query Handling
    const showState = (stateName) => {
        stateIdle.classList.add('hidden');
        stateLoading.classList.add('hidden');
        stateError.classList.add('hidden');
        stateEmpty.classList.add('hidden');
        stateSuccess.classList.add('hidden');
        
        if (stateName === 'idle') stateIdle.classList.remove('hidden');
        if (stateName === 'loading') stateLoading.classList.remove('hidden');
        if (stateName === 'error') stateError.classList.remove('hidden');
        if (stateName === 'empty') stateEmpty.classList.remove('hidden');
        if (stateName === 'success') stateSuccess.classList.remove('hidden');
    };

    const displayRecommendations = (product, recommendations) => {
        queriedProductLabel.innerText = product;
        resultsCountBadge.innerText = `${recommendations.length} Recommendation${recommendations.length > 1 ? 's' : ''}`;
        
        recommendationsGrid.innerHTML = '';
        
        recommendations.forEach(rec => {
            const card = document.createElement('div');
            card.className = 'glass-card rec-card';
            
            // Format percentages and decimals
            const confidencePct = (rec.confidence * 100).toFixed(1);
            const liftFormatted = rec.lift.toFixed(2);
            const supportFormatted = rec.support.toFixed(2);
            
            card.innerHTML = `
                <div class="rec-product">${rec.item}</div>
                <div class="rec-metric-group">
                    <div class="metric-label-container">
                        <span>Confidence</span>
                        <span class="highlight">${confidencePct}%</span>
                    </div>
                    <div class="confidence-bar-bg">
                        <div class="confidence-bar-fill" data-width="${confidencePct}%"></div>
                    </div>
                </div>
                <div class="pills-group">
                    <span class="metric-pill lift-pill" title="Lift value determines association strength">
                        <strong>Lift:</strong> ${liftFormatted}
                    </span>
                    <span class="metric-pill support-pill" title="Support value determines frequency">
                        <strong>Support:</strong> ${supportFormatted}
                    </span>
                </div>
            `;
            
            recommendationsGrid.appendChild(card);
        });
        
        showState('success');
        
        // Premium micro-animation: Trigger confidence bar fill transitions sequentially
        setTimeout(() => {
            const fills = recommendationsGrid.querySelectorAll('.confidence-bar-fill');
            fills.forEach(fill => {
                const targetWidth = fill.getAttribute('data-width');
                fill.style.width = targetWidth;
            });
        }, 100);
    };

    getRecsBtn.addEventListener('click', async () => {
        const selectedProduct = productSelect.value;
        
        // Validate input: empty selection
        if (!selectedProduct) {
            errorTitle.innerText = "No Product Selected";
            errorMessage.innerText = "Please select a product from the shopping cart dropdown menu before executing recommendations.";
            showState('error');
            return;
        }

        showState('loading');
        
        try {
            const response = await fetch(`${API_BASE}/recommend`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ product: selectedProduct })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                if (data.recommendations && data.recommendations.length > 0) {
                    displayRecommendations(data.product, data.recommendations);
                } else {
                    showState('empty');
                }
            } else {
                // Backend-returned custom exceptions
                errorTitle.innerText = data.error || "Recommendation Failed";
                errorMessage.innerText = data.message || "An error occurred on the API server while fetching bundles.";
                showState('error');
            }
        } catch (err) {
            // General Network/CORS failures
            errorTitle.innerText = "API Server Connection Failed";
            errorMessage.innerText = `Could not establish a connection to the recommendation backend. Make sure the Flask application is running at ${API_BASE || 'its relative route'} and is accepting requests. Details: ${err.message}`;
            showState('error');
            statusIndicator.className = 'status-indicator error';
            statusText.innerText = 'Backend: Connection Lost';
        }
    });
});
