#!/bin/bash
# Script pentru pornirea aplicației

# Verific dacă Python este instalat
if ! command -v python3 &> /dev/null
then
    echo "Python 3 nu este instalat. Vă rugăm să instalați Python 3."
    exit 1
fi

# Verific dacă există un mediu virtual, dacă nu, îl creez
if [ ! -d "venv" ]; then
    echo "Creez mediu virtual Python..."
    python3 -m venv venv
fi

# Activez mediul virtual
source venv/bin/activate

# Instalez dependențele
echo "Instalez dependențele necesare..."
pip install -r requirements.txt

# Creez directoarele necesare dacă nu există
mkdir -p product_images
mkdir -p uploaded_documents

# Pornesc aplicația
echo "Pornesc aplicația Streamlit..."
streamlit run main.py --server.port 5000 --server.address 0.0.0.0 --server.headless true