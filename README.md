# Transaction Tracker

Kirim-chiqim (daromad va xarajatlarni) kuzatish uchun Django REST Framework asosidagi backend loyihasi.

## Talablar

- Python 3.12+
- PostgreSQL
- Redis
- Git

---

## O'rnatish

### 1. Loyihani yuklab olish

```bash
git clone https://github.com/abomuslim225/TransactionTracker.git
cd TransactionTracker
```

### 2. Virtual muhit yaratish va faollashtirish

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Kerakli kutubxonalarni o'rnatish

```bash
pip install Django==6.1
pip install djangorestframework==3.18.0
pip install djangorestframework-simplejwt==5.5.1
pip install drf-spectacular==0.30.0
pip install django-modeltranslation==0.19.11
pip install django-filter==24.3
pip install psycopg2-binary==2.9.10
pip install redis==8.1.0
pip install python-dotenv==1.2.3
pip install celery==5.6.3
pip install requests==2.34.2
pip install gunicorn==23.0.0
pip install Pillow==11.0.0
```

Yoki bitta buyruq bilan:

```bash
pip install -r requirements.txt
```

### 4. `.env` faylini yaratish

Loyiha papkasida `.env` nomli fayl yarating va quyidagilarni to'ldiring:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=transactiontracker
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

SENDER_EMAIL=your_email
PASSWORD=App Password

REDIS_URL=redis://localhost:6379/0
```

> **Email sozlamalari haqida:** `PASSWORD` — bu sizning oddiy Gmail parolingiz emas, balki Google hisobingizdan alohida olinadigan **App Password (ilova paroli)**. Buni olish uchun: Google hisobingizda **2-Step Verification**ni yoqing → **Security → App passwords** bo'limidan yangi parol generatsiya qiling.

### 5. PostgreSQL va Redis o'rnatilganini tekshirish

**Ubuntu/Debian:**
```bash
sudo apt install postgresql redis-server
```

**macOS (Homebrew):**
```bash
brew install postgresql redis
```

**Windows:** PostgreSQL — [rasmiy sayt](https://www.postgresql.org/download/windows/), Redis — WSL yoki Docker orqali tavsiya etiladi.

### 6. Bazani migratsiya qilish

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Superuser (admin) yaratish

```bash
python manage.py createsuperuser
```

### 8. Statik fayllarni yig'ish

```bash
python manage.py collectstatic --noinput
```

### 9. Serverni ishga tushirish

```bash
python manage.py runserver
```

Brauzerda oching: [http://127.0.0.1:8000](http://127.0.0.1:8000)

### 10. Celery worker va beat ishga tushirish

Alohida ikkita terminalda:

```bash
celery -A root worker -l info
```

```bash
celery -A root beat -l info
```

---

## Docker orqali ishga tushirish (muqobil, tavsiya etiladi)

Agar kompyuteringizda Docker o'rnatilgan bo'lsa, yuqoridagi 2–10-qadamlarning barchasi o'rniga faqat bitta buyruq yetarli:

```bash
docker compose up -d --build
```

Bu buyruq PostgreSQL, Redis, Django, Celery worker va Celery beat'ni avtomatik o'rnatib, ishga tushiradi.

---

## API hujjatlari

Loyiha ishga tushgach, Swagger hujjatlari quyidagi manzilda mavjud:

```
http://127.0.0.1:8000/api/v1/docs/
```
