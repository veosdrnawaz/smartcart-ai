/**
 * SmartCart AI — Frontend Interaction Logic (v2.0)
 * Works with the redesigned index.html / style.css
 */

document.addEventListener('DOMContentLoaded', () => {

    // ─────────────────────────────────────────────
    // 1. API Configuration
    // ─────────────────────────────────────────────
    const getApiBaseUrl = () => {
        const hostname = window.location.hostname;
        const protocol = window.location.protocol;
        if (hostname === 'localhost' || hostname === '127.0.0.1' || protocol === 'file:') {
            return 'http://127.0.0.1:5000';
        }
        return ''; // Relative in production (Vercel)
    };

    const API_BASE = getApiBaseUrl();
    console.log(`[SmartCart AI] API Base: ${API_BASE || 'Relative (Production)'}`);

    // ─────────────────────────────────────────────
    // 2. DOM References
    // ─────────────────────────────────────────────
    const productSelect       = document.getElementById('product-select');
    const getRecsBtn          = document.getElementById('get-recommendations-btn');

    // State panels
    const stateIdle    = document.getElementById('state-idle');
    const stateLoading = document.getElementById('state-loading');
    const stateError   = document.getElementById('state-error');
    const stateEmpty   = document.getElementById('state-empty');
    const stateSuccess = document.getElementById('state-success');

    // Success details
    const recsGrid            = document.getElementById('recommendations-grid');
    const queriedProductLabel = document.getElementById('queried-product-label');
    const resultsCountBadge   = document.getElementById('results-count-badge');
    const errorTitle          = document.getElementById('error-title');
    const errorMessage        = document.getElementById('error-message');

    // API status indicator (new class: api-dot, id: status-indicator)
    const statusDot  = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');

    // ─────────────────────────────────────────────
    // 3. State Switcher
    // ─────────────────────────────────────────────
    const showState = (name) => {
        [stateIdle, stateLoading, stateError, stateEmpty, stateSuccess].forEach(el => {
            el.classList.add('hidden');
        });
        const map = {
            idle:    stateIdle,
            loading: stateLoading,
            error:   stateError,
            empty:   stateEmpty,
            success: stateSuccess
        };
        if (map[name]) map[name].classList.remove('hidden');
    };

    // ─────────────────────────────────────────────
    // 4. Backend Health Check
    // ─────────────────────────────────────────────
    const setStatus = (type, label) => {
        if (!statusDot || !statusText) return;
        // Remove all state classes, set new one
        statusDot.className = 'api-dot';
        if (type === 'connected') statusDot.classList.add('connected');
        if (type === 'error')     statusDot.classList.add('error');
        statusText.textContent = label;
    };

    const checkHealth = async () => {
        setStatus('', 'Backend: Connecting...');
        try {
            const res = await fetch(`${API_BASE}/health`);
            if (res.ok) {
                const data = await res.json();
                if (data.status === 'healthy') {
                    setStatus('connected', 'Backend: Online — Model Ready');
                } else {
                    setStatus('error', 'Backend: Degraded (Model Missing)');
                }
            } else {
                throw new Error('Non-OK response');
            }
        } catch {
            setStatus('error', 'Backend: Offline');
            console.warn('[SmartCart AI] Flask backend unreachable at', `${API_BASE}/health`);
        }
    };

    checkHealth();
    setInterval(checkHealth, 30000);

    // ─────────────────────────────────────────────
    // 5. Render Recommendations
    // ─────────────────────────────────────────────
    const renderRecs = (product, recs) => {
        queriedProductLabel.textContent = product;
        resultsCountBadge.textContent = `${recs.length} Rule${recs.length !== 1 ? 's' : ''} Found`;
        recsGrid.innerHTML = '';

        recs.forEach(rec => {
            const card = document.createElement('div');
            card.className = 'glass-card rec-card';

            const confPct   = (rec.confidence * 100).toFixed(1);
            const liftFmt   = parseFloat(rec.lift).toFixed(2);
            const suppFmt   = parseFloat(rec.support).toFixed(2);

            card.innerHTML = `
                <div class="rec-product">${rec.item}</div>
                <div class="rec-metric-group">
                    <div class="metric-label-container">
                        <span>Confidence</span>
                        <span class="highlight">${confPct}%</span>
                    </div>
                    <div class="confidence-bar-bg">
                        <div class="confidence-bar-fill" data-width="${confPct}"></div>
                    </div>
                </div>
                <div class="pills-group">
                    <span class="metric-pill lift-pill" title="Association strength — higher is stronger">
                        <strong>Lift:</strong> ${liftFmt}
                    </span>
                    <span class="metric-pill support-pill" title="Frequency in transactions">
                        <strong>Supp:</strong> ${suppFmt}
                    </span>
                </div>
            `;

            recsGrid.appendChild(card);
        });

        showState('success');

        // Animate confidence bars after render
        setTimeout(() => {
            recsGrid.querySelectorAll('.confidence-bar-fill').forEach(bar => {
                bar.style.width = bar.dataset.width + '%';
            });
        }, 100);
    };

    // ─────────────────────────────────────────────
    // 6. Button Click — Fetch Recommendations
    // ─────────────────────────────────────────────
    getRecsBtn.addEventListener('click', async () => {
        const product = productSelect.value;

        if (!product) {
            if (errorTitle)   errorTitle.textContent  = 'No Product Selected';
            if (errorMessage) errorMessage.textContent = 'Choose a product from the dropdown before running the engine.';
            showState('error');
            return;
        }

        showState('loading');
        getRecsBtn.disabled = true;

        try {
            const res = await fetch(`${API_BASE}/recommend`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product })
            });

            const data = await res.json();

            if (res.ok) {
                if (data.recommendations && data.recommendations.length > 0) {
                    renderRecs(data.product, data.recommendations);
                } else {
                    showState('empty');
                }
            } else {
                if (errorTitle)   errorTitle.textContent  = data.error   || 'Recommendation Failed';
                if (errorMessage) errorMessage.textContent = data.message || 'The API returned an error. Check the Flask server logs.';
                showState('error');
            }
        } catch (err) {
            if (errorTitle)   errorTitle.textContent  = 'API Connection Failed';
            if (errorMessage) errorMessage.textContent = `Could not reach the Flask backend at ${API_BASE || 'relative route'}. Ensure the server is running. — ${err.message}`;
            showState('error');
            setStatus('error', 'Backend: Connection Lost');
        } finally {
            getRecsBtn.disabled = false;
        }
    });

});
