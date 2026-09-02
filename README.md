# Transaction Tracker

Kirim-chiqim (daromad va xarajatlarni) kuzatish uchun Django REST Framework asosidagi backend loyihasi.

---

## Eng oson yo'l: Docker orqali ishga tushirish (tavsiya etiladi)

Agar kompyuteringizda [Docker Desktop](https://www.docker.com/products/docker-desktop/) o'rnatilgan bo'lsa, Python, PostgreSQL, Redis kabi hech narsani alohida o'rnatishingiz shart emas — hammasi avtomatik ishlaydi.

### 1-qadam: Loyihani yuklab olish

```bash
git clone https://github.com/abomuslim225/TransactionTracker.git
cd TransactionTracker
```

### 2-qadam: `.env` faylini yaratish

Qaysi terminal ishlatayotganingizga qarab, mos buyruqni tanlang.

> **Qaysi terminal ekanini qanday bilaman?** Agar oyna sarlavhasida yoki qatorida `C:\Users\...>` ko'rinsa va **hech qanday rangli yozuv bo'lmasa** — bu **cmd.exe (Command Prompt)**. Agar qator ko'k rangda va boshida `PS C:\Users\...>` yozuvi bo'lsa — bu **PowerShell**.

**Windows — Command Prompt (cmd.exe):**
```cmd
(
echo SECRET_KEY=your-secret-key-here
echo DEBUG=True
echo ALLOWED_HOSTS=127.0.0.1,localhost
echo DB_NAME=transactiontracker
echo DB_USER=your_db_user
echo DB_PASSWORD=your_db_password
echo DB_HOST=db
echo DB_PORT=5432
echo SENDER_EMAIL=your_email
echo PASSWORD=App Password
echo REDIS_URL=redis://redis:6379/0
) > .env
```

**Windows — PowerShell:**
```powershell
@"
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=transactiontracker
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=db
DB_PORT=5432
SENDER_EMAIL=your_email
PASSWORD=App Password
REDIS_URL=redis://redis:6379/0
"@ | Out-File -FilePath .env -Encoding utf8
```

**macOS / Linux:**
```bash
cat > .env << 'EOF'
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=transactiontracker
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=db
DB_PORT=5432
SENDER_EMAIL=your_email
PASSWORD=App Password
REDIS_URL=redis://redis:6379/0
EOF
```

Buyruq bajarilgach, loyiha papkasida `.env` fayli avtomatik yaratiladi. Uni oching (`notepad .env` yoki istalgan matn muharriri bilan) va **namuna qiymatlarni o'zingiznikiga almashtiring** — ayniqsa `SECRET_KEY`, `DB_PASSWORD`, `SENDER_EMAIL`, `PASSWORD`.

> **Email sozlamalari haqida:** `PASSWORD` — bu sizning oddiy Gmail parolingiz emas, balki Google hisobingizdan alohida olinadigan **App Password (ilova paroli)**. Buni olish uchun: Google hisobingizda **2-Step Verification**ni yoqing → **Security → App passwords** bo'limidan yangi parol generatsiya qiling.

### 3-qadam: Docker orqali ishga tushirish

```bash
docker compose up -d --build
```

Bir necha daqiqadan so'ng, brauzerda oching: [http://localhost:8000](http://localhost:8000)

### 4-qadam: Ishlab turganini tekshirish

```bash
docker ps -a
```

Barcha konteynerlar **"Up"** holatida bo'lishi kerak.

---

Quyidagi qo'lda o'rnatish bo'limlari (Python, PostgreSQL, Redis'ni alohida o'rnatish) **faqat Docker ishlatmoqchi bo'lmaganlar uchun**.

## Qo'lda o'rnatish

### Talablar

- **Python 3.12+**
- PostgreSQL
- Redis
- Git

### 0. Python o'rnatilganini tekshirish

```bash
python --version
```

Agar `Python 3.12.x` (yoki undan yuqori) chiqsa — Python allaqachon bor, keyingi qadamga o'ting.

Agar **"Python was not found"** xatosi chiqsa:

**Windows:**
1. https://www.python.org/downloads/ dan so'nggi Python 3.12.x versiyasini yuklab oling.
2. O'rnatish oynasida pastdagi **"Add python.exe to PATH"** checkbox'ini albatta belgilang.
3. "Install Now" ni bosing.
4. Terminal oynasini yoping va qayta oching, so'ng `python --version` bilan qayta tekshiring.

**macOS:**
```bash
brew install python@3.12
```

**Ubuntu/Debian:**
```bash
sudo apt install python3.12 python3.12-venv
```

### 1. Loyihani yuklab olish

```bash
git clone https://github.com/abomuslim225/TransactionTracker.git
cd TransactionTracker
```

> Papka nomi katta-kichik harflarga sezgir — aynan `TransactionTracker` deb yozing.

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

Muvaffaqiyatli faollashsa, terminal qatorining boshida `(venv)` yozuvi paydo bo'ladi.

### 3. Kerakli kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 4. `.env` faylini yaratish

Yuqoridagi "2-qadam: `.env` faylini yaratish" bo'limidagi buyruqni ishlatishingiz mumkin — faqat `DB_HOST` va `REDIS_URL`ni quyidagicha o'zgartiring (chunki bu safar Docker emas, o'zingizning kompyuteringizdagi PostgreSQL/Redis'ga ulanasiz):

```env
DB_HOST=localhost
REDIS_URL=redis://localhost:6379/0
```

### 5. PostgreSQL va Redis o'rnatish

**Ubuntu/Debian:**
```bash
sudo apt install postgresql redis-server
```

**macOS (Homebrew):**
```bash
brew install postgresql redis
```

**Windows:** PostgreSQL — [rasmiy sayt](https://www.postgresql.org/download/windows/), Redis — WSL yoki Docker orqali tavsiya etiladi.

O'rnatgach, `.env` faylidagi `DB_NAME`, `DB_USER`, `DB_PASSWORD` bilan mos keladigan baza va foydalanuvchi PostgreSQL'da yaratilgan bo'lishi kerak.

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

Alohida ikkita terminalda (har birida avval `venv\Scripts\activate` yoki `source venv/bin/activate` qiling):

```bash
celery -A root worker -l info
```

```bash
celery -A root beat -l info
```

---

## Keng tarqalgan xatolar

| Xato | Sabab | Yechim |
|---|---|---|
| `'"' is not recognized...` yoki `'SECRET_KEY' is not recognized...` | PowerShell buyrug'i cmd.exe'da ishga tushirilgan | Yuqoridagi "Windows — Command Prompt (cmd.exe)" bo'limidagi buyruqni ishlating |
| `Python was not found` | Python o'rnatilmagan yoki PATH'ga qo'shilmagan | "0. Python o'rnatilganini tekshirish" bo'limiga qarang |
| `Repository not found` (git clone) | Repo nomi noto'g'ri yozilgan | Aynan `TransactionTracker` deb yozing |
| `ModuleNotFoundError` | Virtual muhit faollashtirilmagan yoki `pip install` bajarilmagan | `(venv)` terminalda ko'rinayotganini tekshiring, so'ng `pip install -r requirements.txt` |
| Bazaga ulanish xatosi | PostgreSQL ishlamayapti yoki `.env`dagi ma'lumotlar noto'g'ri | PostgreSQL xizmati ishga tushganini va `.env`dagi `DB_*` qiymatlar to'g'riligini tekshiring |

---

## API hujjatlari

Loyiha ishga tushgach, Swagger hujjatlari quyidagi manzilda mavjud:

```
http://127.0.0.1:8000/api/v1/docs/
```
