import streamlit as st
import pandas as pd
import database as db
import datetime
import secrets
import hashlib

# Configurare pagină
st.set_page_config(page_title='Gestionare Utilizatori - LED/LCD Import Management', layout='wide')

# Header
st.title('Gestionare Utilizatori')
st.markdown('Administrare utilizatori pentru sistemul de management importuri LED/LCD.')

# Funcții utilitare
def hash_password(password):
    # În producție, folosiți bcrypt sau argon2
    return hashlib.sha256(password.encode()).hexdigest()

def generate_password():
    # Generează o parolă aleatoare de 10 caractere
    return secrets.token_urlsafe(8)

def get_users():
    """Simulează obținerea utilizatorilor din baza de date"""
    return [
        {"id": 1, "username": "Admin", "email": "admin@example.com", "role": "Admin", "status": "Activ", "last_login": datetime.datetime.now()},
        {"id": 2, "username": "Editor1", "email": "editor1@example.com", "role": "Editor", "status": "Activ", "last_login": datetime.datetime.now() - datetime.timedelta(days=1)},
        {"id": 3, "username": "Vizualizator1", "email": "viewer1@example.com", "role": "Vizualizator", "status": "Activ", "last_login": datetime.datetime.now() - datetime.timedelta(days=2)},
        {"id": 4, "username": "Editor2", "email": "editor2@example.com", "role": "Editor", "status": "Inactiv", "last_login": datetime.datetime.now() - datetime.timedelta(days=7)}
    ]

# Verificare acces
if 'user' not in st.session_state or st.session_state.user is None or st.session_state.user.get('role') != 'Admin':
    st.warning("Această pagină este disponibilă doar pentru administratori. Te rugăm să te autentifici cu un cont de administrator.")
    st.stop()

# Tab-uri principale
tabs = st.tabs(["Listă Utilizatori", "Adaugă Utilizator", "Roluri și Permisiuni", "Jurnal Activitate"])

with tabs[0]:
    st.header("Utilizatori Înregistrați")
    
    # Filtre
    col1, col2 = st.columns(2)
    with col1:
        role_filter = st.selectbox("Filtru Rol", ["Toate", "Admin", "Editor", "Vizualizator"])
    with col2:
        status_filter = st.selectbox("Filtru Status", ["Toate", "Activ", "Inactiv"])
    
    # Obținem lista de utilizatori
    users = get_users()
    
    # Aplicăm filtrele
    if role_filter != "Toate":
        users = [u for u in users if u['role'] == role_filter]
    if status_filter != "Toate":
        users = [u for u in users if u['status'] == status_filter]
    
    # Afișare tabel utilizatori
    if not users:
        st.info("Nu există utilizatori care să corespundă criteriilor de filtrare.")
    else:
        user_table = []
        for u in users:
            user_table.append({
                "ID": u['id'],
                "Utilizator": u['username'],
                "Email": u['email'],
                "Rol": u['role'],
                "Status": u['status'],
                "Ultima Autentificare": u['last_login'].strftime('%d.%m.%Y %H:%M')
            })
        
        st.dataframe(pd.DataFrame(user_table))
        
        # Acțiuni pentru utilizatorul selectat
        user_id = st.number_input("ID Utilizator pentru Acțiuni", min_value=1, max_value=max([u['id'] for u in users]), step=1)
        selected_user = next((u for u in users if u['id'] == user_id), None)
        
        if selected_user:
            st.subheader(f"Acțiuni pentru {selected_user['username']}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_role = st.selectbox("Rol", ["Admin", "Editor", "Vizualizator"], 
                                      index=["Admin", "Editor", "Vizualizator"].index(selected_user['role']))
                if st.button("Schimbă Rol"):
                    st.success(f"Rolul utilizatorului {selected_user['username']} a fost schimbat la {new_role}")
            
            with col2:
                status_action = "Dezactivează" if selected_user['status'] == "Activ" else "Activează"
                if st.button(status_action):
                    new_status = "Inactiv" if selected_user['status'] == "Activ" else "Activ"
                    st.success(f"Statusul utilizatorului {selected_user['username']} a fost schimbat la {new_status}")
            
            with col3:
                if st.button("Resetează Parola"):
                    new_password = generate_password()
                    st.success(f"Parola utilizatorului {selected_user['username']} a fost resetată.")
                    st.info(f"Noua parolă este: {new_password} (Aceasta ar fi trimisă prin email)")

with tabs[1]:
    st.header("Adaugă Utilizator Nou")
    
    with st.form("add_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Nume Utilizator*")
            email = st.text_input("Email*")
            role = st.selectbox("Rol*", ["Admin", "Editor", "Vizualizator"])
        
        with col2:
            password = st.text_input("Parolă", value=generate_password())
            st.info("Lasă parola generată sau introdu una nouă")
            send_email = st.checkbox("Trimite credențiale prin email", value=True)
        
        submit_button = st.form_submit_button("Adaugă Utilizator")
        
        if submit_button:
            if not username or not email:
                st.error("Numele de utilizator și emailul sunt obligatorii!")
            else:
                # Simulăm adăugarea utilizatorului
                st.success(f"Utilizatorul {username} a fost adăugat cu succes!")
                
                if send_email:
                    st.info(f"Un email cu credențialele a fost trimis la adresa {email}")

with tabs[2]:
    st.header("Roluri și Permisiuni")
    
    # Descrierea rolurilor
    role_descriptions = {
        "Admin": {
            "descriere": "Control complet asupra sistemului",
            "permisiuni": [
                "Gestionare utilizatori (adăugare, editare, ștergere)",
                "Acces la toate modulele sistemului",
                "Configurare sistem",
                "Gestionare completă furnizori și produse",
                "Acces la toate rapoartele și statisticile"
            ]
        },
        "Editor": {
            "descriere": "Gestionare conținut și date",
            "permisiuni": [
                "Gestionare furnizori (adăugare, editare)",
                "Gestionare produse (adăugare, editare)",
                "Gestionare stoc (adăugare)",
                "Încărcare documente",
                "Vizualizare rapoarte"
            ]
        },
        "Vizualizator": {
            "descriere": "Doar vizualizare informații",
            "permisiuni": [
                "Vizualizare furnizori",
                "Vizualizare produse",
                "Vizualizare stoc",
                "Vizualizare documente",
                "Generare rapoarte de bază"
            ]
        }
    }
    
    for role, details in role_descriptions.items():
        with st.expander(f"Rol: {role}", expanded=(role == "Admin")):
            st.markdown(f"**Descriere:** {details['descriere']}")
            st.markdown("**Permisiuni:**")
            for permission in details['permisiuni']:
                st.markdown(f"- {permission}")
    
    # Opțiune de editare permisiuni pentru roluri (nu este implementată complet)
    st.subheader("Personalizare Permisiuni")
    st.info("Această secțiune permite personalizarea permisiunilor pentru fiecare rol în mod granular.")
    
    role_to_edit = st.selectbox("Selectează Rol pentru Editare", ["Admin", "Editor", "Vizualizator"])
    
    # Afișăm permisiunile curente și opțiunile de modificare
    module_permissions = {
        "Utilizatori": ["Vizualizare", "Adăugare", "Editare", "Ștergere"],
        "Furnizori": ["Vizualizare", "Adăugare", "Editare", "Ștergere"],
        "Produse": ["Vizualizare", "Adăugare", "Editare", "Ștergere"],
        "Stoc": ["Vizualizare", "Adăugare", "Editare", "Ștergere"],
        "Documente": ["Vizualizare", "Adăugare", "Ștergere"],
        "Rapoarte": ["Vizualizare", "Generare", "Export"]
    }
    
    st.markdown(f"**Permisiuni pentru rolul {role_to_edit}:**")
    
    # Generăm checkboxuri pentru fiecare permisiune
    for module, permissions in module_permissions.items():
        st.markdown(f"**{module}:**")
        cols = st.columns(len(permissions))
        for i, perm in enumerate(permissions):
            # Presetăm permisiunile în funcție de rol
            default_value = False
            if role_to_edit == "Admin":
                default_value = True
            elif role_to_edit == "Editor" and module != "Utilizatori" and perm != "Ștergere":
                default_value = True
            elif role_to_edit == "Vizualizator" and perm == "Vizualizare":
                default_value = True
            
            cols[i].checkbox(perm, value=default_value, key=f"{module}_{perm}_{role_to_edit}")
    
    if st.button("Salvează Permisiuni"):
        st.success(f"Permisiunile pentru rolul {role_to_edit} au fost actualizate!")

with tabs[3]:
    st.header("Jurnal Activitate Utilizatori")
    
    # Filtre pentru jurnal
    col1, col2 = st.columns(2)
    with col1:
        user_filter = st.selectbox("Utilizator", ["Toți"] + [u['username'] for u in get_users()])
    with col2:
        action_filter = st.selectbox("Tip Acțiune", ["Toate", "Autentificare", "Adăugare", "Editare", "Ștergere", "Descărcare", "Export"])
    
    # Interval de timp
    date_col1, date_col2 = st.columns(2)
    with date_col1:
        start_date = st.date_input("De la data", value=datetime.datetime.now() - datetime.timedelta(days=7))
    with date_col2:
        end_date = st.date_input("Până la data", value=datetime.datetime.now())
    
    # Simulăm date de audit
    audit_logs = [
        {"id": 1, "timestamp": datetime.datetime.now() - datetime.timedelta(hours=2), "user": "Admin", "action": "Autentificare", "details": "Autentificare reușită", "ip": "192.168.1.1"},
        {"id": 2, "timestamp": datetime.datetime.now() - datetime.timedelta(hours=1), "user": "Admin", "action": "Editare", "details": "Utilizator ID: 2 editat", "ip": "192.168.1.1"},
        {"id": 3, "timestamp": datetime.datetime.now() - datetime.timedelta(days=1), "user": "Editor1", "action": "Adăugare", "details": "Produs ID: 101 adăugat", "ip": "192.168.1.2"},
        {"id": 4, "timestamp": datetime.datetime.now() - datetime.timedelta(days=1, hours=2), "user": "Editor1", "action": "Descărcare", "details": "Document ID: 45 descărcat", "ip": "192.168.1.2"},
        {"id": 5, "timestamp": datetime.datetime.now() - datetime.timedelta(days=2), "user": "Vizualizator1", "action": "Export", "details": "Raport stoc exportat", "ip": "192.168.1.3"},
        {"id": 6, "timestamp": datetime.datetime.now() - datetime.timedelta(days=3), "user": "Admin", "action": "Ștergere", "details": "Document ID: 22 șters", "ip": "192.168.1.1"},
        {"id": 7, "timestamp": datetime.datetime.now() - datetime.timedelta(days=4), "user": "Editor2", "action": "Autentificare", "details": "Autentificare eșuată", "ip": "192.168.1.4"},
        {"id": 8, "timestamp": datetime.datetime.now() - datetime.timedelta(days=4, hours=1), "user": "Editor2", "action": "Autentificare", "details": "Autentificare reușită", "ip": "192.168.1.4"},
    ]
    
    # Aplicăm filtrele
    filtered_logs = audit_logs
    if user_filter != "Toți":
        filtered_logs = [log for log in filtered_logs if log['user'] == user_filter]
    if action_filter != "Toate":
        filtered_logs = [log for log in filtered_logs if log['action'] == action_filter]
    
    # Filtru de dată
    start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
    end_datetime = datetime.datetime.combine(end_date, datetime.time.max)
    filtered_logs = [log for log in filtered_logs if start_datetime <= log['timestamp'] <= end_datetime]
    
    # Afișare rezultate
    if not filtered_logs:
        st.info("Nu există înregistrări care să corespundă criteriilor de filtrare.")
    else:
        logs_table = []
        for log in filtered_logs:
            logs_table.append({
                "ID": log['id'],
                "Dată și Oră": log['timestamp'].strftime('%d.%m.%Y %H:%M'),
                "Utilizator": log['user'],
                "Acțiune": log['action'],
                "Detalii": log['details'],
                "IP": log['ip']
            })
        
        st.dataframe(pd.DataFrame(logs_table))
        
        # Export opțiuni
        if st.button("Exportă Jurnal"):
            st.success("Jurnalul a fost exportat!")
            st.download_button(
                label="Descarcă CSV",
                data=pd.DataFrame(logs_table).to_csv(index=False).encode('utf-8'),
                file_name=f"jurnal_activitate_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )