# 🚀 INTRUSION X — Network Intrusion Detection System (SOC Dashboard)

Welcome to the **INTRUSION X** Master Security Operations Center (SOC) dashboard. This project is a dark, cyber-themed, fully responsive NIDS backend interface built with Django. It features a seamless login integration via a dynamic 3D-globe landing page, live threat monitoring dashboards, interactive network traffic charts, alert visualizations, and more.

## Architecture & Stack
- **Backend framework**: Django (Python)
- **Database**: SQLite3 (default)
- **Frontend Assets**: Three.js, GSAP (animations), Chart.js (graphs), TailwindCSS (utility layouts), Custom Vanilla CSS (Cyber Theme & Glassmorphism)

## Workspace Architecture
```text
NIDS_BACKEND/
│
├── dashboard/        # SOC dashboard logic and views
├── users/            # Authentication and user management
├── detection/        # Network logs & anomaly detection
├── static/           # CSS, JS, animations
├── templates/        # HTML templates
└── nids_project/     # Django settings & routing
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository

```
git clone https://github.com/your-username/intrusionx.git
cd intrusionx
```

### 2️⃣ Install Dependencies

```
pip install django
```

*(or)*

```
pip install -r requirements.txt
```

---

### 3️⃣ Run Migrations

```
python manage.py makemigrations
python manage.py migrate
```

---

### 4️⃣ Create Admin User

```
python manage.py createsuperuser
```

---

### 5️⃣ Start Server

```
python manage.py runserver
```

🌐 Open: `http://127.0.0.1:8000/`

---

## 🔐 Access Flow

```
Landing Page → Login → SOC Dashboard → Detection Engine → Alerts & Analytics
```

---

## 🛠️ Utility Scripts

```
# System diagnostics
python ATHEX_SOC.py

# Auto migrations
python run_migrations.py

# Project setup/reset helper
python debesh_help.py
```

---

## 🚀 Production Setup

```
python manage.py collectstatic
```

### Recommended Improvements:

* PostgreSQL / MySQL for production DB
* Redis + Celery for background tasks
* Docker containerization
* Nginx + Gunicorn deployment

---

## 🌟 Future Enhancements

* 🔍 Machine Learning-based anomaly detection (LOF, Isolation Forest)
* 🌐 GeoIP attack visualization
* 📡 Real-time packet capture integration
* 🔔 Email/SMS alert system
* 👥 Role-based access control (RBAC)

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

## 📜 License

This project is licensed under the MIT License.

---

## 💻 Source Code

👉 https://github.com/your-repo-link

---

## 👨‍💻 Author

**Debesh Nayak**
Cybersecurity Enthusiast | Developer | SOC Explorer

---

🔥 *INTRUSION X — Defending Networks, Detecting Threats, Delivering Intelligence.*