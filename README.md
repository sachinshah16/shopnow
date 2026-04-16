# ShopNow Hyperlocal Marketplace

ShopNow is a powerful, hyper-local marketplace platform built with Django. It bridges the gap between local vendors and consumers by offering geolocation-based store and product discovery, enabling users to find the best products available in their immediate vicinity.

## Features

- **Hyperlocal Discovery**: Utilizes the Haversine formula to compute dynamic geolocation-based distances, allowing users to find nearby shops and products based on their current location or manually selected location.
- **Consumer Storefront**: A user-friendly frontend where consumers can browse local shops, view products, and add items to their local carts.
- **Vendor Management Interface**: A dedicated interface tailored for vendors to seamlessly manage products, track inventory, and view analytics.
- **AJAX-Based Quick-Sell Workflow**: A robust offline sales functionality ("Quick Sell") integrated directly into the vendor interface, allowing vendors to process offline or in-store purchases swiftly without page reloads.
- **Mode Selection**: A unified entry gateway allowing seamless role-switching between Consumer Mode and Vendor Mode.
- **Pincode Autocomplete**: Simplifies checkout and location input with dynamic pincode prediction.

## Tech Stack

- **Backend**: Python 3, Django (>=4.2)
- **APIs & Serialization**: Django REST Framework
- **Frontend Utilities**: django-widget-tweaks
- **Image Processing**: Pillow
- **Database**: SQLite (default configuration, can be deployed to PostgreSQL for production)

## Project Structure

```text
shopnow/
├── manage.py            # Django project management script
├── shopnow/             # Core project configuration settings, URLs, and WSGI/ASGI
├── orders/              # Orders and cart management app
├── products/            # Product catalog and inventory app
├── users/               # Custom user management, authentication, and profiles
├── vendors/             # Vendor stores, management, and quick-sell app
├── templates/           # Global HTML templates
├── static/              # Global static files (CSS, JS, images)
├── media/               # User-uploaded files (product images, etc.)
└── requirements.txt     # Python package dependencies
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)

### Installation

1. **Clone the repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd shopnow
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser** (for admin testing and vendor creation):
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

Access the application running at `http://127.0.0.1:8000/`.

## Core Logic Highlight

- **Haversine Formula Implementation**: This enables the system to calculate the great-circle distance between two points (the user's browser-detected or manually entered coordinates and the vendor's location) directly, sorting results by proximity for a highly tailored hyper-local shopping experience.
- **Vendor "Quick Sell"**: The vendor dashboard contains an optimized, 2-step (lookup, confirm) checkout API for recording walk-in sales quickly.

## License

This project is proprietary and intended for the ShopNow platform.
