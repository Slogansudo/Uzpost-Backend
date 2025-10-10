# 🇺🇿 UzPost — Milliy Pochta Xizmati Onlayn Platformasi

## 📖 Loyiha tavsifi
**UzPost** — bu O‘zbekiston Milliy Pochta xizmati uchun ishlab chiqilgan **pochta jo‘natmalarini kuzatish va foydalanuvchi autentifikatsiyasi tizimi**.  
Loyiha foydalanuvchilarga o‘z jo‘natmalarini **barcode orqali real vaqt rejimida kuzatish**, **OneID orqali tizimga kirish** va **pochta xizmatlaridan onlayn foydalanish** imkonini beradi.

---

## 🚀 Asosiy imkoniyatlar

| Modul | Tavsif |
|--------|--------|
| 🔐 **Foydalanuvchi autentifikatsiyasi** | Telefon raqami orqali yoki OneID orqali ro‘yxatdan o‘tish |
| 🕒 **Token boshqaruvi** | Har 12 soatda yangilanadigan JWT tokenlar bilan xavfsiz tizimga kirish |
| 🧭 **Jo‘natma kuzatuvi** | Barcode orqali posilkani holatini olish |
| 📍 **Hududiy filtrlash** | Foydalanuvchining viloyati va tumaniga qarab ma’lumotlarni chiqarish |
| ⚙️ **Admin panel** | Foydalanuvchilar, posilkalar, loglar va statistikani boshqarish |
| ⚡ **Kesh va throttling** | Redis va DRF throttling orqali so‘rovlar tezligini boshqarish |
| 🧠 **Log va xavfsizlik** | IP-log tizimi orqali foydalanuvchi faoliyatini kuzatish |

---

## 🧩 Texnologiyalar

- **Backend:** Django 5, Django REST Framework  
- **Ma’lumotlar bazasi:** PostgreSQL 14  
- **Kesh:** Redis  
- **Server:** Nginx + Gunicorn  
- **Autentifikatsiya:** JWT, OneID  
- **Monitoring:** Middleware orqali IP log kuzatuvi  
- **Deployment:** Ubuntu Server 22.04  
- **Dokumentatsiya:** Swagger / Redoc  

---

## ⚙️ Arxitektura

