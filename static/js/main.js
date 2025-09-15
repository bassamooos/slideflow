/**
 * Slideflow Web Application - Main JavaScript
 * تطبيق Slideflow الويب - جافاسكريبت الرئيسي
 */

// Global Variables
const API_BASE_URL = '';
let currentTheme = 'light';
let systemInfo = {};

// Initialize Application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadSystemInfo();
    setupTooltips();
    setupProgressBars();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('🔬 Slideflow Web Application initialized');
    
    // Add fade-in animation to main content
    const main = document.querySelector('main');
    if (main) {
        main.classList.add('fade-in');
    }
    
    // Setup theme from localStorage
    const savedTheme = localStorage.getItem('slideflow-theme');
    if (savedTheme) {
        setTheme(savedTheme);
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Form submissions
    const forms = document.querySelectorAll('form[data-ajax]');
    forms.forEach(form => {
        form.addEventListener('submit', handleAjaxForm);
    });
    
    // Navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            updateActiveNavLink(this);
        });
    });
    
    // Search functionality
    const searchInput = document.querySelector('#searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }
    
    // Copy to clipboard buttons
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(button => {
        button.addEventListener('click', handleCopyToClipboard);
    });
}

/**
 * Load system information
 */
async function loadSystemInfo() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/system_info`);
        if (response.ok) {
            systemInfo = await response.json();
            updateSystemInfoDisplay();
        }
    } catch (error) {
        console.error('Error loading system info:', error);
        showNotification('خطأ في تحميل معلومات النظام', 'error');
    }
}

/**
 * Update system info display
 */
function updateSystemInfoDisplay() {
    const systemInfoElement = document.getElementById('system-info');
    if (systemInfoElement && systemInfo) {
        if (systemInfo.slideflow_available) {
            systemInfoElement.innerHTML = `
                <i class="bi bi-check-circle text-success me-1"></i>
                Slideflow ${systemInfo.slideflow_version || 'Unknown'} متاح
            `;
        } else {
            systemInfoElement.innerHTML = `
                <i class="bi bi-x-circle text-warning me-1"></i>
                Slideflow غير متاح
            `;
        }
    }
}

/**
 * Setup tooltips
 */
function setupTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Setup progress bars with animation
 */
function setupProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar[data-animate]');
    progressBars.forEach(bar => {
        const targetWidth = bar.getAttribute('aria-valuenow');
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.width = targetWidth + '%';
        }, 500);
    });
}

/**
 * Handle AJAX form submissions
 */
async function handleAjaxForm(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>جاري المعالجة...';
    
    try {
        const formData = new FormData(form);
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification('تم بنجاح!', 'success');
            
            // Handle successful response
            if (result.redirect) {
                window.location.href = result.redirect;
            }
        } else {
            throw new Error('Network response was not ok');
        }
    } catch (error) {
        console.error('Form submission error:', error);
        showNotification('حدث خطأ أثناء المعالجة', 'error');
    } finally {
        // Reset button state
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;
    }
}

/**
 * Update active navigation link
 */
function updateActiveNavLink(clickedLink) {
    // Remove active class from all nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Add active class to clicked link
    clickedLink.classList.add('active');
}

/**
 * Handle search functionality
 */
function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    const searchResults = document.querySelector('#searchResults');
    
    if (searchTerm.length < 2) {
        if (searchResults) {
            searchResults.innerHTML = '';
        }
        return;
    }
    
    // Implement search logic here
    console.log('Searching for:', searchTerm);
}

/**
 * Handle copy to clipboard
 */
function handleCopyToClipboard(event) {
    const button = event.target.closest('button');
    const textToCopy = button.getAttribute('data-copy') || 
                      button.getAttribute('data-clipboard-text') ||
                      document.querySelector(button.getAttribute('data-clipboard-target'))?.textContent;
    
    if (textToCopy) {
        navigator.clipboard.writeText(textToCopy).then(() => {
            showNotification('تم النسخ بنجاح!', 'success');
            
            // Visual feedback
            const originalHTML = button.innerHTML;
            button.innerHTML = '<i class="bi bi-check text-success"></i>';
            setTimeout(() => {
                button.innerHTML = originalHTML;
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy: ', err);
            showNotification('فشل في النسخ', 'error');
        });
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    const iconClass = {
        success: 'bi-check-circle',
        error: 'bi-exclamation-triangle',
        warning: 'bi-exclamation-triangle',
        info: 'bi-info-circle'
    }[type] || 'bi-info-circle';
    
    notification.innerHTML = `
        <i class="bi ${iconClass} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Format timestamp
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return new Intl.DateTimeFormat('ar-SA', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

/**
 * Set application theme
 */
function setTheme(theme) {
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('slideflow-theme', theme);
    
    // Update theme toggle button if exists
    const themeToggle = document.querySelector('#themeToggle');
    if (themeToggle) {
        themeToggle.innerHTML = theme === 'dark' ? 
            '<i class="bi bi-sun"></i>' : 
            '<i class="bi bi-moon"></i>';
    }
}

/**
 * Toggle theme
 */
function toggleTheme() {
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
}

/**
 * API Helper Functions
 */
const API = {
    /**
     * Extract tiles
     */
    async extractTiles(projectName, options = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/extract_tiles`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    project_name: projectName,
                    ...options
                })
            });
            
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('API request failed');
            }
        } catch (error) {
            console.error('Extract tiles error:', error);
            showNotification('خطأ في استخراج البلاط', 'error');
            throw error;
        }
    },
    
    /**
     * Train model
     */
    async trainModel(projectName, options = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/train_model`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    project_name: projectName,
                    ...options
                })
            });
            
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('API request failed');
            }
        } catch (error) {
            console.error('Train model error:', error);
            showNotification('خطأ في تدريب النموذج', 'error');
            throw error;
        }
    }
};

/**
 * Utility Functions
 */
const Utils = {
    /**
     * Validate form data
     */
    validateForm(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    },
    
    /**
     * Generate unique ID
     */
    generateId() {
        return 'slideflow_' + Math.random().toString(36).substr(2, 9);
    },
    
    /**
     * Scroll to element
     */
    scrollTo(element, offset = 0) {
        const targetElement = typeof element === 'string' ? 
                            document.querySelector(element) : element;
        
        if (targetElement) {
            const elementPosition = targetElement.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - offset;
            
            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    }
};

// Export for use in other scripts
window.SlideflowApp = {
    API,
    Utils,
    showNotification,
    setTheme,
    toggleTheme,
    formatFileSize,
    formatTimestamp
};