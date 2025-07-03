Here's a clean, professional, and well-structured `README.md` file for your GitHub repository:

---

````markdown
# 🧠 MSRIT CGPA Scraper (AIML Branch)

This is a simple Python script that automates the process of collecting CGPA data from the [MSRIT Results Portal](https://exam.msrit.edu/) using Selenium and Brave browser.

> ⚠️ This tool is for **educational and personal** use only. Use responsibly and do not overload the server.

---

## 📦 Features

- Uses **Selenium WebDriver** with stealth mode to avoid detection
- Automatically inputs a range of USNs (AIML branch format: `1MS23ISxxx`)
- Collects and stores **CGPA** values
- Exports the results to a CSV file (`msrit_cgpa_csAIML.csv`)

---

## 🚀 Prerequisites

- macOS with ARM (M1/M2/M3 chip)
- [Python 3.8+](https://www.python.org/downloads/)
- [Brave Browser](https://brave.com/download/)
- [ChromeDriver (mac-arm64)](https://googlechromelabs.github.io/chrome-for-testing/)

---

## 🛠️ Setup Instructions

1. **Clone the Repository**

```bash
git clone https://github.com/your-username/msrit-cgpa-scraper.git
cd msrit-cgpa-scraper
````

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Run the Script**

```bash
python main.py
```

4. **Manual Step**

* Solve the CAPTCHA on the website manually
* Enter **any valid USN** once to load the results page
* Press `Enter` in the terminal when prompted

---

## 📁 Output

A file named `msrit_cgpa_csAIML.csv` will be generated with the following columns:

* `USN`
* `CGPA`

Example:

```
USN,CGPA
1MS23IS001,9.1
1MS23IS002,8.7
...
```

---

## 🧑‍💻 Author

**Nithish Reddy**
Feel free to connect or raise issues in the repo for suggestions/improvements.

---

## 📜 Disclaimer

This project is intended for **learning and personal use only**. Do not misuse or deploy this at scale. Use at your own risk.

```

---

Let me know if you want badges, GitHub Actions, or license information added!
```
