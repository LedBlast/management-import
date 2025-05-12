import streamlit as st

# Configurare pagină - TREBUIE să fie prima comandă Streamlit
st.set_page_config(
    page_title="LED BLAST - Autentificare",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

import hashlib
import random
import string
import time
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import database as db
import os
import dashboard

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
    dashboard.show_dashboard()
    st.stop()

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