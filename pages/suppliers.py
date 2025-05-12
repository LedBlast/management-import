import streamlit as st
import pandas as pd
import database as db
import os

# Configurare pagină
st.set_page_config(page_title='Furnizori - LED/LCD Import Management', layout='wide')

# Header
st.title('Gestiune Furnizori')
st.markdown('Vizualizare și management furnizori pentru importurile de produse LED/LCD.')

# Obține lista de furnizori
suppliers = db.get_suppliers()

# Tab-uri pentru diferite operațiuni
tabs = st.tabs(["Listă Furnizori", "Adăugare Furnizor", "Produse per Furnizor"])

with tabs[0]:
    st.header('Lista Furnizorilor')
    
    if not suppliers:
        st.info('Nu există furnizori în baza de date.')
    else:
        # Convertim lista de dicționare în DataFrame pentru afișare
        df = pd.DataFrame(suppliers)
        
        # Adăugăm buton de expandare pentru a vedea detalii complete
        for i, supplier in enumerate(suppliers):
            with st.expander(f"{supplier['name']} - {supplier['country']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Persoană contact:** {supplier['contact_person']}")
                    st.markdown(f"**Email:** {supplier['email']}")
                    st.markdown(f"**Telefon:** {supplier['phone']}")
                with col2:
                    st.markdown(f"**Oraș:** {supplier['city']}")
                    # Butoane de acțiune
                    st.button('Editează', key=f"edit_{supplier['id']}")
                    st.button('Șterge', key=f"delete_{supplier['id']}")

with tabs[1]:
    st.header('Adăugare Furnizor Nou')
    
    with st.form("add_supplier_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nume Furnizor*")
            contact_person = st.text_input("Persoană Contact")
            email = st.text_input("Email")
            phone = st.text_input("Telefon")
        
        with col2:
            country = st.text_input("Țară", value="China")
            city = st.text_input("Oraș")
            address = st.text_area("Adresă")
            tax_id = st.text_input("Cod Fiscal")
        
        col3, col4 = st.columns(2)
        with col3:
            ce_certification = st.checkbox("Certificare CE")
        with col4:
            rohs_certification = st.checkbox("Certificare RoHS")
        
        notes = st.text_area("Note Adiționale")
        
        # Buton de salvare
        submit_button = st.form_submit_button("Salvează Furnizor")
        
        if submit_button:
            if not name:
                st.error("Numele furnizorului este obligatoriu!")
            else:
                st.success(f"Furnizorul {name} a fost adăugat cu succes! (simulare)")
                # Aici ar urma logica de salvare în baza de date

with tabs[2]:
    st.header('Produse per Furnizor')
    
    # Dropdown pentru selectarea furnizorului
    supplier_options = [f"{s['name']} (ID: {s['id']})" for s in suppliers]
    selected_supplier = st.selectbox("Selectează Furnizor", options=[""] + supplier_options)
    
    if selected_supplier:
        # Obținem ID-ul furnizorului din string-ul selectat
        supplier_id = int(selected_supplier.split("ID: ")[1].strip(")"))
        
        # Aici ar trebui să obținem produsele pentru acest furnizor
        # Simulăm câteva produse pentru demonstrație
        st.subheader(f"Produse pentru {selected_supplier.split(' (ID')[0]}")
        
        sample_products = [
            {"sku": "LCD-1001", "name": "LCD Display 15\"", "category": "LCD Panels", "stock": 15},
            {"sku": "LCD-1002", "name": "LCD Display 17\"", "category": "LCD Panels", "stock": 8},
            {"sku": "LED-2001", "name": "LED Backlight Module", "category": "LED Components", "stock": 24}
        ]
        
        # Afișăm produsele într-un tabel
        products_df = pd.DataFrame(sample_products)
        st.dataframe(products_df)