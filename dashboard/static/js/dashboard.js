// Dashboard JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard
    initializeDashboard();
    
    // Add smooth scrolling for navigation links
    addSmoothScrolling();
    
    // Add loading states for buttons
    addLoadingStates();
    
    // Add search functionality
    addSearchFunctionality();
    
    // Add filter functionality
    addFilterFunctionality();
});

function initializeDashboard() {
    console.log('🚀 GitHub PR Analytics Dashboard initialized');
    
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
    
    // Add hover effects
    addHoverEffects();
}

function addSmoothScrolling() {
    const navLinks = document.querySelectorAll('a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function addLoadingStates() {
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.classList.contains('btn-loading')) return;
            
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="loading"></span> Loading...';
            this.classList.add('btn-loading');
            this.disabled = true;
            
            // Reset after 3 seconds (for demo purposes)
            setTimeout(() => {
                this.innerHTML = originalText;
                this.classList.remove('btn-loading');
                this.disabled = false;
            }, 3000);
        });
    });
}

function addHoverEffects() {
    // Add hover effects to cards
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

function addSearchFunctionality() {
    // Create search input
    const searchContainer = document.createElement('div');
    searchContainer.className = 'search-container mb-4';
    searchContainer.innerHTML = `
        <div class="input-group">
            <span class="input-group-text">
                <i class="fas fa-search"></i>
            </span>
            <input type="text" class="form-control" id="searchInput" 
                   placeholder="Search reports, visualizations, or insights...">
        </div>
    `;
    
    // Insert search container after hero section
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        heroSection.parentNode.insertBefore(searchContainer, heroSection.nextSibling);
    }
    
    // Add search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            filterItems(searchTerm);
        });
    }
}

function filterItems(searchTerm) {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        const text = card.textContent.toLowerCase();
        const title = card.querySelector('.card-title')?.textContent.toLowerCase() || '';
        const category = card.querySelector('.badge')?.textContent.toLowerCase() || '';
        
        if (text.includes(searchTerm) || title.includes(searchTerm) || category.includes(searchTerm)) {
            card.style.display = 'block';
            card.style.opacity = '1';
        } else {
            card.style.display = 'none';
            card.style.opacity = '0';
        }
    });
}

function addFilterFunctionality() {
    // Add filter buttons for each section
    const sections = ['reports', 'visualizations', 'insights'];
    
    sections.forEach(section => {
        const sectionElement = document.getElementById(section);
        if (sectionElement) {
            const filterContainer = document.createElement('div');
            filterContainer.className = 'filter-container mb-3';
            filterContainer.innerHTML = `
                <div class="btn-group" role="group">
                    <button type="button" class="btn btn-outline-primary btn-sm active" 
                            data-filter="all">All</button>
                    <button type="button" class="btn btn-outline-primary btn-sm" 
                            data-filter="recent">Recent</button>
                    <button type="button" class="btn btn-outline-primary btn-sm" 
                            data-filter="popular">Popular</button>
                </div>
            `;
            
            const sectionTitle = sectionElement.querySelector('.section-title');
            if (sectionTitle) {
                sectionTitle.parentNode.insertBefore(filterContainer, sectionTitle.nextSibling);
            }
            
            // Add filter functionality
            const filterButtons = filterContainer.querySelectorAll('[data-filter]');
            filterButtons.forEach(button => {
                button.addEventListener('click', function() {
                    // Remove active class from all buttons
                    filterButtons.forEach(btn => btn.classList.remove('active'));
                    // Add active class to clicked button
                    this.classList.add('active');
                    
                    const filter = this.getAttribute('data-filter');
                    filterSectionItems(section, filter);
                });
            });
        }
    });
}

function filterSectionItems(section, filter) {
    const sectionElement = document.getElementById(section);
    const cards = sectionElement.querySelectorAll('.card');
    
    cards.forEach(card => {
        switch (filter) {
            case 'recent':
                // Show only recent items (last 7 days)
                const createdAt = card.querySelector('.text-muted')?.textContent;
                if (createdAt && isRecent(createdAt)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
                break;
            case 'popular':
                // Show items with high activity (based on badges or counts)
                const badge = card.querySelector('.badge');
                if (badge && (badge.textContent.includes('Multi') || badge.textContent.includes('High'))) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
                break;
            default:
                // Show all items
                card.style.display = 'block';
        }
    });
}

function isRecent(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays <= 7;
}

// Chart loading functionality
function loadCharts(filename) {
    const modal = document.getElementById('chartsModal');
    const container = document.getElementById('chartsContainer');
    
    // Show loading state
    container.innerHTML = '<div class="text-center py-5"><div class="loading"></div><p class="mt-3">Loading charts...</p></div>';
    
    // Fetch chart data
    fetch(`/api/charts/${filename}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            container.innerHTML = '';
            
            Object.keys(data).forEach(chartKey => {
                const chartDiv = document.createElement('div');
                chartDiv.className = 'mb-4';
                chartDiv.id = `chart-${chartKey}`;
                container.appendChild(chartDiv);
                
                // Create Plotly chart
                Plotly.newPlot(`chart-${chartKey}`, data[chartKey].data, data[chartKey].layout);
            });
            
            // Show modal
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        })
        .catch(error => {
            console.error('Error loading charts:', error);
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-exclamation-triangle text-warning display-4 mb-3"></i>
                    <h5>Error Loading Charts</h5>
                    <p class="text-muted">Unable to load interactive charts. Please try again.</p>
                    <button class="btn btn-primary" onclick="loadCharts('${filename}')">
                        <i class="fas fa-redo me-1"></i>Retry
                    </button>
                </div>
            `;
            
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        });
}

// Export functionality
function exportData(type, filename) {
    const data = {
        type: type,
        filename: filename,
        timestamp: new Date().toISOString()
    };
    
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `${type}_${filename}_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

// Add CSS for loading state
const style = document.createElement('style');
style.textContent = `
    .btn-loading {
        pointer-events: none;
        opacity: 0.7;
    }
    
    .search-container {
        max-width: 600px;
        margin: 0 auto;
    }
    
    .filter-container {
        display: flex;
        justify-content: center;
    }
`;
document.head.appendChild(style); 