# 🌿 FarmCare: The Digital Companion for Cardamom Farmers

Welcome to **FarmCare**, an all-in-one digital companion designed specifically for Cardamom farmers in Kerala. FarmCare leverages advanced **Artificial Intelligence (AI)** to identify plant diseases from images and provides real-time market prices, empowering farmers to make data-driven decisions.

---

## 🚀 Key Features

- **🤖 AI Crop Doctor**: Instantly identify crop diseases by uploading a photo of a leaf or pod. Our AI provides diagnosis and treatment plans.
- **💰 Live Market Prices**: Get real-time auction prices and daily updates from major cardamom markets (Kumily, Vandanmedu, etc.).
- **📉 Price Trends**: Analyze historical price data with interactive charts to determine the best time to sell.
- **🧪 Soil Testing**: Request professional soil testing services directly through the platform.
- **🌍 Bilingual Support**: Get AI advice and platform instructions in both **English** and **Malayalam**.

---

## 🛠️ Step-by-Step Installation Guide (Non-IT Friendly)

You don't need any coding knowledge to get FarmCare up and running. Just follow these simple steps:

### 1. Install Python
*   Download Python from [python.org](https://www.python.org/downloads/).
*   **⚠️ CRITICAL**: When the installer opens, check the box that says **"Add Python to PATH"** before clicking Install.

### 2. Prepare the Project
*   Download and extract the `FarmCare` folder to your Desktop.
*   Open the folder. Click on the address bar at the top, type `cmd`, and press **Enter**.

### 3. Install Requirements
*   In the black window (Terminal) that appears, type this and press **Enter**:
    ```bash
    pip install -r requirements.txt
    ```

### 4. Setup the Database & Data
*   Type these two commands one after the other (press Enter after each):
    ```bash
    python manage.py migrate
    python seed_data.py
    ```

### 5. Add your AI Key & Secrets
*   Get a free key from [Google AI Studio](https://aistudio.google.com/app/apikey).
*   In the project folder, rename `.env.example` to `.env`.
*   Open `.env` with Notepad and paste your key where it says `YOUR_GEMINI_API_KEY_HERE`.

---

## 🚀 How to Launch the Website

Whenever you want to use the app, do this:
1.  Open the `FarmCare` folder.
2.  Type `cmd` in the address bar and press **Enter**.
3.  Run the server:
    ```bash
    python manage.py runserver
    ```
4.  **Open your Browser** (Chrome/Edge) and go to: [**http://127.0.0.1:8000/**](http://127.0.0.1:8000/)

### 🔑 Demo Login Details
| User Type | Username | Password |
| :--- | :--- | :--- |
| **Admin** (Control Center) | `admin` | `admin123` |
| **Farmer** (App View) | `farmer1` | `farmer123` |

---

## 🗄️ Understanding the Database (The Storage)

### What is the Database?
All your records—prices, reports, and farmer details—are stored in a single file called `db.sqlite3` inside the project folder.

### How to Connect and View Data Directly:
1.  **Download a Viewer**: Get [DB Browser for SQLite](https://sqlitebrowser.org/dl/).
2.  **Open the File**: Run the program and click "Open Database".
3.  **Select File**: Choose the `db.sqlite3` file in the project folder.
4.  **Browse Data**: Click the **"Browse Data"** tab to see your tables.

---

## 📂 Project Structure

- **`core/`**: The brain of the app (contains logic for AI, scraping, and user profiles).
- **`farmcare/`**: The configuration center (settings and links).
- **`templates/`**: The design files (what you see on the screen).
- **`static/`**: Styles, images, and visual elements.
- **`media/`**: Where your uploaded leaf photos are stored for analysis.
- **`db.sqlite3`**: The main database file.

---

## 🛠️ Technology Stack

- **Backend**: Django (Python)
- **AI Engine**: Google Gemini API
- **Database**: SQLite3
- **Scraper**: BeautifulSoup4 (for live prices)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

---

## 📧 Contact & Support

I am always happy to help! Whether you have questions about the app or want to discuss a new project, feel free to reach out.

- **📩 Email**: [mailforadithyan@gmail.com](mailto:mailforadithyan@gmail.com)
- **📞 Phone**: [+91 9778238064](tel:+919778238064)
- **🌐 Portfolio**: [adithyan-portfolio.pages.dev](https://adithyan-portfolio.pages.dev/)

---

### ❤️ Credits
**Made with love by adithyan**

*Empowering the backbone of Kerala through technology.*
