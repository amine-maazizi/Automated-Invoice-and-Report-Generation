const { initializeDashboard } = require('./src/pages/dashboard.js');
const { initializeAutomationPage } = require('./src/pages/automation.js');
const { initializeSettingsPage } = require('./src/pages/settings.js');


document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.getElementById('navbar');
    const toggleBtn = document.getElementById('toggle-btn');
    const logoExpanded = document.querySelector('.logo-expanded');
    const logoRetracted = document.querySelector('.logo-retracted');
    const navItems = document.querySelectorAll('.nav-item');
    const content = document.querySelector('.content');

    function expandNavbar() {
        navbar.classList.add('expanded');
        navbar.addEventListener('transitionend', handleExpansionTextUpdate, { once: true });
    }

    function collapseNavbar() {
        logoExpanded.style.display = 'none';
        logoRetracted.style.display = 'block';
        navItems.forEach(item => item.style.display = 'none');
        navbar.classList.remove('expanded');
    }

    function handleExpansionTextUpdate(event) {
        if (event.propertyName === 'width') {
            logoExpanded.style.display = 'block';
            logoRetracted.style.display = 'none';
            navItems.forEach(item => item.style.display = 'block');
        }
    }

    toggleBtn.addEventListener('click', () => {
        if (navbar.classList.contains('expanded')) {
            collapseNavbar();
        } else {
            expandNavbar();
        }
    });

    function loadPage(page) {
        fetch(`src/pages/${page}.html`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.text();
            })
            .then(html => {
                content.innerHTML = html;

                // Initialize the correct page script
                switch (page) {
                    case 'dashboard':
                        initializeDashboard();
                        break;
                    case 'automation':
                        initializeAutomationPage();
                        break;
                    case 'settings':
                        initializeSettingsPage();
                        break;
                    default:
                        console.error('No matching page initializer found.');
                }
            })
            .catch(error => {
                console.error('Error fetching the page:', error);
                content.innerHTML = '<p>Error loading page.</p>';
            });
    }

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const page = item.getAttribute('data-page');
            loadPage(page);
        });
    });

    loadPage('dashboard');
});
