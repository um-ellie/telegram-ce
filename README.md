# Telegram CE — Terminal Edition

A sleek, comprehensive Telegram client that lives entirely in your terminal.
Interactive arrow-key menus, live incoming messages, styled panels, and a one-command Docker setup.

Built with `Telethon`, `Rich`, and `prompt_toolkit` — v2.0

---

Languages / زبان‌ها:

- [English Version](#english-version)
- [نسخه فارسی](#نسخه-فارسی)

---

<a name="english-version"></a>

# English Version

## Features

- **Interactive main menu** — arrow-key navigation (up/down or j/k, Enter to select, number keys for quick-pick, Esc to cancel)
- **Chat management** — browse channels, groups, direct messages and bots with unread badges
- **Message reading** — compact, wrapped message panels with view counts, forwards and media icons
- **Send messages** — to any chat, group, channel or user
- **Channel membership** — join and leave public channels and groups
- **Search** — find any chat by name or @username
- **Account dashboard** — channels, groups, DMs, bots, pinned and unread statistics at a glance
- **Live feed** — incoming messages render in real time while you type (toggleable)
- **Smart prompt** — Tab autocompletion for commands and chat names, typo suggestions, in-session history
- **Two login methods** — QR code (recommended) or phone number + code, with 2FA support
- **One-command Docker run** — your session persists in a named Docker volume, so you log in exactly once

## Requirements

- **Docker** and **Docker Compose** (for the recommended path)
- A Telegram account
- Your personal API ID and API hash from [my.telegram.org](https://my.telegram.org)

## Quick Start (Docker Compose)

```bash
# 1. Configure credentials
cp .env.example .env
#    Edit .env and fill in TELEGRAM_API_ID and TELEGRAM_API_HASH
#    (get them free from https://my.telegram.org)

# 2. Build and run — that's it
docker compose run --rm telegram-ce
```

### First login

On first launch you choose between two login methods:

- **QR code (recommended)** — a QR code renders right in the terminal. Scan it from your phone:
  **Telegram → Settings → Devices → Link Desktop Device**.
  No SMS code is involved, so it is immune to Telegram's code-delivery rate limits.
- **Phone number + code** — the classic flow, with retries, resend (`r`), and flood-wait handling.

If your account has 2FA enabled, you will also be asked for your password.
After a successful login the session is saved — every later launch signs you in automatically.

### Where is my session stored?

The session file (your login key) is **not** stored inside the project folder.
It lives in a named Docker volume, which is safer: it can never be accidentally
committed to git, pushed, or shared with the project.

| Location | Path |
|---|---|
| Inside the container | `/app/data/telegram_ce_session.session` |
| On your machine | `~/.local/share/docker/volumes/telegram-ce_telegram-ce-data/_data/` (rootless Docker) or `/var/lib/docker/volumes/telegram-ce_telegram-ce-data/_data/` (standard Docker) |

Useful commands:

```bash
docker volume ls                                          # list volumes
docker volume inspect telegram-ce_telegram-ce-data       # exact host path
docker compose run --rm telegram-ce ls -la /app/data     # view the file from inside
```

The session survives `docker compose down`, image rebuilds, and Docker upgrades.
It is only removed by `docker compose down -v` or `docker volume rm telegram-ce_telegram-ce-data`.
If you ever lose it, you simply scan a new QR code — chats and messages live on Telegram's servers.

### Local run (without Docker)

Requires Python 3.12+:

```bash
pip install -r requirements.txt
export TELEGRAM_API_ID=... TELEGRAM_API_HASH=...
python -m app
```

The session file then defaults to `/app/data`; override the directory with the
`TELEGRAM_CE_DATA_DIR` environment variable.

## Commands

| Command | Arguments | Description |
|---|---|---|
| `/menu` | — | Open the interactive main menu |
| `/chats` | — | List all channels, groups and DMs |
| `/view` | `<target> [n]` | Read recent messages (`@name`, `#index`, or id) |
| `/info` | `<target>` | Full profile / channel card |
| `/send` | `<target> <msg>` | Send a message (`/reply` alias) |
| `/join` | `<@channel>` | Join a public channel or group |
| `/leave` | `<@channel>` | Leave a channel or group |
| `/read` | `<target>` | Mark a chat as read |
| `/search` | `<query>` | Search chats by name or username |
| `/stats` | — | Account overview dashboard |
| `/me` | — | Your account card |
| `/help` | — | Command guide |
| `/clear` | — | Clear the screen |
| `/quit` | — | Exit safely (`/exit` alias) |

`#index` refers to the row numbers shown by `/chats` — for example `/view #3` opens the third chat.

## Project Structure

```
app/
├── __main__.py        # entry point (python -m app)
├── config.py          # env-based configuration
├── commands.py        # command registry (help + autocompletion source)
├── app.py             # interactive loop, dispatcher, hub menu
├── telegram/
│   ├── client.py      # Telethon lifecycle + QR / code login flows
│   └── service.py     # all Telegram operations, returned as plain dicts
└── ui/
    ├── theme.py       # central palette, box styles, shared console
    ├── banner.py      # startup banner and account card
    ├── components.py  # tables, message panels, stats, live feed
    └── menu.py        # arrow-key interactive menu (tty-aware)
```

## Troubleshooting

**Colors look broken (raw garbage like `?[95m`)** — add `TELEGRAM_CE_PLAIN=1` to your `.env`;
the app then renders cleanly without colors.

**Some symbols or channel names show as `?` or boxes** — your terminal font lacks emoji glyphs.
Install a font with emoji coverage (for example a Nerd Font) and select it in your terminal.

## Privacy

Your API credentials live only in your local `.env`, and your Telethon session only in a local
Docker volume. Nothing is sent anywhere except directly to Telegram's servers.

## License

[MIT](LICENSE) — customize and enjoy!

---

<a name="نسخه-فارسی"></a>

# نسخه فارسی

یک کلاینت شخصی و کامل برای تلگرام که کاملاً داخل ترمینال اجرا می‌شود.
منوی تعاملی با کلیدهای جهت‌دار، نمایش زنده‌ی پیام‌های ورودی، پنل‌های مرتب و اجرای داکری با یک دستور.

## امکانات

- **منوی اصلی تعاملی** — جابه‌جایی با کلیدهای جهت‌دار (بالا/پایین یا j/k)، انتخاب با Enter، انتخاب سریع با عدد، انصراف با Esc
- **مدیریت چت‌ها** — مرور کانال‌ها، گروه‌ها، پیام‌های خصوصی و ربات‌ها همراه با شمارنده‌ی نخوانده‌ها
- **خواندن پیام‌ها** — پنل‌های جمع‌وجور با شکستن خطوط طولانی، تعداد بازدید، فوروارد و آیکن رسانه
- **ارسال پیام** — به هر چت، گروه، کانال یا کاربر
- **عضویت در کانال** — join و leave کانال‌ها و گروه‌های عمومی
- **جستجو** — پیدا کردن هر چت با نام یا @username
- **داشبورد اکانت** — آمار کانال‌ها، گروه‌ها، چت‌ها، ربات‌ها، سنجاق‌شده‌ها و نخوانده‌ها
- **فید زنده** — پیام‌های ورودی همزمان با تایپ کردن نمایش داده می‌شوند (قابل خاموش‌کردن)
- **پرامپت هوشمند** — تکمیل خودکار دستورات و نام چت‌ها با Tab، پیشنهاد برای غلط‌های تایپی و تاریخچه‌ی ورودی
- **دو روش لاگین** — کد QR (پیشنهادی) یا شماره تلفن + کد، همراه با پشتیبانی از تایید دومرحله‌ای
- **اجرای داکری با یک دستور** — سشن شما در یک volume داکری ذخیره می‌شود و فقط یک بار لاگین می‌کنید

## پیش‌نیازها

- **Docker** و **Docker Compose**
- یک اکانت تلگرام
- شناسه‌ی API و هش API شخصی خودتان از [my.telegram.org](https://my.telegram.org)

## نصب و راه‌اندازی سریع (Docker Compose)

```bash
# ۱. تنظیم اعتبارنامه‌ها
cp .env.example .env
#    فایل .env را باز کنید و TELEGRAM_API_ID و TELEGRAM_API_HASH را پر کنید
#    (از سایت https://my.telegram.org رایگان بگیرید)

# ۲. ساخت و اجرا — همین!
docker compose run --rm telegram-ce
```

### لاگین اولیه

بار اول که برنامه را اجرا کنید، بین دو روش لاگین یکی را انتخاب می‌کنید:

- **کد QR (پیشنهادی)** — یک QR داخل خود ترمینال نمایش داده می‌شود. با گوشی اسکن کنید:
  **تلگرام → تنظیمات → دستگاه‌ها → اتصال دستگاه دسکتاپ**.
  هیچ کد پیامکی در کار نیست، پس محدودیت ارسال کد تلگرام هم اثرش را نمی‌گذارد.
- **شماره تلفن + کد** — روش کلاسیک، با امکان تلاش مجدد، ارسال دوباره‌ی کد (با `r`) و مدیریت محدودیت تلگرام.

اگر تایید دومرحله‌ای فعال باشد، رمز دومرحله‌ای هم پرسیده می‌شود.
بعد از لاگین موفق، سشن ذخیره می‌شود و دفعات بعد بدون هیچ لاگینی وارد می‌شوید.

### سشن کجا ذخیره می‌شود؟

فایل سشن (کلید ورود شما) **داخل پوشه‌ی پروژه ذخیره نمی‌شود**؛ در یک volume نام‌دار داکری نگهداری
می‌شود که امن‌تر است: هرگز به‌صورت تصادفی در گیت commit یا همراه پروژه share نمی‌شود.

| محل | مسیر |
|---|---|
| داخل کانتینر | `/app/data/telegram_ce_session.session` |
| روی سیستم شما | `~/.local/share/docker/volumes/telegram-ce_telegram-ce-data/_data/` (داکر rootless) یا `/var/lib/docker/volumes/telegram-ce_telegram-ce-data/_data/` (داکر معمولی) |

دستورهای مفید:

```bash
docker volume ls                                          # لیست volumeها
docker volume inspect telegram-ce_telegram-ce-data       # مسیر دقیق روی سیستم
docker compose run --rm telegram-ce ls -la /app/data     # دیدن فایل از داخل کانتینر
```

سشن با `docker compose down`، rebuild ایمیج و حتی حذف خود docker از بین نمی‌رود؛
فقط با `docker compose down -v` یا `docker volume rm telegram-ce_telegram-ce-data` حذف می‌شود.
اگر هم روزی از دست برود، فقط یک بار دیگر QR اسکن می‌کنید — چت‌ها و پیام‌ها روی سرور تلگرام هستند.

### اجرای محلی (بدون داکر)

نیازمند پایتون 3.12 به بالا:

```bash
pip install -r requirements.txt
export TELEGRAM_API_ID=... TELEGRAM_API_HASH=...
python -m app
```

در این حالت فایل سشن به‌صورت پیش‌فرض در `/app/data` ذخیره می‌شود؛ با متغیر محیطی
`TELEGRAM_CE_DATA_DIR` می‌توانید مسیر آن را عوض کنید.

## دستورها

| دستور | آرگومان‌ها | توضیح |
|---|---|---|
| `/menu` | — | باز کردن منوی اصلی تعاملی |
| `/chats` | — | لیست همه‌ی کانال‌ها، گروه‌ها و چت‌ها |
| `/view` | `<هدف> [تعداد]` | خواندن پیام‌های اخیر (`@نام`، `#شماره` یا شناسه) |
| `/info` | `<هدف>` | کارت اطلاعات کانال یا کاربر |
| `/send` | `<هدف> <متن>` | ارسال پیام (مستعار: `/reply`) |
| `/join` | `<@کانال>` | عضویت در کانال یا گروه عمومی |
| `/leave` | `<@کانال>` | خروج از کانال یا گروه |
| `/read` | `<هدف>` | علامت‌گذاری چت به‌عنوان خوانده‌شده |
| `/search` | `<عبارت>` | جستجوی چت‌ها با نام یا نام کاربری |
| `/stats` | — | داشبورد آمار اکانت |
| `/me` | — | کارت اکانت شما |
| `/help` | — | راهنمای دستورها |
| `/clear` | — | پاک کردن صفحه |
| `/quit` | — | خروج امن (مستعار: `/exit`) |

`#شماره` به شماره‌ی ردیف‌های جدول `/chats` اشاره دارد — مثلاً `/view #3` سومین چت را باز می‌کند.

## رفع اشکال

**رنگ‌ها خراب نمایش داده می‌شوند (کاراکترهای خام مثل `?[95m`)** — خط `TELEGRAM_CE_PLAIN=1` را به فایل `.env` اضافه کنید؛ برنامه بدون رنگ و کاملاً تمیز رندر می‌شود.

**بعضی نمادها یا نام کانال‌ها به‌صورت `?` یا مربع دیده می‌شوند** — فونت ترمینال شما ایموجی ندارد. یک فونت با پشتیبانی ایموجی (مثلاً Nerd Font) نصب و در ترمینال انتخاب کنید.

## حریم خصوصی

اعتبارنامه‌های API شما فقط در فایل محلی `.env` و سشن تلگرام فقط در یک volume محلی داکر نگهداری می‌شود. هیچ داده‌ای به هیچ‌جایی جز سرورهای خود تلگرام ارسال نمی‌شود.

## مجوز

[MIT](LICENSE) — آزادید که تغییرش دهید و لذت ببرید!
