import streamlit as st

# Configurare pagină - TREBUIE să fie prima comandă Streamlit
st.set_page_config(
    page_title="LED BLAST - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import database as db
import os
import time
import io
import base64
from PIL import Image
from datetime import datetime, timedelta

# Funcție pentru afișarea dashboard-ului
def show_dashboard():
    # Verificăm autentificarea
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.error("Nu ești autentificat! Te rugăm să te autentifici pentru a accesa dashboard-ul.")
        st.stop()
    
    # Inițializare session state pentru pagina curentă dacă nu există
    if 'page' not in st.session_state:
        st.session_state.page = 'dashboard'
    
    # Stilul UI-ului principal
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] > div {
            background-color: #f8f9fa;
            padding-top: 2rem;
            border-right: 1px solid #e9ecef;
        }
        .sidebar-menu-item {
            padding: 0.5rem 1rem;
            border-radius: 4px;
            margin-bottom: 0.5rem;
        }
        .sidebar-menu-item:hover {
            background-color: #e9ecef;
        }
        .dashboard-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 1rem;
        }
        .dashboard-subtitle {
            font-size: 1.5rem;
            color: #3498db;
            margin-bottom: 2rem;
        }
        .stat-card {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            text-align: center;
            margin-bottom: 1rem;
            transition: transform 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        .stat-label {
            font-size: 1.1rem;
            color: #7f8c8d;
        }
        .chart-container {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 1rem;
            margin-bottom: 1.5rem;
        }
        .table-container {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 1rem;
            margin-bottom: 1.5rem;
            max-height: 300px;
            overflow-y: auto;
        }
        .download-btn {
            display: inline-block;
            padding: 0.3rem 0.6rem;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.9rem;
        }
        .download-btn:hover {
            background-color: #2980b9;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Verificăm dacă utilizatorul are rolul de admin pentru a afișa pagini specifice
    is_admin = False
    if 'user' in st.session_state and st.session_state.user:
        is_admin = st.session_state.user.get('role') == 'Admin'
    
    # Bara laterală
    with st.sidebar:
        st.image("assets/logo.png", width=200)
        st.markdown("---")
        
        # Informații utilizator
        if 'user' in st.session_state and st.session_state.user:
            st.markdown(f"### Bun venit, {st.session_state.user.get('username')}!")
            st.markdown(f"*Rol: {st.session_state.user.get('role')}*")
            st.markdown("---")
        
        # Menu-ul principal
        st.header("Navigare")
        
        if st.button("📊 Dashboard", key="nav_dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
            
        if st.button("🏭 Furnizori", key="nav_suppliers"):
            st.session_state.page = "suppliers"
            st.rerun()
            
        if st.button("📦 Produse", key="nav_products"):
            st.session_state.page = "products"
            st.rerun()
            
        if st.button("📄 Documente", key="nav_documents"):
            st.session_state.page = "documents"
            st.rerun()
            
        # Pagina de management utilizatori este disponibilă doar pentru administratori
        if is_admin:
            if st.button("👥 Management Utilizatori", key="nav_users"):
                st.session_state.page = "user_management"
                st.rerun()
        
        st.markdown("---")
        
        # Buton de logout
        if st.button("🚪 Deconectare", key="logout_btn"):
            # Resetăm session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.authenticated = False
            st.session_state.current_page = 'login'
            st.rerun()
    
    # Header principal
    st.markdown('<div class="dashboard-title">Panou de Control</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">Sistem de administrare importuri LED/LCD</div>', unsafe_allow_html=True)
    
    # Pagina curentă - verifică dacă există, altfel setează default
    current_page = st.session_state.get('page', 'dashboard')
    
    # Afișează conținutul paginii corespunzătoare
    if current_page == 'dashboard':
        # Statistici generale
        try:
            # Obținem statistici din baza de date
            stats = db.get_stats()
        except:
            # Statistici simulate pentru demonstrație
            stats = {
                'suppliers_count': 24,
                'products_count': 156,
                'stock_value': 107000.0,
                'low_stock_count': 12,
                'users_count': 15,
                'documents_count': 78
            }
        
        # Row 1 - Carduri statistici
        st.subheader("Statistici Generale")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="stat-value">{stats["suppliers_count"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="stat-label">Furnizori</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="stat-value">{stats["products_count"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="stat-label">Produse</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="stat-value">{format_currency(stats["stock_value"])}</div>', unsafe_allow_html=True)
            st.markdown('<div class="stat-label">Valoare Stoc</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="stat-value">{stats["low_stock_count"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="stat-label">Alerte Stoc</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Row 2 - Grafice
        st.subheader("Analiză Stoc și Achiziții")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            stock_chart = generate_stock_chart()
            st.image(stock_chart, caption="Valoare Stoc per Categorie")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            purchases_chart = generate_purchases_chart()
            st.image(purchases_chart, caption="Achiziții Lunare per Furnizor")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Row 3 - Alerte și Activitate Recentă
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Alerte Stoc")
            st.markdown('<div class="table-container">', unsafe_allow_html=True)
            
            # Obținem alerte de stoc
            try:
                low_stock_alerts = db.get_stock_alerts()
            except:
                # Date simulate pentru demonstrație
                low_stock_alerts = [
                    {'id': 1, 'sku': 'LCD-1001', 'name': 'LCD Display 15"', 'stock_quantity': 3, 'stock_alert_threshold': 5, 'supplier_name': 'Shenzhen Display Tech'},
                    {'id': 2, 'sku': 'LCD-1005', 'name': 'LCD Display 19"', 'stock_quantity': 2, 'stock_alert_threshold': 5, 'supplier_name': 'Guangzhou LED Solutions'},
                    {'id': 3, 'sku': 'LED-2001', 'name': 'LED Backlight Module', 'stock_quantity': 4, 'stock_alert_threshold': 10, 'supplier_name': 'Hong Kong Electronics Ltd'}
                ]
            
            if low_stock_alerts:
                alerts_df = pd.DataFrame([
                    {
                        "SKU": alert['sku'],
                        "Produs": alert['name'],
                        "Stoc": alert['stock_quantity'],
                        "Limită": alert['stock_alert_threshold'],
                        "Furnizor": alert['supplier_name']
                    }
                    for alert in low_stock_alerts
                ])
                st.dataframe(alerts_df, use_container_width=True)
            else:
                st.info("Nu există alerte de stoc în acest moment.")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.subheader("Activitate Recentă")
            st.markdown('<div class="table-container">', unsafe_allow_html=True)
            
            # Simulăm activitate recentă
            activity_data = [
                {"Utilizator": "Maria", "Acțiune": "Adăugare produs", "Data": "12.05.2025 09:15"},
                {"Utilizator": "Ion", "Acțiune": "Actualizare stoc", "Data": "12.05.2025 08:45"},
                {"Utilizator": "Ana", "Acțiune": "Încărcare document", "Data": "11.05.2025 17:30"},
                {"Utilizator": "Mihai", "Acțiune": "Adăugare furnizor", "Data": "11.05.2025 14:20"},
                {"Utilizator": "Elena", "Acțiune": "Modificare produs", "Data": "10.05.2025 11:10"}
            ]
            
            activity_df = pd.DataFrame(activity_data)
            st.dataframe(activity_df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# Funcții utilitare
def format_currency(amount):
    if amount is None:
        return "-"
    return f"{amount:.2f} Lei"

def format_date(date_obj, format="%d.%m.%Y"):
    if date_obj is None:
        return "-"
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d %H:%M:%S")
        except:
            return date_obj
    return date_obj.strftime(format)

def get_binary_file_downloader_html(bin_file_path, file_label):
    with open(bin_file_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(bin_file_path)}" class="download-btn">{file_label}</a>'
    return href

# Funcții pentru generarea graficelor
def generate_stock_chart():
    # Simulăm date pentru grafic
    categories = ['LCD Panels', 'LED Components', 'Touch Screens', 'Power Supplies']
    stock_values = [45000, 32000, 18000, 12000]
    
    # Creăm graficul
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(categories, stock_values, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'])
    ax.set_ylabel('Valoare Stoc (Lei)')
    ax.set_title('Valoare Stoc per Categorie')
    
    # Adăugăm valori pe bare
    for i, v in enumerate(stock_values):
        ax.text(i, v + 1000, f"{v} Lei", ha='center')
    
    # Convertim graficul la un format care poate fi afișat în Streamlit
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    
    return buf

def generate_purchases_chart():
    # Simulăm date pentru grafic
    months = ['Ian', 'Feb', 'Mar', 'Apr', 'Mai']
    suppliers = ['Shenzhen Display', 'Guangzhou LED', 'Hong Kong Electronics']
    
    data = np.array([
        [15000, 18000, 12000, 20000, 25000],  # Shenzhen Display
        [8000, 10000, 15000, 12000, 9000],    # Guangzhou LED
        [5000, 7000, 9000, 6000, 8000]        # Hong Kong Electronics
    ])
    
    # Creăm graficul
    fig, ax = plt.subplots(figsize=(10, 5))
    
    bottom = np.zeros(len(months))
    for i, supplier in enumerate(suppliers):
        ax.bar(months, data[i], bottom=bottom, label=supplier)
        bottom += data[i]
    
    ax.set_ylabel('Valoare Achiziții (Lei)')
    ax.set_title('Achiziții Lunare per Furnizor')
    ax.legend()
    
    # Convertim graficul la un format care poate fi afișat în Streamlit
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    
    return buf