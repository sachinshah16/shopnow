/* ============================================
   ShopNow — Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {

    // ---- Auto-dismiss toasts ----
    document.querySelectorAll('.shopnow-toast').forEach(function (el) {
        const toast = new bootstrap.Toast(el, { delay: 4000 });
        toast.show();
    });

    // ---- CSRF Token helper ----
    function getCSRF() {
        const el = document.querySelector('[name=csrfmiddlewaretoken]');
        if (el) return el.value;
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) return meta.content;
        // Cookie fallback
        const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }

    // ---- Quick Add to Cart (AJAX) ----
    document.querySelectorAll('.quick-add-form').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const btn = form.querySelector('.btn-add-to-cart');
            const url = form.dataset.url;
            const formData = new FormData(form);

            btn.disabled = true;
            btn.textContent = 'Adding...';

            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRF()
                }
            })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'ok') {
                    btn.textContent = '✓ Added!';
                    btn.classList.add('added');
                    updateCartBadge(data.cart_count);
                    showToast(data.message, 'success');
                    setTimeout(() => {
                        btn.textContent = 'Add to Cart';
                        btn.classList.remove('added');
                        btn.disabled = false;
                    }, 1500);
                } else {
                    btn.textContent = 'Add to Cart';
                    btn.disabled = false;
                    showToast(data.error || 'Please login first', 'error');
                    if (!data.error) {
                        window.location.href = '/users/login/';
                    }
                }
            })
            .catch(err => {
                btn.textContent = 'Add to Cart';
                btn.disabled = false;
                // Likely not authenticated
                window.location.href = '/users/login/';
            });
        });
    });

    // ---- Update Cart Badge ----
    function updateCartBadge(count) {
        let badge = document.getElementById('cartBadge');
        if (count > 0) {
            if (!badge) {
                badge = document.createElement('span');
                badge.id = 'cartBadge';
                badge.className = 'cart-badge';
                document.getElementById('navCartBtn').appendChild(badge);
            }
            badge.textContent = count;
        } else if (badge) {
            badge.remove();
        }
    }

    // ---- Toast Notification ----
    function showToast(message, type) {
        type = type || 'info';
        const bgClass = {
            'success': 'text-bg-success',
            'error': 'text-bg-danger',
            'warning': 'text-bg-warning',
            'info': 'text-bg-info'
        }[type] || 'text-bg-info';

        const icon = {
            'success': 'bi-check-circle',
            'error': 'bi-exclamation-circle',
            'warning': 'bi-exclamation-triangle',
            'info': 'bi-info-circle'
        }[type] || 'bi-info-circle';

        let container = document.getElementById('toastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }

        const html = `
            <div class="toast show align-items-center ${bgClass} border-0 shopnow-toast" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="bi ${icon} me-2"></i>${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', html);

        const newToast = container.lastElementChild;
        const bsToast = new bootstrap.Toast(newToast, { delay: 3000 });
        bsToast.show();
        newToast.addEventListener('hidden.bs.toast', () => newToast.remove());
    }

    // ---- Search Suggestions ----
    const searchInput = document.getElementById('searchInput');
    const suggestionsBox = document.getElementById('searchSuggestions');
    let searchTimeout;

    if (searchInput && suggestionsBox) {
        searchInput.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            const q = this.value.trim();

            if (q.length < 2) {
                suggestionsBox.classList.remove('show');
                suggestionsBox.innerHTML = '';
                return;
            }

            searchTimeout = setTimeout(function () {
                fetch(`/home/api/search-suggest/?q=${encodeURIComponent(q)}`)
                    .then(r => r.json())
                    .then(data => {
                        if (data.results && data.results.length > 0) {
                            let html = '';
                            data.results.forEach(item => {
                                if (item.type === 'product') {
                                    html += `<a href="/home/products/${item.slug}/" class="search-suggestion-item d-flex justify-content-between">
                                        <span><i class="bi bi-tag me-2 text-muted"></i>${item.name}</span>
                                        <span class="text-muted small">₹${parseInt(item.price).toLocaleString()}</span>
                                    </a>`;
                                } else {
                                    html += `<a href="/home/shops/${item.id}/" class="search-suggestion-item">
                                        <i class="bi bi-shop me-2 text-muted"></i>${item.name}
                                    </a>`;
                                }
                            });
                            suggestionsBox.innerHTML = html;
                            suggestionsBox.classList.add('show');
                        } else {
                            suggestionsBox.classList.remove('show');
                        }
                    });
            }, 300);
        });

        // Close suggestions on click outside
        document.addEventListener('click', function (e) {
            if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
                suggestionsBox.classList.remove('show');
            }
        });
    }

    // ---- Navbar scroll effect ----
    const navbar = document.getElementById('mainNavbar');
    if (navbar) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 50) {
                navbar.classList.add('shadow-sm');
            } else {
                navbar.classList.remove('shadow-sm');
            }
        });
    }
});
