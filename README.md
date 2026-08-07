# 📱 telegram-ce | تلگرام در ترمینال

  

> یک کلاینت شخصی سبک و مینیمال برای تلگرام که تو ترمینال لینوکس اجرا میشه.

> A lightweight and minimal personal Telegram client designed to run in the Linux terminal.

  

---

  

زبان‌ها / Languages:

- [🐈 نسخه فارسی](#-نسخه-فارسی)

- [🇬🇧 English Version](#-english-version)

  

---

  

<a name="-نسخه-فارسی"></a>

# 🐈 نسخه فارسی

  


یه پروژه برای تمرینه. ولی کاملا کار می کنه. می تونید توی ترمینال لینوکس یا ترمینال ویندوز به وسیله Docker اجراش کنید.
اسمش رو گذاشتم telegram-ce .

  

---

  

## 📸 پیش‌نمایش و نمای برنامه (Screenshots)

  



<div align="center">

<img src="https://github.com/user-attachments/assets/f20e4cfc-7aec-4baf-8cdc-32ad9503fff6" alt="نمای محیط برنامه" width="700"/>


</div>

  



---

  

## امکانات

-  **کاملا ترمینالی:** توی ترمینال اجرا میشه. اگه تو ویندوز یا mac هم بخواید با docker راحت اجرا میشه

-  **رابط کاربری :** با استفاده از کتابخانه‌های `Rich` و `prompt_toolkit`.

-  **اجرا:** خیلی راحت با داکر کمپوز اجرا میشه و سیستم اصلیت رو کثیف نمیکنه.

-  **امن و شخصی:** کلیدها و Session فقط دست خودته.

  

---

  

## 🛠️ پیش‌نیازها و نصب سریع

  

قبل از هر کاری، حتما **داکر (Docker)** و **Docker Compose** رو سیستم نصب باشه.

  

### ۱. تنظیم فایل تنظیمات (`.env`)

ابتدا فایل نمونه `.env.example` رو کپی کن و اسمش رو بزار `.env`:

  

```bash

cp .env.example .env

```

  

حالا فایل `.env` رو باز کن و `TELEGRAM_API_ID` و `TELEGRAM_API_HASH` خودت رو توش بذار. (اگه نداری، خیلی راحت از سایت [my.telegram.org](https://my.telegram.org) بگیر).

  

```env

TELEGRAM_API_ID=123456

TELEGRAM_API_HASH=your_api_hash_here

```

  

---

  

## 🚀 نحوه اجرا

  

واسه اجرای برنامه فقط کافیه این دستور رو توی ترمینال بزنی:

اول این دستور رو بزن برای ساخت docker compose :
```bash
docker compose build
```

و بعد با این دستور می تونی اجراش کنی:
```bash

docker compose run --rm telegram-client

```

  

بار اول که داکر ایمیج رو می‌سازه و  اجرا می کنه برای ساخت فایل session  از شما شماره تلفن تلگرام و کد تایید چند مرحله ای رو می‌خواد و از دفعات بعد با کمک همون فایل session وارد اکانت شما میشه

  

---

  

<br/>

  

---

  

<a name="-english-version"></a>

# 🇬🇧 English Version

  

This is a practice project, but it is fully functional. You can run it in a Linux terminal or a Windows terminal using Docker.
I named it telegram-ce.

  

---

  

## 📸 Preview & Screenshots

  

<div align="center">

<img src="https://github.com/user-attachments/assets/f20e4cfc-7aec-4baf-8cdc-32ad9503fff6" alt="Telegram CE Screenshot" width="700"/>

<p><i>(Drop your awesome terminal screenshots here!)</i></p>

</div>

  

---

  

## Features

- **Pure Terminal Experience:** Minimal resource usage, zero clutter.

- **Rich UI:** Built with awesome Python libraries (`Rich` & `prompt_toolkit`).

- **Docker-Ready:** Containerized with Docker Compose so your host OS stays clean.

- **Private & Secure:** Your credentials and sessions stay strictly on your local setup.

  

---

  

## Setup & Requirements

  

Make sure you have **Docker** and **Docker Compose** installed.

  

### 1. Configure `.env`

Copy the example environment file:

  

```bash

cp .env.example .env

```

  

Edit `.env` and fill in your `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` (get them from [my.telegram.org](https://my.telegram.org)):

  

```env

TELEGRAM_API_ID=123456

TELEGRAM_API_HASH=your_api_hash_here

```

  

---

  

## 🚀 How to Run

  

To fire up the application, simply run:

  maybe you need to build docker compose for first time:
  ```bash
  docker compose build
  ```

```bash

docker compose run --rm telegram-client

```

  

The first time you build and run the Docker image, the application will ask for your Telegram phone number and the two-step verification code to create a session file.
From the next runs onward, it will use the existing session file to automatically log in to your account.

  

---

  

## 📄 License

[MIT License](LICENSE) — Feel free to customize and enjoy! 