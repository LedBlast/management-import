# Sistem de Administrare Importuri LED/LCD

Un sistem web avansat de management al stocurilor pentru importuri de produse LED/LCD, conceput pentru eficientizarea proceselor de gestionare și monitorizare.

## Caracteristici

- Autentificare utilizatori cu opțiune 2FA
- Gestiune furnizori și produse
- Monitorizare stocuri cu alerte pentru niveluri scăzute
- Management documente cu suport pentru încărcare și vizualizare
- Grafice interactive pentru analiza datelor
- Interfață responsivă adaptată pentru dispozitive mobile

## Tehnologii Utilizate

- Streamlit pentru interfață web
- PostgreSQL pentru baza de date
- Flask pentru autentificare
- Biblioteci Python: Pandas, Matplotlib, NumPy, PIL

## Cerințe de Sistem

- Python 3.8+
- PostgreSQL
- Dependențe Python (listate în `requirements.txt`)

## Instalare

1. Extrageți arhiva:
   ```
   tar -xzf led_blast_system.tar.gz
   cd export_package
   ```

2. Inițializați baza de date (necesită PostgreSQL instalat):
   ```
   ./db_init.sh
   ```
   Scriptul va solicita numele bazei de date, utilizator și parolă, apoi va crea baza de date și va importa schema și datele demonstrative.

3. Porniți aplicația folosind scriptul automat:
   ```
   ./start.sh
   ```
   
Scriptul de pornire va instala automat toate dependențele necesare într-un mediu virtual și va lansa aplicația pe portul 5000.

## Structura Aplicației

- `/main.py` - Punctul de intrare al aplicației
- `/pages/` - Module pentru diferite secțiuni ale aplicației
- `/database.py` - Funcții pentru interacțiunea cu baza de date
- `/autentificare.py` - Sistem de autentificare
- `/dashboard.py` - Panoul principal de administrare

## Date Autentificare (Demo)

- Utilizator: test
- Parolă: test
- Email: mihai.bogdan1010@yahoo.com

## Implementare

Pentru a implementa acest sistem pe serverul dumneavoastră:

1. Configurați o bază de date PostgreSQL
2. Actualizați credențialele în fișierul `.env` sau variabilele de mediu
3. Rulați scriptul `database.py` pentru a crea tabelele inițiale și a încărca date demonstrative
4. Lansați aplicația cu `streamlit run main.py`
5. Accesați aplicația la adresa `http://your-server:5000`