# 🍲 Meal Planner Progetto (Django Full-Stack)

Questo è un progetto Django full-stack per la gestione del piano pasti settimanale e la generazione automatica della lista della spesa aggregata.

## 🎯 Obiettivo del Progetto

Il progetto ha lo scopo di semplificare la pianificazione dei pasti casalinghi, fornendo:
1.  **Database di Ricette e Ingredienti:** Un sistema per definire ricette e le relative quantità di ingredienti.
2.  **Pianificazione Settimanale:** Una griglia interattiva per assegnare ricette a giorni e pasti specifici.
3.  **Lista della Spesa Aggregata:** Una funzionalità core che somma automaticamente le quantità di tutti gli ingredienti necessari, tenendo conto delle ricette ripetute, per generare una lista di acquisti unica e ottimizzata.

## ⚙️ Configurazione Locale

Per avviare il progetto in locale:

1.  **Clona il repository:**
    ```bash
    git clone [https://github.com/maurobeltrami/meal_planner]
    cd meal_planner
    ```

2.  **Crea e attiva l'ambiente virtuale:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Installa le dipendenze:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Nota: Non hai ancora creato il file `requirements.txt`. Fai `pip freeze > requirements.txt` dopo il commit iniziale.)*

4.  **Esegui le migrazioni:**
    ```bash
    python manage.py migrate
    ```

5.  **Crea un utente amministratore e avvia il server:**
    ```bash
    python manage.py createsuperuser
    python manage.py runserver
    ```
    Accesso all'Admin: `http://127.0.0.1:8000/admin/`

## 🔗 Struttura dei Modelli

- **`Ingredient`**: Definisce l'articolo (es. Farina, g).
- **`Recipe`**: Nome del piatto (es. Lasagne).
- **`RecipeIngredient`**: Collegamento che definisce la quantità necessaria per ogni ricetta.
- **`WeeklyPlan`**: Traccia quali ricette sono pianificate per giorno e pasto.