// Main JavaScript for Project Evaluator Application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        if (!alert.querySelector('.btn-close')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form validation helpers
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Character counter for text fields
    const textAreas = document.querySelectorAll('textarea[maxlength], input[maxlength]');
    textAreas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        if (maxLength) {
            const counter = document.createElement('div');
            counter.className = 'form-text text-end';
            counter.innerHTML = `<span class="char-count">0</span>/${maxLength} caractères`;
            textarea.parentNode.appendChild(counter);

            const updateCounter = () => {
                const current = textarea.value.length;
                const span = counter.querySelector('.char-count');
                span.textContent = current;
                
                if (current > maxLength * 0.9) {
                    span.className = 'char-count text-warning';
                } else if (current === maxLength) {
                    span.className = 'char-count text-danger';
                } else {
                    span.className = 'char-count text-muted';
                }
            };

            textarea.addEventListener('input', updateCounter);
            updateCounter();
        }
    });

    // Progress bar animations
    const progressBars = document.querySelectorAll('.progress-bar');
    const animateProgressBars = () => {
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = width;
            }, 100);
        });
    };

    // Trigger animation when progress bars come into view
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const progressObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateProgressBars();
                progressObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    progressBars.forEach(bar => {
        progressObserver.observe(bar.parentElement);
    });

    // Loading states for buttons
    const loadingButtons = document.querySelectorAll('[data-loading-text]');
    loadingButtons.forEach(button => {
        button.addEventListener('click', function() {
            const originalText = this.innerHTML;
            const loadingText = this.getAttribute('data-loading-text');
            
            this.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>${loadingText}`;
            this.disabled = true;
            
            // Reset after 30 seconds (timeout)
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 30000);
        });
    });

    // Table sorting (basic)
    const sortableHeaders = document.querySelectorAll('[data-sort]');
    sortableHeaders.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const table = this.closest('table');
            const column = this.getAttribute('data-sort');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            const isAscending = this.classList.contains('sort-asc');
            
            // Remove sort classes from all headers
            sortableHeaders.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
            
            // Add appropriate class to current header
            this.classList.add(isAscending ? 'sort-desc' : 'sort-asc');
            
            rows.sort((a, b) => {
                const aValue = a.querySelector(`[data-value="${column}"]`)?.textContent || '';
                const bValue = b.querySelector(`[data-value="${column}"]`)?.textContent || '';
                
                const comparison = aValue.localeCompare(bValue, 'fr', { numeric: true });
                return isAscending ? -comparison : comparison;
            });
            
            // Re-append sorted rows
            rows.forEach(row => tbody.appendChild(row));
        });
    });

    // Auto-save form data to sessionStorage
    const formsToSave = document.querySelectorAll('form[data-auto-save]');
    formsToSave.forEach(form => {
        const formId = form.getAttribute('data-auto-save');
        const savedData = sessionStorage.getItem(`form_${formId}`);
        
        // Restore saved data
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                Object.keys(data).forEach(key => {
                    const element = form.querySelector(`[name="${key}"]`);
                    if (element) {
                        element.value = data[key];
                    }
                });
            } catch (e) {
                console.warn('Error restoring form data:', e);
            }
        }
        
        // Save data on input
        form.addEventListener('input', function() {
            const formData = new FormData(this);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            sessionStorage.setItem(`form_${formId}`, JSON.stringify(data));
        });
        
        // Clear saved data on successful submit
        form.addEventListener('submit', function() {
            sessionStorage.removeItem(`form_${formId}`);
        });
    });

    // Confirm dialogs for destructive actions
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const target = this.getAttribute('data-copy');
            const element = document.querySelector(target);
            
            if (element) {
                const text = element.textContent || element.value;
                navigator.clipboard.writeText(text).then(() => {
                    // Show tooltip or flash message
                    const originalTitle = this.getAttribute('title');
                    this.setAttribute('title', 'Copié !');
                    const tooltip = bootstrap.Tooltip.getInstance(this);
                    if (tooltip) {
                        tooltip.setContent({ '.tooltip-inner': 'Copié !' });
                        tooltip.show();
                        setTimeout(() => {
                            this.setAttribute('title', originalTitle);
                            tooltip.setContent({ '.tooltip-inner': originalTitle });
                        }, 2000);
                    }
                }).catch(err => {
                    console.error('Error copying text: ', err);
                });
            }
        });
    });

    // Number formatting for Quebec French
    const formatNumber = (number) => {
        return new Intl.NumberFormat('fr-CA', {
            minimumFractionDigits: 1,
            maximumFractionDigits: 1
        }).format(number);
    };

    // Format currency for Quebec French
    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('fr-CA', {
            style: 'currency',
            currency: 'CAD'
        }).format(amount);
    };

    // Debounce function for search inputs
    const debounce = (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };

    // Search functionality
    const searchInputs = document.querySelectorAll('[data-search]');
    searchInputs.forEach(input => {
        const target = input.getAttribute('data-search');
        const searchTarget = document.querySelector(target);
        
        if (searchTarget) {
            const searchFunction = debounce((query) => {
                const rows = searchTarget.querySelectorAll('tbody tr, .search-item');
                
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    const matches = text.includes(query.toLowerCase());
                    row.style.display = matches ? '' : 'none';
                });
            }, 300);
            
            input.addEventListener('input', (e) => {
                searchFunction(e.target.value);
            });
        }
    });

    // Print functionality
    const printButtons = document.querySelectorAll('[data-print]');
    printButtons.forEach(button => {
        button.addEventListener('click', function() {
            const target = this.getAttribute('data-print');
            if (target) {
                const element = document.querySelector(target);
                if (element) {
                    const printWindow = window.open('', '_blank');
                    printWindow.document.write(`
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Impression - ${document.title}</title>
                            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                            <link href="${window.location.origin}/static/css/style.css" rel="stylesheet">
                        </head>
                        <body class="p-4">
                            ${element.outerHTML}
                        </body>
                        </html>
                    `);
                    printWindow.document.close();
                    printWindow.print();
                }
            } else {
                window.print();
            }
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + N for new project
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            const newProjectLink = document.querySelector('a[href*="new_project"]');
            if (newProjectLink) {
                window.location.href = newProjectLink.href;
            }
        }
        
        // Ctrl/Cmd + H for home
        if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
            e.preventDefault();
            const homeLink = document.querySelector('a[href="/"], a[href*="index"]');
            if (homeLink) {
                window.location.href = homeLink.href;
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        }
    });
});

// Global utility functions
window.ProjectEvaluator = {
    showToast: function(message, type = 'success') {
        // Create a toast notification
        const toastContainer = document.querySelector('.toast-container') || (() => {
            const container = document.createElement('div');
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
            return container;
        })();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast element after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },
    
    formatScore: function(score) {
        return new Intl.NumberFormat('fr-CA', {
            minimumFractionDigits: 1,
            maximumFractionDigits: 1
        }).format(score);
    },
    
    formatDate: function(date) {
        return new Intl.DateTimeFormat('fr-CA').format(new Date(date));
    },
    
    formatDateTime: function(date) {
        return new Intl.DateTimeFormat('fr-CA', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    }
};
