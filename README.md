# 🌿 FarmCare: Smart Cardamom Farming Platform

Welcome to **FarmCare**, an all-in-one digital companion designed specifically for Cardamom farmers. FarmCare leverages advanced **Artificial Intelligence (AI)** to identify plant diseases from images and provides real-time market prices, empowering farmers to make data-driven decisions.

## 🚀 Key Features

- **🤖 AI Crop Doctor**: Instantly identify crop diseases by uploading a photo of a leaf or pod. Our AI provides diagnosis and treatment plans.
- **💰 Live Market Prices**: Get real-time auction prices and daily updates from major cardamom markets.
- **📉 Price Trends**: Analyze historical price data with interactive charts to determine the best time to sell.
- **🧪 Soil Testing**: Request professional soil testing services directly through the platform.
- **🗣️ Bilingual Support**: Get AI advice and platform instructions in both English and regional languages (like Malayalam).
- **🔒 Secure Authentication**: Robust user authentication system for Farmers and Admins.

---

## 💻 Technical Stack

FarmCare is built using modern web technologies to ensure scalability, security, and a seamless user experience.

- **Backend Framework**: Django (Python 3.x)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: SQLite3 (Development) / Can be migrated to PostgreSQL for production
- **AI Integration**: Google Gemini Pro Vision API (for image-based disease detection)
- **Web Scraping**: BeautifulSoup4 & Requests (for live price fetching)
- **Background Tasks**: APScheduler (for automated price updates)
- **Report Generation**: ReportLab (for generating downloadable PDF reports)
- **Image Processing**: Pillow (PIL)

---

## ⚙️ How It Works

1. **AI Disease Detection**: When a user uploads an image, the backend sends it to the Gemini Pro Vision API along with a specialized prompt. The AI acts as an expert plant pathologist, analyzes the visual symptoms, identifies the disease, and returns structured treatment advice in multiple languages.
2. **Live Pricing**: A background scheduled task periodically scrapes the official Spices Board or local auction websites using `BeautifulSoup`. The parsed data is cleaned and stored in the database, updating the historical price trends visible on the dashboard.
3. **Authentication & Roles**: The system uses Django's built-in authentication but extends it to support custom roles (Farmer vs. Admin). Admins have a dedicated panel to manage soil test requests, user data, and manually trigger price scraping.

---

## 🛠️ Step-by-Step Installation Guide

Anyone can install and run this project locally by following these steps:

### Prerequisites
- **Python 3.8+**: Ensure Python is installed on your system.
- **Git**: (Optional) For cloning the repository.

### Step 1: Get the Project
Download the ZIP file of the project and extract it, or clone it using Git:
```bash
git clone <repository_url>
cd FarmCare
```

### Step 2: Create a Virtual Environment (Recommended)
Creating a virtual environment keeps the project dependencies separate from your system.
```bash
python -m venv .venv
```
Activate the virtual environment:
- On **Windows**: `.venv\Scripts\activate`
- On **macOS/Linux**: `source .venv/bin/activate`

### Step 3: Install Required Dependencies
Run the following command in your terminal to install all the technical packages required:
```bash
pip install -r requirements.txt
```

### Step 4: Configure the AI API Key
The AI features require a Google Gemini API key.
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and generate a free API key.
2. Open `farmcare/settings.py` in a text editor.
3. Find the line `GEMINI_API_KEY = 'YOUR_SECRET_KEY_HERE'` and replace `'YOUR_SECRET_KEY_HERE'` with your actual key.

### Step 5: Database Setup & Migrations
Create the necessary database tables:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Load Initial Data (Seed Data)
Populate the database with sample prices, diseases, and demo users:
```bash
python seed_data.py
```

### Step 7: Run the Server
Start the Django development server:
```bash
python manage.py runserver
```
Open your web browser and visit: **http://127.0.0.1:8000/**

---

## 📖 How to Use the Application (User Guide)

### For Farmers:
1. **Login/Register**: Navigate to the homepage and log in. 
   - *Demo Farmer Credentials*: Username: `farmer1`, Password: `farmer123`
2. **Dashboard**: Once logged in, you will see the latest cardamom market prices and a trend chart.
3. **AI Crop Doctor (Disease Detection)**:
   - Click on the "AI Detect" or "Crop Doctor" option in the navigation bar.
   - Upload a clear photo of the infected cardamom plant part.
   - Wait a few seconds for the AI to analyze the image.
   - Read the detailed diagnosis and treatment steps. You can toggle the language to your preference.
4. **Soil Testing**:
   - Go to the "Soil Test" section.
   - Fill out the request form with your farm details to schedule a professional test.

### For Administrators:
1. **Admin Login**: Go to the login page and use the admin credentials.
   - *Demo Admin Credentials*: Username: `admin`, Password: `admin123`
2. **Admin Dashboard**: View platform statistics, recent soil test requests, and user activity.
3. **Manage Prices**: You can view the scraped prices. To forcefully update prices immediately, click the "Update Prices" button on the dashboard or run `python manage.py scrape_prices` in the terminal.
4. **Review Soil Tests**: Approve, reject, or update the status of soil test requests made by farmers.

---

## ❓ Troubleshooting

- **"ModuleNotFoundError"**: You forgot to install the requirements. Make sure you activated your virtual environment and ran `pip install -r requirements.txt`.
- **"AI Analysis Failed"**: Verify that your internet connection is active and that your `GEMINI_API_KEY` in `settings.py` is correct and has not expired.
- **Blank Page or "Connection Refused"**: Ensure the local server is running in your terminal using `python manage.py runserver`.

---

<br>

<div align="center">
  <h3>Made with ❤️ by Adithyan</h3>
  <p>
    📧 Contact: <a href="mailto:mailforadithyan@gmail.com">mailforadithyan@gmail.com</a>
    <br>
    🌐 Portfolio: <a href="https://adithyan-portfolio.pages.dev/">https://adithyan-portfolio.pages.dev/</a>
  </p>
</div>
