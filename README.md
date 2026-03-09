# 🌿 FarmCare: Smart Cardamom Farming Platform

Welcome to **FarmCare**, an all-in-one digital companion designed specifically for Cardamom farmers in Kerala. FarmCare uses advanced **Artificial Intelligence (AI)** to identify diseases from a simple photo and provides real-time market prices to help you get the best value for your crop.

---

## ✨ Key Features for Farmers

*   **🤖 AI Crop Doctor**: Take a photo of a leaf or cardamom pod, and our AI will instantly identify if there is a disease and tell you exactly how to treat it.
*   **💰 Live Market Prices**: Get the latest auction prices from major Kerala markets (Kumily, Vandanmedu, Puttady, etc.) updated daily.
*   **📉 Price Trends**: See how prices have changed over the last 7 days to decide the best time to sell.
*   **🧪 Soil Testing**: Request a professional soil test directly through the app to understand your land's health.
*   **🗣️ Bilingual Support**: All AI advice is available in both **English and Malayalam**.

---

## 🛠️ Simple Installation Guide (For Everyone)

You don't need to be a computer expert to set this up. Follow these simple steps:

### Step 1: Install Python
Python is the "engine" that runs this app.
1.  Go to [python.org](https://www.python.org/downloads/) and click the big yellow **Download Python** button.
2.  **IMPORTANT**: When installing, make sure to check the box that says **"Add Python to PATH"**.

### Step 2: Get the Project Files
1.  Download the project folder and extract it to a place you can find easily (like your Desktop).

### Step 3: Open the Project Folder
1.  Open the folder you just extracted.
2.  Click on the top address bar in your file explorer, type `cmd`, and press **Enter**. A black window (Terminal) will open.

### Step 4: Install the Required Tools
In that black window, copy and paste the following line and press **Enter**:
```bash
pip install -r requirements.txt
```
*Wait for it to finish. It will download all the necessary components.*

### Step 5: Set Up the Database
This prepares the app to store your reports and prices. Type these two lines one by one:
```bash
python manage.py migrate
python seed_data.py
```

### Step 6: Add your AI Key (Crucial)
To make the AI work, you need a free key from Google.
1.  Get a free key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Open the file named `farmcare/settings.py` with Notepad.
3.  Look for `GEMINI_API_KEY` and paste your key inside the quotes like this:
    `GEMINI_API_KEY = 'YOUR_SECRET_KEY_HERE'`

---

## 🚀 How to Start the App

Whenever you want to use FarmCare, follow these steps:
1.  Open the project folder.
2.  Open the terminal (type `cmd` in the address bar again).
3.  Type this command and press **Enter**:
    ```bash
    python manage.py runserver
    ```
4.  Open your web browser (Chrome or Edge) and go to:
    **http://127.0.0.1:8000/**

---

## 🔑 Demo Login Accounts

| Role | Username | Password |
| :--- | :--- | :--- |
| **Admin** (Control Panel) | `admin` | `admin123` |
| **Farmer** (Your View) | `farmer1` | `farmer123` |

---

## 📱 Using the AI Crop Doctor

1.  Log in as a **Farmer**.
2.  Click on **AI Detect** in the menu.
3.  **Upload a photo** of the affected cardamom part.
4.  Wait about 5-10 seconds while the "Expert AI Pathologist" analyzes your crop.
5.  Read the results! You can switch between **English** and **Malayalam** using the toggle at the top.

---

## 📈 Price Updates
The app automatically tries to get the latest prices from the Spices Board website. 
*   **To update manually**: Admins can click the "Update Prices" button on their dashboard.
*   **Technical Tip**: You can also run `python manage.py scrape_prices` in the terminal to force an update.

---

## ❓ Troubleshooting

*   **"Python not found"**: Ensure you checked the "Add Python to PATH" box during installation. If not, reinstall Python.
*   **"Analysis Failed"**: Check your internet connection or ensure your Gemini API Key is correct in `settings.py`.
*   **Blank Page**: Make sure the server is running (Step 4 of "How to Start").

---

**Developed with 💚 for the Cardamom Farming Community of Kerala.**
