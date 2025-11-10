# 🧩 AI Crossword Generator
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-darkgreen?logo=django&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Gemini%20API-Google%20AI-orange?logo=google&logoColor=white)

## **Project:** an AI-powered crossword generator that builds a playable crossword puzzle with the users category

---

## This project demonstrates:
- Custom constraint based algorithms  
- Prompt engineering  
- API integration  
- Django + Python development

---

## Instructions to Run the Crossword App Locally
1. **Clone the repo:**
    ```bash 
    git clone https://github.com/juliagrove/ai-crossword-generator.git
    ```

2. **Set up your Environment**
   - Create and activate the conda env: 

   ```bash
   cd ai-crossword-generator

   conda env create -f environment.yml
   
   conda activate ai_crossword_env
   ```
3. **Obtain a Gemini API key**
   - Create a `.env` file in the root directory and add: `GEMINI_API_KEY = "YOUR-API-KEY"`

4. **Run the App**
   ```bash 
    python manage.py runserver
    ```

5. **Navigate to Local Host**
   - Open a browser and navigate to http://127.0.0.1:8000/crossword/

---

## Tech Stack
- **Backend:** Django (Python)
- **AI:** Google Gemini LLM
- **Frontend:** HTML/CSS
