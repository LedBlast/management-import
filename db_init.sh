#!/bin/bash
# Script pentru inițializarea bazei de date

# Verifică dacă PostgreSQL este instalat
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL nu este instalat. Vă rugăm să instalați PostgreSQL."
    exit 1
fi

# Solicită credențiale pentru baza de date
read -p "Introduceți numele bazei de date: " DB_NAME
read -p "Introduceți utilizatorul PostgreSQL: " DB_USER
read -s -p "Introduceți parola utilizatorului: " DB_PASSWORD
echo ""

# Creează baza de date dacă nu există
echo "Creez baza de date $DB_NAME dacă nu există..."
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h localhost -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "Baza de date există deja."

# Importă schema și datele din backup.sql
echo "Importă schema și datele în baza de date..."
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h localhost -d $DB_NAME -f backup.sql

# Creează fișierul .env cu configurația bazei de date
echo "Creez fișierul .env cu configurația bazei de date..."
cat > .env << EOF
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
PGHOST=localhost
PGPORT=5432
PGDATABASE=$DB_NAME
PGUSER=$DB_USER
PGPASSWORD=$DB_PASSWORD
EOF

echo "Configurația bazei de date a fost salvată în fișierul .env"
echo "Baza de date a fost inițializată cu succes!"