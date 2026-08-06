# 📱 telegram-ce | تلگرام در ترمینال

> یک کلاینت شخصی، شیک و سبُک برای تلگرام، درست توی دل ترمینال لینوکس! 🚀

---

 زبان‌ها / Languages:
- [🐈 نسخه فارسی](#-نسخه-فارسی)
- [🇬🇧 English Version](#-english-version)

---

<a name="-نسخه-فارسی"></a>
# 🐈 نسخه فارسی

سلام رفیق! 👋  
تا حالا شده موقع کد زدن یا کار تو ترمینال، دلت بخواد بدون این‌که فازتو عوض کنی و بری سراغ گوشی یا برنامه‌های سنگین دسکتاپ، سریع پیامای تلگرامت رو ببینی یا جواب بدی؟  
**telegram-ce** دقیقا واسه همین ساخته شده! یه کلاینت تلگرام باحال و ترمینالی که سریع اجرا میشه و کار باهاش خیلی کیف میده.

---

## 📸 پیش‌نمایش و نمای برنامه (Screenshots)

<!-- عکس‌های محیط برنامه‌تو می‌تونی اینجا بذاری -->
<div align="center">
  <img src="https://via.placeholder.com/800x450.png?text=Telegram+CE+Terminal+UI+Screenshot" alt="نمای محیط برنامه" width="700"/>
  <p><i>(جای عکس محیط باحال برنامه‌ت! بعد از گرفتن اسکرین‌شات، آدرسش رو اینجا بذار)</i></p>
</div>

<!-- اگر چندتا عکس داشتی می‌تونی اینطوری هم بذاری:
| نمای چت‌ها | ارسال پیام |
| :---: | :---: |
| ![چت‌ها](docs/screenshot1.png) | ![ارسال](docs/screenshot2.png) |
-->

---

## ✨ امکانات خفن
- 💻 **کاملا ترمینالی:** بدون مصرف رم اضافه و سنگینی GUI!
- 🎨 **رابط کاربری شیک:** با استفاده از کتابخانه‌های خفن `Rich` و `prompt_toolkit`.
- 🐳 **آماده برای داکر:** خیلی راحت با داکر کمپوز اجرا میشه و سیستم اصلیت رو کثیف نمیکنه.
- 🔐 **امن و شخصی:** کلیدها و Session فقط دست خودته.

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

```bash
docker compose run --rm telegram-ce
```

*(بار اول داکر ایمیج رو می‌سازه و بار اول اجرا هم تلگرام ازت شماره تلفن و کد تایید می‌خواد، بعدش دیگه مستری! 😎)*

---

<br/>

---

<a name="-english-version"></a>
# 🇬🇧 English Version

Hey there! 👋  
Ever wished you could check your Telegram messages right from your Linux terminal without breaking your flow or context switching to a heavy GUI app?  
**telegram-ce** is built just for that! A lightweight, stylish, and keyboard-friendly Telegram terminal client.

---

## 📸 Preview & Screenshots

<div align="center">
  <img src="https://via.placeholder.com/800x450.png?text=Telegram+CE+Terminal+UI+Screenshot" alt="Telegram CE Screenshot" width="700"/>
  <p><i>(Drop your awesome terminal screenshots here!)</i></p>
</div>

---

## ✨ Features
- 💻 **Pure Terminal Experience:** Minimal resource usage, zero clutter.
- 🎨 **Rich UI:** Built with awesome Python libraries (`Rich` & `prompt_toolkit`).
- 🐳 **Docker-Ready:** Containerized with Docker Compose so your host OS stays clean.
- 🔐 **Private & Secure:** Your credentials and sessions stay strictly on your local setup.

---

## 🛠️ Setup & Requirements

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

```bash
docker compose run --rm telegram-ce
```

*(On first launch, it builds the container and prompts for your phone number & Telegram verification code. After that, you're good to go! 😎)*

---

## 📄 License
[MIT License](LICENSE) — Feel free to customize and enjoy! 🎉
