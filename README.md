# 🚨 RescueMap: AI-Enabled Emergency & Disaster Response Platform

RescueMap is a Flask-based smart disaster response system that integrates **real-time weather data**, **flood zone visualization**, **shelter detection**, and **emergency alert services** using geolocation and mapping APIs. The platform allows users to log in, view local emergency zones, locate nearby shelters, and trigger SOS alerts via email with GPS coordinates.

---

## 🌟 Features

- 🔒 Secure User Authentication (Login/Signup)
- 📍 Real-Time Weather Forecast & Sunrise/Sunset Detection (via OpenWeather API)
- 🌊 Flood Zone Visualization, Drainage & Lake Mapping (via GeoJSON + Folium)
- 🏫 Automatic Shelter Locator using Trueway Places API
- 🗺️ Route Mapping and Region-based Highlighting
- ✉️ SOS Email System with Dynamic IP-based Location Capture
- 📰 Weather News Feed (via NewsAPI)

---

## 🧰 Tech Stack

| Layer         | Technology Used                          |
|---------------|-------------------------------------------|
| **Frontend**  | HTML, CSS (Jinja Templates)               |
| **Backend**   | Python, Flask, Jinja2                     |
| **Mapping**   | Folium, GeoJSON, Geopy, Trueway APIs      |
| **APIs**      | OpenWeatherMap, Trueway Places, IPinfo    |
| **Email**     | smtplib, EmailMessage, Gmail SMTP         |
| **Environment** | `.env` file for secure mail credentials |

---

## 📂 Folder Structure

📦 RescueMap/
┣ 📜 app.py # Main Flask app
┣ 📜 utils.py # API integrations and helper functions
┣ 📜 details.json # User login data
┣ 📜 .env # Email credentials (Gmail)
┣ 📜 req.txt # Requirements file
┣ 📁 templates/ # HTML templates for frontend
┣ 📁 data/ # GeoJSON files (lake, drainage, flood)

yaml
Copy
Edit

---

## 🚀 How to Run

1. **Clone the repo**:
```bash
git clone https://github.com/yourusername/rescuemap.git
cd rescuemap
Install dependencies:

bash
Copy
Edit
pip install -r req.txt
Create a .env file:

bash
Copy
Edit
mail_sender = 'your_email@gmail.com'
mail_password = 'your_app_password'
mail_receiver = 'receiver_email@gmail.com'
Run the app:

bash
Copy
Edit
python app.py
📍 Sample Use Cases
A user logs in and views flood zones in their locality.

Clicks “Shelter” → Map shows 5 nearest shelters using GPS or IP.

In a panic situation, user submits an SOS form → Sends email with name, contact, and current coordinates.

News and weather updates are integrated for real-time situational awareness.

