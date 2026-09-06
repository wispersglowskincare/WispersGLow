# Wispers Glow

A database-driven Flask skincare shop for Wispers Glow. It is intentionally WhatsApp-first: customers can browse products, use a session cart, and send the order to WhatsApp. There is no card payment and no fake payment confirmation.

## Run on Windows

```powershell
py -3.13 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

Open `http://127.0.0.1:5000`.

The first launch creates the SQLite database, demo products, demo artwork, and the protected admin account:

```text
URL:      http://127.0.0.1:5000/admin/login
Username: admin
Password: admin1234
```

Change the starter password before publishing. The database stores a password hash, not the plain password. The admin dashboard manages products, image uploads, homepage copy, testimonials, and promotions. Adding one product creates its homepage card and dynamic `/product/<slug>` page automatically.

## Project layout

```text
app/
  admin.py       protected studio dashboard
  auth.py        session login/logout
  models.py      SQLAlchemy models and first-launch seed
  routes.py      public pages, cart, WhatsApp order link
  templates/     Jinja pages and reusable partials
  static/        CSS, JavaScript, and local uploads
instance/        SQLite database (created at runtime)
```

Demo SVG artwork is intentionally abstract so it cannot be mistaken for real customer results. Replace it with the brand's own imagery from the admin dashboard.