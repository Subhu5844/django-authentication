# 🍪 Django Cookie-Based Authentication with CSRF & OTP

This project is a **Django + DRF authentication system** that uses **cookie-based authentication** (not headers), **OTP-based user registration**, and **CSRF protection**.  
It also includes **Swagger UI** for API documentation and testing.

---

## ✨ Features
- 🔐 **User Registration** (`/api/register/`)
  - Registers with email + password
  - Sends a **One-Time Password (OTP)** to email
- ✅ **OTP Verification** (`/api/register/verify`)
  - Verifies OTP and activates the account
- 🔑 **Login** (`/api/login/`)
  - Validates credentials
  - Sets `auth_token` as an **HTTP-only cookie**
- 👤 **User Details** (`/api/me/`)
  - Returns details of the logged-in user
  - Protected: requires cookie-based authentication
- 🚪 **Logout** (`/api/logout/`)
  - Clears authentication cookie
  - Invalidates token server-side
- 🛡️ **Security**
  - Cookie-based auth only (no headers)
  - CSRF protection on all unsafe requests
  - Cookies marked as `HttpOnly`, `Secure`, and `SameSite=Lax`
- 📖 **Swagger UI** (`/swagger/`)
  - Automatically generates **CSRF token**
  - Allows testing all endpoints interactively

---

## 🛠️ Tech Stack
- [Django 5.2](https://docs.djangoproject.com/en/stable/)
- [Django REST Framework (DRF)](https://www.django-rest-framework.org/)
- [DRF Spectacular](https://drf-spectacular.readthedocs.io/) (Swagger / OpenAPI docs)
- SQLite (default, easy setup)

---

## 🚀 Getting Started

### 1. Clone Repository
```bash
git clone https://github.com/your-username/django-asgn.git
cd django-asgn/config
