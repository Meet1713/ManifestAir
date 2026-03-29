# ✈️ ManifestAir

## 📌 Overview
ManifestAir is a web-based flight aggregation system that allows users to search for flights, compare prices, track routes using a watchlist, and receive notifications when prices drop. It also includes an admin dashboard for managing system operations.

---

## Features

### Traveler
- Search flights (one-way & round-trip)  
- View prices, airlines, duration, stops  
- Currency conversion (USD → CAD)  
- Add routes to watchlist  
- Receive price-drop notifications  

### Admin
- Dashboard with system metrics  
- Refresh watchlist prices  
- Manage users  
- Switch between live and mock provider  

---

## Architecture
- MVC (Model–View–Controller) using Flask  
- Design Patterns:
  - Observer (notifications)  
  - Simple Factory (provider selection)  

---

## APIs Used
- SerpApi (flight data)  
- CurrencyAPI (price conversion)  
- Unsplash API (images)  

---

## Tech Stack
- Python (Flask)  
- HTML, CSS, JavaScript, Bootstrap  
- MySQL (Aiven)  
- Render (deployment)  

---

## 