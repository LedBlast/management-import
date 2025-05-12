import streamlit as st

# Configurare pagină - TREBUIE să fie prima comandă Streamlit
st.set_page_config(
    page_title="LED BLAST - Management System",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

import hashlib
import random
import string
import time
from PIL import Image
import io
import base64
import database as db
import os

# Ascunde complet bara laterală și toate elementele sale până la autentificare
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.markdown("""
    <style>
        [data-testid="collapsedControl"] {
            display: none
        }
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Funcții pentru autentificare
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    """Verifică credențialele utilizatorului în baza de date."""
    password_hash = hash_password(password)
    try:
        user = db.verify_user_credentials(username, password_hash)
        return user
    except Exception as e:
        st.error(f"Eroare la verificarea credențialelor: {str(e)}")
        return None

def render_recaptcha():
    """Simulează integrarea reCAPTCHA."""
    # Aceasta e doar o simulare a reCAPTCHA - într-o implementare reală, am folosi JavaScript și API-ul Google
    st.markdown("""
    <div style="border: 1px solid #ccc; border-radius: 4px; padding: 10px; background-color: #f9f9f9; margin: 15px 0;">
        <div style="display: flex; align-items: center;">
            <div style="margin-right: 10px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 64 64">
                    <path fill="#4CAF50" d="M32,2A30,30,0,1,0,62,32,30,30,0,0,0,32,2Zm0,54A24,24,0,1,1,56,32,24,24,0,0,1,32,56Z"/>
                    <path fill="#4CAF50" d="M32,22a1.5,1.5,0,0,0-1.5,1.5v15a1.5,1.5,0,0,0,3,0v-15A1.5,1.5,0,0,0,32,22Z"/>
                    <circle fill="#4CAF50" cx="32" cy="46" r="2"/>
                </svg>
            </div>
            <div>
                <h4 style="margin: 0; color: #555;">reCAPTCHA Advanced</h4>
                <p style="margin: 5px 0 0; font-size: 0.8em; color: #777;">Protejat de reCAPTCHA</p>
            </div>
        </div>
        <div style="margin-top: 10px; font-size: 0.9em; color: #555;">Acest site este protejat de reCAPTCHA și se aplică <a href="#">Politica de confidențialitate</a> și <a href="#">Termenii de utilizare</a> Google.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # În mod real, aici am avea un ID reCAPTCHA
    # Simulăm verificarea reCAPTCHA
    if 'recaptcha_verified' not in st.session_state:
        st.session_state.recaptcha_verified = True  # În producție, aceasta ar fi validată prin API
    
    return st.session_state.recaptcha_verified

# Inițializarea session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'user' not in st.session_state:
    st.session_state.user = None

if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = 0

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'

# Custom CSS pentru pagina de login
st.markdown("""
<style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background-color: white;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 20px;
    }
    .form-header {
        text-align: center;
        margin-bottom: 20px;
        color: #003366;
    }
    .captcha-container {
        margin: 20px 0;
        text-align: center;
    }
    .links-container {
        display: flex;
        justify-content: space-between;
        margin-top: 15px;
        font-size: 0.9em;
    }
    .auth-btn {
        width: 100%;
    }
    .stButton>button {
        width: 100%;
    }
    footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 10px;
        font-size: 0.8em;
        color: #666;
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

# Funcție pentru afișarea titlului
def show_title():
    st.markdown('<div class="logo-container"><h1 style="color:#003366; text-align:center;">LED BLAST</h1></div>', unsafe_allow_html=True)

# Funcții utilitare (definite aici pentru a fi disponibile în dashboard)
def format_currency(amount):
    if amount is None:
        return "-"
    return f"{amount:.2f} Lei"

def format_date(date_obj, format="%d.%m.%Y"):
    if date_obj is None:
        return "-"
    from datetime import datetime
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
    import matplotlib.pyplot as plt
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
    
    import numpy as np
    data = np.array([
        [15000, 18000, 12000, 20000, 25000],  # Shenzhen Display
        [8000, 10000, 15000, 12000, 9000],    # Guangzhou LED
        [5000, 7000, 9000, 6000, 8000]        # Hong Kong Electronics
    ])
    
    # Creăm graficul
    import matplotlib.pyplot as plt
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

# Funcție pentru afișarea dashboard-ului
def show_dashboard():
    # Verificăm dacă utilizatorul are rolul de admin pentru a afișa pagini specifice
    is_admin = False
    if 'user' in st.session_state and st.session_state.user:
        is_admin = st.session_state.user.get('role') == 'Admin'
    
    # Adăugăm funcția de deconectare în partea dreaptă sub opțiunea settings
    with st.container():
        col1, col2, col3 = st.columns([1, 6, 1])
        with col3:
            # Adăugăm un buton de deconectare în colțul dreapta sus
            if st.button("🚪 Logout", key="top_logout_btn"):
                # Resetăm session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.session_state.authenticated = False
                st.session_state.current_page = 'login'
                st.rerun()
    
    # Bara laterală
    with st.sidebar:
        st.image("assets/logo.png", width=200)
        st.markdown("---")
        
        # Informații utilizator
        if 'user' in st.session_state and st.session_state.user:
            st.markdown(f"### Bun venit, {st.session_state.user.get('username')}!")
            st.markdown(f"*Rol: {st.session_state.user.get('role')}*")
            st.markdown("---")
        
        # Menu-ul principal cu iconițe
        st.header("Navigare")
        
        # Stilizăm butoanele de meniu
        st.markdown("""
        <style>
            div.stButton > button {
                width: 100%;
                text-align: left;
                padding: 10px;
                border: none;
                background-color: transparent;
                font-size: 1rem;
                font-weight: 500;
                transition: background-color 0.3s;
            }
            div.stButton > button:hover {
                background-color: rgba(0, 0, 0, 0.05);
            }
            .active-menu-item {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 4px;
            }
        </style>
        """, unsafe_allow_html=True)
        
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
                import pandas as pd
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
            
            import pandas as pd
            activity_df = pd.DataFrame(activity_data)
            st.dataframe(activity_df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    elif current_page == 'suppliers':
        st.subheader("Pagina Furnizori")
        st.info("Navigați la pagina de furnizori din meniul lateral pentru a accesa toate funcționalitățile.")
    elif current_page == 'products':
        st.subheader("Pagina Produse")
        st.info("Navigați la pagina de produse din meniul lateral pentru a accesa toate funcționalitățile.")
    elif current_page == 'documents':
        st.subheader("Pagina Documente")
        st.info("Navigați la pagina de documente din meniul lateral pentru a accesa toate funcționalitățile.")
    elif current_page == 'user_management' and is_admin:
        st.subheader("Management Utilizatori")
        st.info("Navigați la pagina de management utilizatori din meniul lateral pentru a accesa toate funcționalitățile.")
    elif current_page == 'user_management' and not is_admin:
        st.error("Nu aveți drepturi de acces la această pagină!")
        st.session_state.page = 'dashboard'
        st.rerun()

# Funcții pentru navigare între pagini
def go_to_login():
    st.session_state.current_page = 'login'

def go_to_register():
    st.session_state.current_page = 'register'

def go_to_forgot_password():
    st.session_state.current_page = 'forgot_password'

def go_to_dashboard():
    st.session_state.current_page = 'dashboard'

# Verifică dacă utilizatorul este autentificat
if st.session_state.authenticated:
    # Dacă este autentificat, afișăm dashboard-ul
    show_dashboard()
    st.stop()

def generate_purchases_chart():
    # Simulăm date pentru grafic
    months = ['Ian', 'Feb', 'Mar', 'Apr', 'Mai']
    suppliers = ['Shenzhen Display', 'Guangzhou LED', 'Hong Kong Electronics']
    
    import numpy as np
    data = np.array([
        [15000, 18000, 12000, 20000, 25000],  # Shenzhen Display
        [8000, 10000, 15000, 12000, 9000],    # Guangzhou LED
        [5000, 7000, 9000, 6000, 8000]        # Hong Kong Electronics
    ])
    
    # Creăm graficul
    import matplotlib.pyplot as plt
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

# Pagină de login
if st.session_state.current_page == 'login':
    show_title()
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="form-header">Autentificare</h2>', unsafe_allow_html=True)
    
    # Formular de login
    username = st.text_input("Utilizator", key="login_username")
    password = st.text_input("Parolă", type="password", key="login_password")
    
    # Afișăm reCAPTCHA dacă e nevoie (după un număr de încercări eșuate)
    if st.session_state.login_attempts >= 2:
        captcha_verified = render_recaptcha()
    else:
        captcha_verified = True
    
    # Buton de login
    if st.button("Autentificare", key="login_btn", type="primary"):
        if not username or not password:
            st.error("Numele de utilizator și parola sunt obligatorii!")
        elif st.session_state.login_attempts >= 2 and not captcha_verified:
            st.error("Verificarea reCAPTCHA este necesară!")
        else:
            # Verifică credențialele
            user = None
            if username == "test" and password == "test":
                # Credențiale hardcodate pentru demo
                user = {
                    'id': 1,
                    'username': 'test',
                    'email': 'mihai.bogdan1010@yahoo.com',
                    'role': 'Admin'
                }
            else:
                # Verificăm în baza de date
                user = verify_user(username, password)
            
            if user:
                st.session_state.authenticated = True
                st.session_state.user = {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role'],
                    'last_login': time.time()
                }
                st.success("Autentificare reușită!")
                time.sleep(1)  # Mică întârziere pentru a vedea mesajul de succes
                go_to_dashboard()
                st.rerun()
            else:
                st.error("Utilizator sau parolă incorectă!")
                st.session_state.login_attempts += 1
    
    # Link-uri pentru înregistrare și recuperare parolă
    st.markdown('<div class="links-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ai uitat parola?", key="forgot_pwd_btn"):
            go_to_forgot_password()
            st.rerun()
    with col2:
        if st.button("Creează cont", key="register_btn"):
            go_to_register()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Pagină de înregistrare
elif st.session_state.current_page == 'register':
    show_title()
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="form-header">Înregistrare Cont Nou</h2>', unsafe_allow_html=True)
    
    # Formular de înregistrare
    username = st.text_input("Nume utilizator", key="reg_username")
    email = st.text_input("Email", key="reg_email")
    password = st.text_input("Parolă", type="password", key="reg_password")
    confirm_password = st.text_input("Confirmă parola", type="password", key="reg_confirm_password")
    
    # Afișare reCAPTCHA
    captcha_verified = render_recaptcha()
    
    # Termeni și condiții
    terms_accepted = st.checkbox("Am citit și sunt de acord cu termenii și condițiile")
    
    # Buton de înregistrare
    if st.button("Înregistrare", key="register_submit_btn", type="primary"):
        if not username or not email or not password or not confirm_password:
            st.error("Toate câmpurile sunt obligatorii!")
        elif password != confirm_password:
            st.error("Parolele nu coincid!")
        elif not captcha_verified:
            st.error("Verificarea reCAPTCHA este necesară!")
        elif not terms_accepted:
            st.error("Trebuie să accepți termenii și condițiile!")
        else:
            # Încercăm să înregistrăm utilizatorul în baza de date
            try:
                # Hash-uim parola
                password_hash = hash_password(password)
                
                # Salvăm utilizatorul
                user_id = db.save_user(username, email, password_hash, role='Vizualizator')
                
                if user_id:
                    st.success("Cont creat cu succes! Te poți autentifica acum.")
                    time.sleep(2)  # Mică întârziere pentru a vedea mesajul
                    go_to_login()
                    st.rerun()
                else:
                    st.error("Eroare la crearea contului. Te rugăm să încerci din nou.")
            except Exception as e:
                st.error(f"Eroare la înregistrare: {str(e)}")
    
    # Link înapoi la login
    if st.button("Înapoi la autentificare", key="back_to_login_btn"):
        go_to_login()
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Pagină de recuperare parolă
elif st.session_state.current_page == 'forgot_password':
    show_title()
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="form-header">Recuperare Parolă</h2>', unsafe_allow_html=True)
    
    # Formular de recuperare parolă
    email = st.text_input("Adresa de email", key="forgot_email")
    
    # Afișare reCAPTCHA
    captcha_verified = render_recaptcha()
    
    # Buton de trimitere
    if st.button("Trimite link recuperare", key="forgot_submit_btn", type="primary"):
        if not email:
            st.error("Adresa de email este obligatorie!")
        elif not captcha_verified:
            st.error("Verificarea reCAPTCHA este necesară!")
        else:
            # Verificăm dacă email-ul există în baza de date
            try:
                user = db.get_user_by_email(email)
                if user:
                    # Simulăm trimiterea email-ului de recuperare
                    st.success(f"Un email cu instrucțiuni pentru resetarea parolei a fost trimis la adresa {email}!")
                    time.sleep(2)  # Mică întârziere pentru a vedea mesajul
                    go_to_login()
                    st.rerun()
                else:
                    st.error("Nu există niciun cont asociat cu această adresă de email.")
            except Exception as e:
                st.error(f"Eroare la procesarea cererii: {str(e)}")
    
    # Link înapoi la login
    if st.button("Înapoi la autentificare", key="back_to_login_from_forgot_btn"):
        go_to_login()
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown(
    '<footer>© 2025 LED BLAST. Toate drepturile rezervate.</footer>',
    unsafe_allow_html=True
)