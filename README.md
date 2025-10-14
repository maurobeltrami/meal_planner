# 🍽️ Meal Planner Django App

Questa applicazione web permette di pianificare i pasti settimanali, gestire le ricette in modo dinamico e generare automaticamente la lista della spesa aggregata in base al piano settimanale.

## 🚀 Guida all'Installazione e Avvio

Segui questi passaggi per configurare e avviare l'applicazione nel tuo ambiente locale.

### Prerequisiti

- **Python** (versione 3.x)
- **pip** (gestore di pacchetti Python)
- **Git**

---

## Istruzioni di Setup

### 1. Clonazione del Repository

Clona il progetto da GitHub e naviga nella directory:

```bash
git clone https://github.com/maurobeltrami/meal_planner
cd meal_planner

python -m venv venv
source venv/bin/activate  # Linux/macOS
# 'venv\Scripts\activate' su Windows

pip install -r requirements.txt

python manage.py migrate

python manage.py collectstatic

python manage.py runserver