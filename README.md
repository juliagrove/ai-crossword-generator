# 🧩 **AI Crossword Generator**
# **Deployed at:**  https://ai-crossword-generator.onrender.com  *(server may take a moment to wake up)*
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-darkgreen?logo=django&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Gemini%20API-Google%20AI-orange?logo=google&logoColor=white)
## **Overview:** an AI-powered crossword generator that builds an interactive crossword puzzle from the users category.
---
## **Highlights & How it works**
1. User provides a category
2. Gemini LLM generates words and clues in the category, using **Gemini Structured Outputs** for consistent JSON outputs
3. A custom **constraint based algorithm** individually places words, starting with the longest word
4. UI renders an interactive crossword puzzle, with live input checking
---
## **Tech Stack**
- **Backend:** Django (Python)
- **Database:** PostgreSQL
- **AI:** Google Gemini LLM
- **Frontend:** JavaScript, HTML/CSS (via Django templates)
---
## **Demo**
![AI Crossword Demo](demo/demo.gif)
