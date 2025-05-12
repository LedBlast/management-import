import streamlit as st
import pandas as pd
import database as db
from PIL import Image
import os
import base64
import io

# Configurare pagină
st.set_page_config(page_title='Produse - LED/LCD Import Management', layout='wide')

# Directorul pentru imagini produse
PRODUCT_IMAGES_DIR = "product_images"
if not os.path.exists(PRODUCT_IMAGES_DIR):
    os.makedirs(PRODUCT_IMAGES_DIR)

# Header
st.title('Gestiune Produse')
st.markdown('Vizualizare și management produse LED/LCD importate.')

# Funcția pentru afișarea imaginilor miniatură și mărirea lor în modal
def get_image_with_zoom(image_path, image_name, size=(50, 50)):
    # Verificăm dacă fișierul există
    if not os.path.exists(image_path):
        # Imagine placeholder pentru produsele fără imagine
        placeholder_img = Image.new('RGB', size, color='lightgray')
        img_byte_arr = io.BytesIO()
        placeholder_img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
    else:
        # Deschidem imaginea și redimensionăm la dimensiunea thumbnail
        img = Image.open(image_path)
        img.thumbnail(size)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
    
    # Convertim imaginea în base64 pentru afișare în HTML
    img_b64 = base64.b64encode(img_byte_arr).decode()
    
    # Generăm un ID unic pentru modal pentru a evita conflictele
    import uuid
    unique_id = str(uuid.uuid4()).replace('-', '')
    
    # Cream HTML-ul care include imaginea miniatură și modalul pentru zoom
    # Eliminăm caracterele newline și spațiile nedorite
    # Am eliminat evenimentele React care generau erori (onmouseover, onmouseout, onclick)
    html = f"""<style>.thumbnail{{width:{size[0]}px;height:{size[1]}px;object-fit:cover;cursor:pointer;}}.modal{{display:none;position:fixed;z-index:1000;left:0;top:0;width:100%;height:100%;overflow:auto;background-color:rgba(0,0,0,0.7);}}.modal-content{{margin:5% auto;display:block;max-width:500px;max-height:500px;}}.close{{position:absolute;top:15px;right:35px;color:white;font-size:40px;font-weight:bold;cursor:pointer;}}.zoom-icon{{position:absolute;background-color:rgba(255,255,255,0.7);border-radius:50%;padding:2px;width:20px;height:20px;display:flex;align-items:center;justify-content:center;cursor:pointer;margin-left:35px;margin-top:-15px;}}</style><div style="position:relative;display:inline-block;"><img src="data:image/png;base64,{img_b64}" class="thumbnail" alt="{image_name}" style="cursor:pointer;"><div class="zoom-icon"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="11" y1="8" x2="11" y2="14"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg></div></div><div id="modal-{unique_id}" class="modal"><span class="close" style="cursor:pointer;">&times;</span><img class="modal-content" src="data:image/png;base64,{img_b64}"></div><script>document.addEventListener('DOMContentLoaded',function(){{const thumbnail=document.querySelectorAll('.thumbnail');const modal=document.getElementById('modal-{unique_id}');const closeBtn=document.querySelectorAll('.close');thumbnail.forEach(img=>{{img.addEventListener('mouseover',function(){{this.style.opacity=0.8;}});img.addEventListener('mouseout',function(){{this.style.opacity=1;}})}});thumbnail.forEach(img=>{{img.addEventListener('click',function(){{modal.style.display='block';}});}});closeBtn.forEach(btn=>{{btn.addEventListener('click',function(){{modal.style.display='none';}});}});window.addEventListener('click',function(event){{if(event.target==modal){{modal.style.display='none';}}}});}});</script>"""
    return html

# Obține lista de produse
products = db.get_products()

# Tab-uri pentru diferite operațiuni
tabs = st.tabs(["Catalog Produse", "Adăugare Produs", "Alerte Stoc"])

with tabs[0]:
    st.header('Catalog Produse')
    
    # Filtre pentru produse
    col1, col2, col3 = st.columns(3)
    with col1:
        search_term = st.text_input("Caută produs", placeholder="SKU sau nume")
    with col2:
        # Obține categoriile unice
        categories = list(set([p['category'] for p in products if p['category']]))
        selected_category = st.selectbox("Filtru Categorie", options=["Toate"] + categories)
    with col3:
        show_low_stock = st.checkbox("Arată doar stoc scăzut")
    
    # Filtrare produse
    filtered_products = products
    if search_term:
        filtered_products = [p for p in filtered_products if search_term.lower() in p['name'].lower() or search_term.lower() in p['sku'].lower()]
    if selected_category and selected_category != "Toate":
        filtered_products = [p for p in filtered_products if p['category'] == selected_category]
    if show_low_stock:
        filtered_products = [p for p in filtered_products if p['stock_quantity'] <= p['stock_alert_threshold']]
    
    if not filtered_products:
        st.info('Nu există produse care să corespundă criteriilor de filtrare.')
    else:
        # Pregătim datele pentru tabel
        table_data = []
        for product in filtered_products:
            # Obținem calea imaginii
            image_path = product.get('image_path', '')
            if not image_path or not os.path.exists(image_path):
                image_path = os.path.join(PRODUCT_IMAGES_DIR, f"placeholder_{product['id']}.png")
                
            # Generăm HTML pentru imagine cu zoom
            image_html = get_image_with_zoom(image_path, f"product_{product['id']}")
            
            # Status stoc
            stock_status = "🔴 Scăzut" if product['stock_quantity'] <= product['stock_alert_threshold'] else "🟢 OK"
            
            table_data.append({
                "Imagine": image_html,
                "SKU": product['sku'],
                "Nume": product['name'],
                "Categorie": product['category'],
                "Furnizor": product['supplier_name'],
                "Stoc": f"{product['stock_quantity']} ({stock_status})",
                "Preț": f"{product['purchase_price']} Lei" if product['purchase_price'] else "N/A"
            })
        
        # Convertim la DataFrame și afișăm
        products_df = pd.DataFrame(table_data)
        st.write(products_df.to_html(escape=False, index=False), unsafe_allow_html=True)
        
        # Afișarea produselor ca carduri expandabile (alternativ)
        st.subheader("Vizualizare detaliată")
        for product in filtered_products:
            with st.expander(f"{product['name']} (SKU: {product['sku']})"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**Categorie:** {product['category']}")
                    st.markdown(f"**Furnizor:** {product['supplier_name']}")
                
                with col2:
                    st.markdown(f"**Stoc:** {product['stock_quantity']} buc")
                    stock_status = "🔴 Stoc scăzut" if product['stock_quantity'] <= product['stock_alert_threshold'] else "🟢 Stoc OK"
                    st.markdown(f"**Status:** {stock_status}")
                
                with col3:
                    st.markdown(f"**Preț achiziție:** {product['purchase_price']} Lei" if product['purchase_price'] else "**Preț achiziție:** N/A")
                    st.markdown(f"**Ultima achiziție:** {product['last_purchase_date'].strftime('%d.%m.%Y') if product['last_purchase_date'] else 'Niciodată'}")
                
                # Butoane de acțiune
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.button("Vizualizare", key=f"view_{product['id']}")
                with col2:
                    st.button("Editare", key=f"edit_{product['id']}")
                with col3:
                    st.button("Adaugă stoc", key=f"stock_{product['id']}")
                with col4:
                    st.button("Șterge", key=f"delete_{product['id']}")

with tabs[1]:
    st.header('Adăugare Produs Nou')
    
    # Obține lista de furnizori pentru dropdown
    suppliers = db.get_suppliers()
    supplier_options = {s['id']: s['name'] for s in suppliers}
    
    with st.form("add_product_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            sku = st.text_input("SKU*")
            name = st.text_input("Nume Produs*")
            category = st.selectbox("Categorie", ["LCD Panels", "LED Components", "Touch Screens", "Power Supplies", "Altele"])
            supplier_id = st.selectbox("Furnizor", options=list(supplier_options.keys()), format_func=lambda x: supplier_options.get(x, "Selectează"))
        
        with col2:
            purchase_price = st.number_input("Preț Achiziție (Lei)", min_value=0.0, step=0.1)
            stock_quantity = st.number_input("Stoc Inițial", min_value=0, step=1)
            stock_alert = st.number_input("Alertă Stoc Minim", min_value=1, value=5)
            dimensions = st.text_input("Dimensiuni")
        
        description = st.text_area("Descriere")
        technical_specs = st.text_area("Specificații Tehnice")
        
        # Adăugare imagine produs
        st.subheader("Imagine Produs")
        uploaded_image = st.file_uploader("Încarcă imagine", type=["jpg", "jpeg", "png"])
        if uploaded_image is not None:
            image = Image.open(uploaded_image)
            st.image(image, caption="Previzualizare imagine", width=300)
        
        # Buton de salvare
        submit_button = st.form_submit_button("Salvează Produs")
        
        if submit_button:
            if not sku or not name:
                st.error("SKU-ul și numele produsului sunt obligatorii!")
            else:
                # Aici ar urma logica de salvare în baza de date
                # Inclusiv salvarea imaginii dacă este încărcată
                if uploaded_image is not None:
                    # Simulăm salvarea imaginii
                    st.info("Imaginea produsului a fost salvată.")
                
                st.success(f"Produsul {name} a fost adăugat cu succes! (simulare)")

with tabs[2]:
    st.header('Alerte Stoc')
    
    # Obține produsele cu stoc scăzut
    low_stock_products = [p for p in products if p['stock_quantity'] <= p['stock_alert_threshold']]
    
    if not low_stock_products:
        st.success("Nu există produse cu stoc sub limita de alertă.")
    else:
        st.warning(f"{len(low_stock_products)} produse au stoc scăzut și necesită reaprovizionare.")
        
        # Tabel cu produsele cu stoc scăzut
        table_data = []
        for p in low_stock_products:
            table_data.append({
                "SKU": p['sku'],
                "Produs": p['name'],
                "Stoc Actual": p['stock_quantity'],
                "Limită Alertă": p['stock_alert_threshold'],
                "Furnizor": p['supplier_name']
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df)
        
        # Buton pentru generare comandă
        if st.button("Generează Comandă Reaprovizionare"):
            st.info("Comanda de reaprovizionare a fost generată și este pregătită pentru export. (simulare)")
            
            # Aici ar urma logica pentru generarea și exportul comenzii