/**
 * NextStep — Frontend Application
 * Handles API calls, navigation, and real-time UI updates
 */

const API = '';
let currentUser = null;
let currentSection = 'hero';

// ── API Helpers ──────────────────────────────────────────────

async function api(path, options = {}) {
    const url = `${API}${path}`;
    const config = { headers: { 'Content-Type': 'application/json' }, ...options };
    if (config.body && typeof config.body === 'object') config.body = JSON.stringify(config.body);
    try {
        const res = await fetch(url, config);
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }
        return await res.json();
    } catch (e) {
        if (e.message.includes('Failed to fetch')) throw new Error('Service unavailable');
        throw e;
    }
}

// ── Navigation ──────────────────────────────────────────────

function showSection(name) {
    document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
    const hero = document.getElementById('section-hero');
    if (name === 'hero') { hero.style.display = ''; }
    else { hero.style.display = 'none'; document.getElementById(`section-${name}`).classList.remove('hidden'); }
    document.querySelectorAll('.nav-link').forEach(l => l.classList.toggle('active', l.dataset.section === name));
    currentSection = name;
}

document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', e => {
        e.preventDefault();
        const section = link.dataset.section;
        if (section === 'dashboard' && !currentUser) { showSection('setup'); return; }
        showSection(section);
        if (section === 'jobs') loadJobs();
        if (section === 'recommendations') loadRecommendations();
        if (section === 'system') checkHealth();
        if (section === 'dashboard') loadDashboard();
    });
});

// ── Loading Screen ──────────────────────────────────────────

setTimeout(() => {
    const loader = document.getElementById('loading-screen');
    if (loader) loader.classList.add('hide');
    createParticles();
    loadStats();
}, 500);

function createParticles() {
    const container = document.getElementById('particles');
    if (!container) return;
    for (let i = 0; i < 20; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        p.style.left = Math.random() * 100 + '%';
        p.style.top = Math.random() * 100 + '%';
        p.style.animationDelay = Math.random() * 6 + 's';
        p.style.animationDuration = (4 + Math.random() * 4) + 's';
        const colors = ['#3b82f6', '#8b5cf6', '#10b981', '#06b6d4'];
        p.style.background = colors[Math.floor(Math.random() * colors.length)];
        container.appendChild(p);
    }
}

async function loadStats() {
    try {
        const jobs = await api('/api/jobs?limit=1');
        document.getElementById('stat-jobs').textContent = jobs.total || 0;
    } catch { document.getElementById('stat-jobs').textContent = '0'; }
    try {
        const users = await api('/api/users/?limit=1');
        document.getElementById('stat-users').textContent = users.total || 0;
    } catch { document.getElementById('stat-users').textContent = '0'; }
}

// ── Hero Buttons ────────────────────────────────────────────

document.getElementById('btn-get-started').addEventListener('click', () => {
    if (currentUser) showSection('dashboard');
    else showSection('setup');
});
document.getElementById('btn-view-architecture').addEventListener('click', () => {
    showSection('system');
    checkHealth();
});

// ── File Upload Logic ───────────────────────────────────────
const dropzone = document.getElementById('resume-dropzone');
const fileInput = document.getElementById('input-resume');
const filenameDisplay = document.getElementById('resume-filename');
let selectedFile = null;

dropzone.addEventListener('click', () => fileInput.click());
dropzone.addEventListener('dragover', e => {
    e.preventDefault();
    dropzone.style.borderColor = 'var(--accent-blue)';
    dropzone.style.backgroundColor = 'rgba(10, 102, 194, 0.05)';
});
dropzone.addEventListener('dragleave', () => {
    dropzone.style.borderColor = 'var(--glass-border)';
    dropzone.style.backgroundColor = 'transparent';
});
dropzone.addEventListener('drop', e => {
    e.preventDefault();
    dropzone.style.borderColor = 'var(--glass-border)';
    dropzone.style.backgroundColor = 'transparent';
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener('change', e => {
    if (e.target.files.length) handleFile(e.target.files[0]);
});

function handleFile(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        toast('Please select a PDF file', 'error');
        return;
    }
    selectedFile = file;
    filenameDisplay.textContent = `Selected: ${file.name}`;
    filenameDisplay.style.display = 'block';
    dropzone.style.borderColor = 'var(--accent-green)';
}

// ── Registration ────────────────────────────────────────────

document.getElementById('form-setup').addEventListener('submit', async e => {
    e.preventDefault();
    if (!selectedFile) {
        toast('Please upload your resume PDF first', 'error');
        return;
    }

    const btn = document.getElementById('btn-register');
    btn.disabled = true;
    btn.querySelector('span').textContent = 'Parsing Resume & Creating...';

    try {
        const formData = new FormData();
        formData.append('name', document.getElementById('input-name').value.trim());
        formData.append('email', document.getElementById('input-email').value.trim());
        formData.append('location', document.getElementById('input-location').value.trim() || 'Remote');
        formData.append('file', selectedFile);

        // Note: Using standard fetch here to pass FormData natively instead of the api() helper
        const url = `${API}/api/users/register/resume`;
        const res = await fetch(url, {
            method: 'POST',
            body: formData
            // Don't set Content-Type header manually for FormData
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }

        const user = await res.json();
        currentUser = user;
        localStorage.setItem('jrs_user', JSON.stringify(user));
        toast('Profile created successfully using Resume!', 'success');
        updateUserUI();
        showSection('dashboard');
        loadDashboard();
        loadStats();
    } catch (err) {
        toast(err.message, 'error');
    } finally {
        btn.disabled = false;
        btn.querySelector('span').textContent = 'Create Profile & Get Recommendations';
    }
});

// ── Restore Session ─────────────────────────────────────────

(function restoreSession() {
    try {
        const saved = localStorage.getItem('jrs_user');
        if (saved) { currentUser = JSON.parse(saved); updateUserUI(); }
    } catch {}
})();

function updateUserUI() {
    if (!currentUser) return;
    const initials = currentUser.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
    document.getElementById('user-initials').textContent = initials;
    document.getElementById('profile-initials').textContent = initials;
    document.getElementById('btn-logout').style.display = 'inline-flex';

    document.getElementById('profile-name').textContent = currentUser.name;
    document.getElementById('profile-email').textContent = currentUser.email;
    document.getElementById('profile-experience').textContent = currentUser.experience_years;
    document.getElementById('profile-location').textContent = currentUser.location || 'Not set';

    const skillsEl = document.getElementById('profile-skills');
    skillsEl.innerHTML = (currentUser.skills || []).map(s => `<span class="skill-tag">${s}</span>`).join('');
    
    // Update Full Profile Section
    const fullInitials = document.getElementById('full-profile-initials');
    if (fullInitials) {
        fullInitials.textContent = initials;
        document.getElementById('full-profile-name').textContent = currentUser.name;
        document.getElementById('full-profile-email').textContent = currentUser.email;
        document.getElementById('full-profile-experience').textContent = currentUser.experience_years + ' years';
        document.getElementById('full-profile-location').textContent = currentUser.location || 'Remote';
        document.getElementById('full-profile-skills').innerHTML = (currentUser.skills || []).map(s => `<span class="skill-tag">${s}</span>`).join('');
    }
}

const btnLogout = document.getElementById('btn-logout');
if (btnLogout) {
    btnLogout.addEventListener('click', () => {
        currentUser = null;
        localStorage.removeItem('jrs_user');
        btnLogout.style.display = 'none';
        document.getElementById('user-initials').textContent = '?';
        showSection('hero');
    });
}

// ── Dashboard ───────────────────────────────────────────────

async function loadDashboard() {
    if (!currentUser) return;
    // Refresh user data
    try {
        const user = await api(`/api/users/${currentUser.id}`);
        currentUser = user;
        localStorage.setItem('jrs_user', JSON.stringify(user));
        updateUserUI();
    } catch {}
    loadRecoPreview();
    loadActivity();
}

async function loadRecoPreview() {
    const list = document.getElementById('reco-preview-list');
    try {
        const data = await api(`/api/recommendations/${currentUser.id}?top_n=4`);
        if (!data.recommendations || data.recommendations.length === 0) {
            list.innerHTML = '<p class="empty-state">No recommendations yet. Browse some jobs first!</p>';
            return;
        }
        list.innerHTML = data.recommendations.map(r => renderJobCard(r.job, r.score, r.match_reasons)).join('');
    } catch {
        list.innerHTML = '<p class="empty-state">Could not load recommendations</p>';
    }
}

async function loadActivity() {
    const timeline = document.getElementById('activity-timeline');
    try {
        const data = await api(`/api/users/${currentUser.id}/activity?limit=10`);
        const acts = data.activities || [];
        document.getElementById('activity-count').textContent = `${acts.length} events`;
        if (acts.length === 0) {
            timeline.innerHTML = '<p class="empty-state">No activity yet. Browse jobs to start!</p>';
            return;
        }
        const icons = { job_clicked: '👁️', job_applied: '📨', job_searched: '🔍' };
        timeline.innerHTML = acts.map(a => `
            <div class="timeline-item">
                <span class="timeline-icon">${icons[a.activity_type] || '📌'}</span>
                <span class="timeline-text">${a.activity_type.replace(/_/g, ' ')}${a.job_id ? '' : ''}${a.search_query ? ': "' + a.search_query + '"' : ''}</span>
                <span class="timeline-time">${timeAgo(a.timestamp)}</span>
            </div>
        `).join('');
    } catch {
        timeline.innerHTML = '<p class="empty-state">Could not load activity</p>';
    }
}

document.getElementById('link-view-all-reco').addEventListener('click', e => {
    e.preventDefault();
    showSection('recommendations');
    loadRecommendations();
});

// ── Jobs ────────────────────────────────────────────────────

let jobsCache = [];
async function loadJobs(filters = {}) {
    const grid = document.getElementById('jobs-grid');
    grid.innerHTML = '<div class="skeleton-card"></div><div class="skeleton-card"></div><div class="skeleton-card"></div>';
    try {
        let query = '/api/jobs?limit=50';
        if (filters.experience_level) query += `&experience_level=${filters.experience_level}`;
        if (filters.job_type) query += `&job_type=${filters.job_type}`;
        const data = await api(query);
        jobsCache = data.jobs || [];
        if (jobsCache.length === 0) {
            grid.innerHTML = '<p class="empty-state">No jobs found. Click "Seed Jobs" to add sample data.</p>';
            return;
        }
        grid.innerHTML = jobsCache.map(j => renderJobCard(j)).join('');
    } catch {
        grid.innerHTML = '<p class="empty-state">Could not load jobs. Is the Job Service running?</p>';
    }
}

document.getElementById('btn-seed-jobs').addEventListener('click', async () => {
    try {
        document.getElementById('btn-seed-jobs').textContent = '⏳ Fetching...';
        document.getElementById('btn-seed-jobs').disabled = true;
        const res = await api('/api/jobs/fetch-live', { method: 'POST' });
        toast(res.message, 'success');
        loadJobs();
        loadStats();
    } catch (e) {
        toast('Failed to fetch live jobs', 'error');
    } finally {
        document.getElementById('btn-seed-jobs').textContent = '🔄 Fetch Live Jobs';
        document.getElementById('btn-seed-jobs').disabled = false;
    }
});

document.getElementById('filter-experience').addEventListener('change', () => applyFilters());
document.getElementById('filter-type').addEventListener('change', () => applyFilters());
function applyFilters() {
    loadJobs({
        experience_level: document.getElementById('filter-experience').value,
        job_type: document.getElementById('filter-type').value,
    });
}

let searchTimeout;
document.getElementById('input-search-jobs').addEventListener('input', e => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(async () => {
        const q = e.target.value.trim();
        if (q.length < 2) { loadJobs(); return; }
        try {
            const data = await api(`/api/jobs/search?q=${encodeURIComponent(q)}`);
            const grid = document.getElementById('jobs-grid');
            if (data.jobs.length === 0) { grid.innerHTML = '<p class="empty-state">No results</p>'; return; }
            grid.innerHTML = data.jobs.map(j => renderJobCard(j)).join('');
            // Publish search event
            if (currentUser) {
                api('/api/events/publish', { method: 'POST', body: { event_type: 'job_searched', user_id: currentUser.id, data: { search_query: q } } }).catch(() => {});
            }
        } catch { }
    }, 400);
});

// ── Recommendations ─────────────────────────────────────────

async function loadRecommendations() {
    if (!currentUser) { showSection('setup'); return; }
    const grid = document.getElementById('reco-full-list');
    grid.innerHTML = '<div class="skeleton-card"></div><div class="skeleton-card"></div><div class="skeleton-card"></div>';
    try {
        const data = await api(`/api/recommendations/${currentUser.id}?top_n=20`);
        if (!data.recommendations || data.recommendations.length === 0) {
            grid.innerHTML = '<p class="empty-state">No recommendations yet. Add skills to your profile and browse some jobs!</p>';
            return;
        }
        grid.innerHTML = data.recommendations.map(r => renderRecoCard(r)).join('');
        const src = data.source === 'cache' ? '⚡ From Cache' : '🧠 Freshly Computed';
        toast(`${data.count} recommendations loaded (${src})`, 'info');
    } catch (e) {
        grid.innerHTML = `<p class="empty-state">Error: ${e.message}</p>`;
    }
}

document.getElementById('btn-recalculate').addEventListener('click', async () => {
    if (!currentUser) return;
    try {
        toast('Recalculating...', 'info');
        await api(`/api/recommendations/${currentUser.id}/recalculate`, { method: 'POST' });
        await loadRecommendations();
    } catch (e) { toast(e.message, 'error'); }
});

// ── Render Helpers ──────────────────────────────────────────

function renderJobCard(job, score, reasons) {
    const scoreHTML = score !== undefined ? `<span class="score-badge ${score > 0.3 ? 'score-high' : score > 0.15 ? 'score-mid' : 'score-low'}">${Math.round(score * 100)}% match</span>` : '';
    const reasonsHTML = reasons ? `<div class="match-reasons">${reasons.slice(0, 3).map(r => `<span class="match-reason">✓ ${r}</span>`).join('')}</div>` : '';
    const salary = job.salary_range;
    const salaryStr = salary && salary.min ? `₹${(salary.min / 100000).toFixed(1)}L - ${(salary.max / 100000).toFixed(1)}L` : '';

    return `
        <div class="job-card" onclick="openJob('${job.id}')" style="animation-delay: ${Math.random() * 0.3}s">
            <div class="job-card-header">
                <div>
                    <div class="job-card-title">${esc(job.title)}</div>
                    <div class="job-card-company">${esc(job.company)}</div>
                </div>
                ${scoreHTML}
            </div>
            <div class="job-card-meta">
                <span class="job-meta-tag">📍 ${esc(job.location)}</span>
                <span class="job-meta-tag">💼 ${esc(job.experience_level)}</span>
                ${salaryStr ? `<span class="job-meta-tag">💰 ${salaryStr}</span>` : ''}
                <span class="job-meta-tag">📋 ${esc(job.job_type)}</span>
            </div>
            <div class="job-card-skills">
                ${(job.required_skills || []).slice(0, 5).map(s => `<span class="job-skill-tag">${esc(s)}</span>`).join('')}
                ${job.required_skills && job.required_skills.length > 5 ? `<span class="job-skill-tag">+${job.required_skills.length - 5}</span>` : ''}
            </div>
            ${reasonsHTML}
        </div>
    `;
}

function renderRecoCard(reco) {
    return renderJobCard(reco.job, reco.score, reco.match_reasons);
}

// ── Job Modal ───────────────────────────────────────────────

async function openJob(jobId) {
    const modal = document.getElementById('job-modal');
    const body = document.getElementById('modal-body');
    modal.classList.remove('hidden');

    // Publish click event
    if (currentUser) {
        api('/api/events/publish', { method: 'POST', body: { event_type: 'job_clicked', user_id: currentUser.id, data: { job_id: jobId } } }).catch(() => {});
    }

    try {
        const job = await api(`/api/jobs/${jobId}`);
        const salary = job.salary_range;
        const salaryStr = salary && salary.min ? `₹${(salary.min / 100000).toFixed(1)}L - ${(salary.max / 100000).toFixed(1)}L` : 'Not disclosed';

        body.innerHTML = `
            <h2 class="modal-title">${esc(job.title)}</h2>
            <p class="modal-company">${esc(job.company)}</p>
            <div class="modal-section">
                <h4>Description</h4>
                <p>${esc(job.description)}</p>
            </div>
            <div class="modal-section">
                <h4>Required Skills</h4>
                <div class="profile-skills">${(job.required_skills || []).map(s => `<span class="skill-tag">${esc(s)}</span>`).join('')}</div>
            </div>
            <div class="modal-section">
                <h4>Details</h4>
                <p>📍 ${esc(job.location)} &nbsp;|&nbsp; 💼 ${esc(job.experience_level)} &nbsp;|&nbsp; 📋 ${esc(job.job_type)} &nbsp;|&nbsp; 💰 ${salaryStr}</p>
            </div>
            <div class="modal-actions">
                <button class="btn btn-primary" onclick="applyJob('${job.id}')">📨 Apply Now</button>
                <button class="btn btn-outline" onclick="closeModal()">Close</button>
            </div>
        `;
    } catch {
        body.innerHTML = '<p class="empty-state">Could not load job details</p>';
    }
}

window.applyJob = async function(jobId) {
    if (!currentUser) { toast('Please register first', 'error'); return; }
    try {
        await api('/api/events/publish', { method: 'POST', body: { event_type: 'job_applied', user_id: currentUser.id, data: { job_id: jobId } } });
        await api(`/api/users/${currentUser.id}/activity`, { method: 'POST', body: { activity_type: 'job_applied', job_id: jobId } });
        toast('Application submitted! Recommendations will update.', 'success');
        closeModal();
    } catch (e) { toast(e.message, 'error'); }
};

function closeModal() { document.getElementById('job-modal').classList.add('hidden'); }
document.getElementById('modal-overlay').addEventListener('click', closeModal);
document.getElementById('modal-close').addEventListener('click', closeModal);
window.openJob = openJob;
window.closeModal = closeModal;

// ── Health Checks ───────────────────────────────────────────

async function checkHealth() {
    const checks = [
        { id: 'status-gateway', url: '/api/health' },
        { id: 'status-user', url: '/api/users/?limit=1' },
        { id: 'status-job', url: '/api/jobs?limit=1' },
        { id: 'status-reco', url: '/api/recommendations/similar-jobs/test' },
    ];
    for (const c of checks) {
        const el = document.getElementById(c.id);
        try {
            await api(c.url);
            el.textContent = 'healthy';
            el.className = 'system-status status-healthy';
        } catch {
            el.textContent = 'down';
            el.className = 'system-status';
            el.style.background = 'rgba(239,68,68,0.15)';
            el.style.color = '#ef4444';
        }
    }
}

// ── Toast Notifications ─────────────────────────────────────

function toast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const icons = { success: '✅', error: '❌', info: 'ℹ️' };
    const t = document.createElement('div');
    t.className = `toast toast-${type}`;
    t.innerHTML = `<span>${icons[type] || ''}</span><span>${esc(message)}</span>`;
    container.appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateX(50px)'; setTimeout(() => t.remove(), 300); }, 4000);
}

// ── Utilities ───────────────────────────────────────────────

function esc(str) { if (!str) return ''; const d = document.createElement('div'); d.textContent = str; return d.innerHTML; }

function timeAgo(ts) {
    if (!ts) return '';
    const diff = (Date.now() - new Date(ts).getTime()) / 1000;
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
}
