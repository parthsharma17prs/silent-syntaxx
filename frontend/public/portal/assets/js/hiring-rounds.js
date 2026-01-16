/**
 * Hiring Rounds Configuration - Production JavaScript
 * Handles multi-step form, drag-and-drop, validation, and API integration
 */

const API_BASE_URL = 'http://localhost:5000/api';
let currentStep = 1;
let jobData = null;
let rounds = [];
let jobId = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Get job ID from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    jobId = urlParams.get('jobId');
    
    if (!jobId) {
        showError('No job ID provided. Redirecting to dashboard...');
        setTimeout(() => window.location.href = 'company.html', 2000);
        return;
    }
    
    // Load job details and existing rounds
    loadJobDetails();
    loadExistingRounds();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize with one empty round if none exist
    if (rounds.length === 0) {
        addNewRound();
    }
});

/**
 * Load job details from API
 */
async function loadJobDetails() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE_URL}/company/jobs`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        }).catch(networkError => {
            throw new Error('Cannot connect to server. Please ensure the backend is running on http://localhost:5000');
        });
        
        if (!response.ok) throw new Error('Failed to load job details');
        
        const data = await response.json();
        // Find the specific job (data is already an array of jobs)
        jobData = data.find(job => job.id == jobId);
        
        if (!jobData) {
            throw new Error('Job not found');
        }
        
        displayJobOverview(jobData);
    } catch (error) {
        console.error('Error loading job details:', error);
        showError('Failed to load job details');
    }
}

/**
 * Load existing rounds if any
 */
async function loadExistingRounds() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE_URL}/company/hiring-rounds/job/${jobId}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        }).catch(networkError => {
            throw new Error('Cannot connect to server. Please ensure the backend is running on http://localhost:5000');
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.rounds && data.rounds.length > 0) {
                rounds = data.rounds;
                renderRounds();
            }
        }
    } catch (error) {
        console.error('Error loading existing rounds:', error);
    }
}

/**
 * Display job overview in Step 1
 */
function displayJobOverview(job) {
    document.getElementById('jobTitleDisplay').textContent = `for ${job.title}`;
    
    const overviewHtml = `
        <div class="overview-section">
            <h3>Basic Information</h3>
            <div class="info-row">
                <span class="info-label">Job Title:</span>
                <span class="info-value">${job.title}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Job Type:</span>
                <span class="info-value">${job.job_type}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Location:</span>
                <span class="info-value">${job.location || 'Not specified'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Salary Range:</span>
                <span class="info-value">${job.salary_range || 'Not specified'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Application Deadline:</span>
                <span class="info-value">${formatDate(job.application_deadline)}</span>
            </div>
        </div>
        <div class="overview-section">
            <h3>Eligibility Criteria</h3>
            <div class="info-row">
                <span class="info-label">Minimum CGPA:</span>
                <span class="info-value">${job.min_cgpa}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Eligible Branches:</span>
                <span class="info-value">${job.eligible_branches || 'All'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Status:</span>
                <span class="info-value" style="color: ${getStatusColor(job.status)}; font-weight: 600;">
                    ${job.status}
                </span>
            </div>
        </div>
    `;
    
    document.getElementById('jobOverview').innerHTML = overviewHtml;
}

/**
 * Add a new round to the configuration
 */
function addNewRound() {
    const roundNumber = rounds.length + 1;
    const newRound = {
        round_number: roundNumber,
        round_name: `Round ${roundNumber}`,
        round_type: 'Online',
        round_mode: 'Interview',
        description: '',
        duration_minutes: 60,
        evaluation_criteria: [],
        is_elimination_round: true,
        scheduled_date: '',
        scheduled_time: '',
        venue: '',
        status: 'Draft',
        min_passing_score: 60,
        max_score: 100,
        configuration: {}
    };
    
    rounds.push(newRound);
    renderRounds();
}

/**
 * Render all rounds in the UI
 */
function renderRounds() {
    const container = document.getElementById('roundsContainer');
    
    if (rounds.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📋</div>
                <h3>No rounds configured yet</h3>
                <p>Click "Add Another Round" to start building your hiring process</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = rounds.map((round, index) => `
        <div class="round-card" draggable="true" data-round-index="${index}">
            <div class="round-header">
                <div class="round-title">
                    <span class="drag-handle" title="Drag to reorder">☰</span>
                    <div class="round-number">${round.round_number}</div>
                    <input 
                        type="text" 
                        class="round-name-input" 
                        value="${round.round_name}"
                        onchange="updateRound(${index}, 'round_name', this.value)"
                        placeholder="Round Name"
                    />
                </div>
                <div class="round-actions">
                    <button class="btn btn-danger btn-icon" onclick="deleteRound(${index})" title="Delete Round">
                        🗑️
                    </button>
                </div>
            </div>
            
            <div class="round-form">
                <div class="form-group">
                    <label>
                        Round Type <span class="required">*</span>
                    </label>
                    <select onchange="updateRound(${index}, 'round_type', this.value)" required>
                        <option value="Online" ${round.round_type === 'Online' ? 'selected' : ''}>Online</option>
                        <option value="Offline" ${round.round_type === 'Offline' ? 'selected' : ''}>Offline</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>
                        Round Mode <span class="required">*</span>
                    </label>
                    <select onchange="updateRound(${index}, 'round_mode', this.value)" required>
                        <option value="MCQ" ${round.round_mode === 'MCQ' ? 'selected' : ''}>MCQ Test</option>
                        <option value="Coding" ${round.round_mode === 'Coding' ? 'selected' : ''}>Coding Challenge</option>
                        <option value="Interview" ${round.round_mode === 'Interview' ? 'selected' : ''}>Interview</option>
                        <option value="Group Discussion" ${round.round_mode === 'Group Discussion' ? 'selected' : ''}>Group Discussion</option>
                        <option value="Assignment" ${round.round_mode === 'Assignment' ? 'selected' : ''}>Assignment</option>
                        <option value="Case Study" ${round.round_mode === 'Case Study' ? 'selected' : ''}>Case Study</option>
                        <option value="Presentation" ${round.round_mode === 'Presentation' ? 'selected' : ''}>Presentation</option>
                        <option value="Other" ${round.round_mode === 'Other' ? 'selected' : ''}>Other</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Duration (minutes)</label>
                    <input 
                        type="number" 
                        value="${round.duration_minutes || ''}" 
                        onchange="updateRound(${index}, 'duration_minutes', parseInt(this.value))"
                        placeholder="60"
                        min="1"
                    />
                </div>
                
                <div class="form-group">
                    <label>Minimum Passing Score (%)</label>
                    <input 
                        type="number" 
                        value="${round.min_passing_score || ''}" 
                        onchange="updateRound(${index}, 'min_passing_score', parseFloat(this.value))"
                        placeholder="60"
                        min="0"
                        max="100"
                        step="0.01"
                    />
                </div>
                
                <div class="form-group">
                    <label>Scheduled Date</label>
                    <input 
                        type="date" 
                        value="${round.scheduled_date || ''}" 
                        onchange="updateRound(${index}, 'scheduled_date', this.value)"
                    />
                </div>
                
                <div class="form-group">
                    <label>Scheduled Time</label>
                    <input 
                        type="time" 
                        value="${round.scheduled_time || ''}" 
                        onchange="updateRound(${index}, 'scheduled_time', this.value)"
                    />
                </div>
                
                <div class="form-group full-width">
                    <label>Venue / Meeting Link</label>
                    <input 
                        type="text" 
                        value="${round.venue || ''}" 
                        onchange="updateRound(${index}, 'venue', this.value)"
                        placeholder="Physical location or online meeting link"
                    />
                </div>
                
                <div class="form-group full-width">
                    <label>Description / Instructions</label>
                    <textarea 
                        onchange="updateRound(${index}, 'description', this.value)"
                        placeholder="Provide detailed instructions for candidates..."
                    >${round.description || ''}</textarea>
                </div>
                
                <div class="form-group full-width">
                    <div class="checkbox-group">
                        <input 
                            type="checkbox" 
                            id="elimination_${index}"
                            ${round.is_elimination_round ? 'checked' : ''}
                            onchange="updateRound(${index}, 'is_elimination_round', this.checked)"
                        />
                        <label for="elimination_${index}" style="margin: 0;">
                            This is an elimination round (candidates who don't pass will be removed)
                        </label>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    // Set up drag and drop
    setupDragAndDrop();
}

/**
 * Update a specific field in a round
 */
function updateRound(index, field, value) {
    if (rounds[index]) {
        rounds[index][field] = value;
    }
}

/**
 * Delete a round
 */
function deleteRound(index) {
    if (confirm('Are you sure you want to delete this round?')) {
        rounds.splice(index, 1);
        // Renumber remaining rounds
        rounds.forEach((round, idx) => {
            round.round_number = idx + 1;
            round.round_name = round.round_name.replace(/Round \d+/, `Round ${idx + 1}`);
        });
        renderRounds();
    }
}

/**
 * Set up drag and drop functionality
 */
function setupDragAndDrop() {
    const roundCards = document.querySelectorAll('.round-card');
    
    roundCards.forEach(card => {
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragover', handleDragOver);
        card.addEventListener('drop', handleDrop);
        card.addEventListener('dragend', handleDragEnd);
    });
}

let draggedElement = null;

function handleDragStart(e) {
    draggedElement = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    return false;
}

function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    
    if (draggedElement !== this) {
        const fromIndex = parseInt(draggedElement.dataset.roundIndex);
        const toIndex = parseInt(this.dataset.roundIndex);
        
        // Reorder rounds array
        const [movedRound] = rounds.splice(fromIndex, 1);
        rounds.splice(toIndex, 0, movedRound);
        
        // Renumber rounds
        rounds.forEach((round, idx) => {
            round.round_number = idx + 1;
        });
        
        renderRounds();
    }
    
    return false;
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
}

/**
 * Navigation between steps
 */
function nextStep() {
    // Validate current step
    if (currentStep === 2) {
        if (!validateRounds()) {
            return;
        }
    }
    
    if (currentStep < 3) {
        currentStep++;
        updateStepDisplay();
        
        if (currentStep === 3) {
            renderReviewSection();
        }
    }
}

function previousStep() {
    if (currentStep > 1) {
        currentStep--;
        updateStepDisplay();
    }
}

function updateStepDisplay() {
    // Update stepper
    document.querySelectorAll('.step').forEach(step => {
        const stepNum = parseInt(step.dataset.step);
        step.classList.remove('active', 'completed');
        
        if (stepNum === currentStep) {
            step.classList.add('active');
        } else if (stepNum < currentStep) {
            step.classList.add('completed');
        }
    });
    
    // Update content
    document.querySelectorAll('.step-content-inner').forEach(content => {
        content.classList.remove('active');
    });
    document.querySelector(`.step-content-inner[data-step="${currentStep}"]`).classList.add('active');
}

/**
 * Validate rounds configuration
 */
function validateRounds() {
    if (rounds.length === 0) {
        alert('Please add at least one round to continue.');
        return false;
    }
    
    for (let i = 0; i < rounds.length; i++) {
        const round = rounds[i];
        
        if (!round.round_name || round.round_name.trim() === '') {
            alert(`Round ${i + 1}: Please provide a round name.`);
            return false;
        }
        
        if (!round.round_type) {
            alert(`Round ${i + 1}: Please select a round type.`);
            return false;
        }
        
        if (!round.round_mode) {
            alert(`Round ${i + 1}: Please select a round mode.`);
            return false;
        }
    }
    
    return true;
}

/**
 * Render review section
 */
function renderReviewSection() {
    document.getElementById('totalRoundsCount').textContent = `${rounds.length} Round${rounds.length !== 1 ? 's' : ''} Configured`;
    
    const reviewHtml = rounds.map((round, index) => `
        <div class="round-summary">
            <div class="round-summary-header">
                <h4>
                    <span style="color: var(--primary-color);">Round ${round.round_number}:</span> 
                    ${round.round_name}
                </h4>
                <button class="btn btn-secondary btn-icon" onclick="editRound(${index})" title="Edit">
                    ✏️
                </button>
            </div>
            <div class="round-details">
                <div class="detail-item">
                    <span class="detail-label">Type</span>
                    <span class="detail-value">${round.round_type}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Mode</span>
                    <span class="detail-value">${round.round_mode}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Duration</span>
                    <span class="detail-value">${round.duration_minutes ? round.duration_minutes + ' min' : 'Not set'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Elimination</span>
                    <span class="detail-value">${round.is_elimination_round ? 'Yes' : 'No'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Passing Score</span>
                    <span class="detail-value">${round.min_passing_score ? round.min_passing_score + '%' : 'Not set'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Scheduled</span>
                    <span class="detail-value">
                        ${round.scheduled_date ? formatDate(round.scheduled_date) : 'Not scheduled'}
                    </span>
                </div>
            </div>
            ${round.description ? `
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border-color);">
                    <span class="detail-label">Description:</span>
                    <p style="margin-top: 0.5rem; color: var(--text-primary);">${round.description}</p>
                </div>
            ` : ''}
        </div>
    `).join('');
    
    document.getElementById('reviewRounds').innerHTML = reviewHtml;
}

/**
 * Edit a round from review page
 */
function editRound(index) {
    currentStep = 2;
    updateStepDisplay();
    // Scroll to the specific round
    setTimeout(() => {
        const roundCards = document.querySelectorAll('.round-card');
        if (roundCards[index]) {
            roundCards[index].scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }, 100);
}

/**
 * Submit configuration to API
 */
async function submitConfiguration() {
    if (!validateRounds()) {
        return;
    }
    
    // Confirm submission
    if (!confirm(`Are you sure you want to submit this configuration with ${rounds.length} round(s)?`)) {
        return;
    }
    
    const loadingEl = document.getElementById('submitLoading');
    loadingEl.classList.add('show');
    
    try {
        const token = localStorage.getItem('token');
        
        // Log the data being sent
        console.log('Submitting rounds configuration:', {
            jobId,
            rounds,
            roundsCount: rounds.length
        });
        
        const response = await fetch(`${API_BASE_URL}/company/hiring-rounds/job/${jobId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ rounds })
        }).catch(networkError => {
            throw new Error('Cannot connect to server. Please ensure the backend is running on http://localhost:5000');
        });
        
        const data = await response.json();
        
        console.log('API Response:', {
            status: response.status,
            ok: response.ok,
            data
        });
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to save configuration');
        }
        
        // Success!
        loadingEl.classList.remove('show');
        alert('✓ Hiring process configured successfully!');
        
        // Redirect to company dashboard
        window.location.href = 'company.html';
        
    } catch (error) {
        loadingEl.classList.remove('show');
        console.error('Error submitting configuration:', error);
        alert('Error: ' + error.message);
    }
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Prevent accidental navigation away
    window.addEventListener('beforeunload', (e) => {
        if (currentStep === 2 && rounds.length > 0) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
}

/**
 * Utility Functions
 */
function formatDate(dateString) {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

function getStatusColor(status) {
    const colors = {
        'Approved': '#10b981',
        'Pending': '#f59e0b',
        'Rejected': '#ef4444',
        'Closed': '#6b7280'
    };
    return colors[status] || '#6b7280';
}

function showError(message) {
    alert('Error: ' + message);
}
