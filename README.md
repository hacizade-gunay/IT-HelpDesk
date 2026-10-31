IT Help Desk API
FastAPI və SQLAlchemy vasitəsilə hazırlanmış IT Help Desk müraciətlərinin (tickets) idarə olunması üçün RESTful backend servisi.
Texnologiya Steki
 * Python 3.10+
 * FastAPI — API freymvorku
 * SQLAlchemy — ORM və Verilənlər Bazası idarəetməsi
 * Pydantic v2 — Məlumatların doğrulanması (Validation) və Schema idarəetməsi
 * SQLite / SQL Server — Verilənlər Bazası
Quraşdırma və İşə Salma
 * Layihəni klonlayın və qovluğa keçin:
git clone https://github.com/hacizade-gunay/IT-HelpDesk.git
cd IT-HelpDesk

 * Lazımi kitabxanaları quraşdırın:
pip install -r requirements.txt

 * Serveri işə salın:
uvicorn main:app --reload

Mühit Dəyişənləri (Environment Variables)
Susmaya görə layihə SQLite verilənlər bazasından (sqlite:///./helpdesk.db) istifadə edir. İstəyə bağlı olaraq SQL Server və ya başqa verilənlər bazasını DATABASE_URL vasitəsilə təyin edə bilərsiniz:
export DATABASE_URL="mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server"

API Endpoint-ləri
| Metod | Endpoint | Təsvir | Sorğu Parametrləri / Gövdəsi |
|---|---|---|---|
| POST | /tickets | Yeni müraciət yaradır | title, description, category, priority |
| GET | /tickets | Müraciətləri siyahılayır (tarixə görə azalan) | Query: category, status |
| GET | /tickets/stats | Ümumi və statuslar üzrə statistik göstəricilər | - |
| GET | /tickets/{ticket_id} | Konkret müraciətin təfərrüatını gətirir | Path: ticket_id |
| PATCH | /tickets/{ticket_id}/status | Müraciətin statusunu yeniləyir | status |
Məlumat Modelləri və Enum-lar
 * Category: Hardware, Software, Network, Account, Other
 * Priority: Low, Medium (Default), High
 * Status: New (Default), In Progress, Resolved, Closed
İnteraktiv Sənədləşmə
Server işə düşdükdən sonra aşağıdakı ünvanlardan sorğuları test edə bilərsiniz:
 * Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
 * ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
