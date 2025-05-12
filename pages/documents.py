import streamlit as st
import pandas as pd
import database as db
import os
import base64
from datetime import datetime

# Configurare pagină
st.set_page_config(page_title='Documente - LED/LCD Import Management', layout='wide')

# Directorul pentru documente
DOCUMENTS_DIR = "uploaded_documents"
if not os.path.exists(DOCUMENTS_DIR):
    os.makedirs(DOCUMENTS_DIR)

# Header
st.title('Gestiune Documente')
st.markdown('Încărcare și management documente pentru importurile de produse LED/LCD.')

# Funcție pentru download fișiere cu iconițe
def get_binary_file_downloader_html(bin_file_path, file_label, is_admin=False):
    with open(bin_file_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    
    # Iconiță de descărcare - folosim JavaScript direct pentru a evita erorile React
    download_icon = f"""<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(bin_file_path)}" class="icon-btn download-btn" title="Descarcă fișier"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2980b9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg></a>"""
    
    # Adăugam butonul de ștergere dacă utilizatorul este admin
    delete_icon = ""
    if is_admin:
        doc_id = os.path.basename(bin_file_path).split('.')[0]  # extragem un ID pentru document
        # Folosim un anchor tag în loc de buton pentru a evita erorile React cu onClick
        # Înlocuim onclick cu JavaScript adăugat prin addEventListener pentru a preveni erorile React
        delete_icon = f"""<a href="#" class="icon-btn delete-btn" id="delete-{doc_id}" title="Șterge fișier" style="display:inline-flex;margin:0 5px;text-decoration:none;"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e74c3c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg></a><script>document.addEventListener('DOMContentLoaded',function(){{document.getElementById('delete-{doc_id}').addEventListener('click',function(e){{e.preventDefault();if(confirm('Sigur doriți să ștergeți documentul {file_label}?')){{alert('Document {file_label} șters (simulare)');}}}});}});</script>"""
    
    # Stiluri pentru butoanele noastre
    styles = """
    <style>
        .icon-btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin: 0 5px;
            padding: 5px;
            border-radius: 4px;
            transition: all 0.2s;
        }
        .download-btn:hover svg {
            stroke: #1a5276;
        }
        .delete-btn:hover svg {
            stroke: #922b21;
        }
    </style>
    """
    
    return styles + download_icon + delete_icon

# Tab-uri pentru diferite operațiuni
tabs = st.tabs(["Listă Documente", "Încărcare Document"])

with tabs[0]:
    st.header('Documente Disponibile')
    
    # Simulăm documente din baza de date (în implementarea finală, acestea vor veni din tabelul 'documents')
    documents_data = [
        {"id": 1, "title": "Factură Shenzhen Display", "file_name": "invoice_sdt_2025_1.pdf", 
         "category": "Factură", "supplier": "Shenzhen Display Tech", "upload_date": datetime(2025, 5, 1)},
        {"id": 2, "title": "Certificat CE - LCD Panels", "file_name": "ce_cert_lcd_2025.pdf", 
         "category": "Certificare", "supplier": "Shenzhen Display Tech", "upload_date": datetime(2025, 4, 15)},
        {"id": 3, "title": "Factură Guangzhou LED", "file_name": "invoice_gzled_2025_1.pdf", 
         "category": "Factură", "supplier": "Guangzhou LED Solutions", "upload_date": datetime(2025, 5, 5)},
    ]
    
    # Creăm un tabel pentru afișarea documentelor
    if documents_data:
        # Filtre pentru documente
        col1, col2 = st.columns(2)
        with col1:
            search_term = st.text_input("Caută document", placeholder="Nume sau categorie")
        with col2:
            category_options = ["Toate"] + list(set(doc["category"] for doc in documents_data))
            selected_category = st.selectbox("Filtru Categorie", options=category_options)
        
        # Filtrăm documentele
        filtered_docs = documents_data
        if search_term:
            filtered_docs = [d for d in filtered_docs if search_term.lower() in d['title'].lower() or 
                            search_term.lower() in d['file_name'].lower()]
        if selected_category and selected_category != "Toate":
            filtered_docs = [d for d in filtered_docs if d['category'] == selected_category]
        
        # Afișăm documentele ca tabel cu opțiuni de download
        if not filtered_docs:
            st.info("Nu există documente care să corespundă criteriilor de filtrare.")
        else:
            # Pregătim datele pentru tabel
            docs_for_display = []
            for doc in filtered_docs:
                # Simulăm că avem fișierul (în implementarea reală, verificăm dacă fișierul există)
                file_path = os.path.join(DOCUMENTS_DIR, doc['file_name'])
                # Verificăm dacă fișierul există pe disc
                if not os.path.exists(file_path):
                    # Pentru demo, creăm un fișier text gol cu acest nume
                    with open(file_path, 'w') as f:
                        f.write(f"Demo file for {doc['title']}")
                
                # Verificăm dacă utilizatorul este admin
                is_admin = False
                if 'user' in st.session_state and st.session_state.user:
                    is_admin = st.session_state.user.get('role') == 'Admin'
                
                # Adăugăm în lista pentru afișare
                doc_with_action = {
                    "Titlu": doc['title'],
                    "Categorie": doc['category'],
                    "Furnizor": doc['supplier'],
                    "Data Încărcare": doc['upload_date'].strftime('%d.%m.%Y'),
                    "Fișier": doc['file_name'],
                    "Acțiuni": get_binary_file_downloader_html(file_path, "Fișier", is_admin)
                }
                docs_for_display.append(doc_with_action)
            
            # Afișăm tabelul
            docs_df = pd.DataFrame(docs_for_display)
            st.write(docs_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info('Nu există documente în baza de date.')

with tabs[1]:
    st.header('Încarcă Document Nou')
    
    # Formularul pentru încărcarea documentului
    with st.form("upload_document_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            doc_title = st.text_input("Titlu Document*")
            doc_category = st.selectbox("Categorie", ["Factură", "Certificare", "Specificații", "Declarație Vamală", "Altele"])
        
        with col2:
            # Obținem lista de furnizori din baza de date
            suppliers = db.get_suppliers()
            supplier_options = [f"{s['name']} (ID: {s['id']})" for s in suppliers]
            selected_supplier = st.selectbox("Furnizor Asociat", options=[""] + supplier_options)
            
            # Opțional, asociază cu un produs
            products = db.get_products()
            product_options = [f"{p['name']} (ID: {p['id']})" for p in products]
            selected_product = st.selectbox("Produs Asociat (opțional)", options=[""] + product_options)
        
        # Încărcare fișier
        uploaded_file = st.file_uploader("Selectează document", type=["pdf", "doc", "docx", "xls", "xlsx", "jpg", "png"])
        
        notes = st.text_area("Note Adiționale")
        
        # Buton de salvare
        submit_button = st.form_submit_button("Încarcă Document")
        
        if submit_button:
            if not doc_title or not uploaded_file:
                st.error("Titlul documentului și fișierul sunt obligatorii!")
            else:
                # Salvăm fișierul
                file_path = os.path.join(DOCUMENTS_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Afișăm confirmarea
                st.success(f"Documentul '{doc_title}' a fost încărcat cu succes!")
                
                # Opțiune de descărcare directă pentru documentul tocmai încărcat
                st.markdown(get_binary_file_downloader_html(file_path, "fișierul tocmai încărcat"), unsafe_allow_html=True)