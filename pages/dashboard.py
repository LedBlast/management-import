import streamlit as st
import pandas as pd
import database as db
import datetime

# Configurare pagină
st.set_page_config(page_title='Dashboard - LED/LCD Import Management', layout='wide')

# Header
st.title('Dashboard Sistem')
st.markdown('Vizualizare centralizată a sistemului de gestiune importuri LED/LCD')

# Obține statisticile generale
try:
    stats = db.get_stats()
    
    # Calculează valorile pentru afișare
    suppliers_count = stats['suppliers_count']
    products_count = stats['products_count']
    stock_value = stats['stock_value']
    low_stock_count = stats['low_stock_count']
except Exception as e:
    st.error(f"Eroare la încărcarea statisticilor: {str(e)}")
    suppliers_count = 0
    products_count = 0
    stock_value = 0
    low_stock_count = 0

# Afișare carduri statistici
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="stat-card">', unsafe_allow_html=True)
    st.markdown(f'<p class="stat-value">{suppliers_count}</p>', unsafe_allow_html=True)
    st.markdown('<p class="stat-label">Furnizori</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="stat-card">', unsafe_allow_html=True)
    st.markdown(f'<p class="stat-value">{products_count}</p>', unsafe_allow_html=True)
    st.markdown('<p class="stat-label">Produse</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="stat-card">', unsafe_allow_html=True)
    st.markdown(f'<p class="stat-value">{stock_value:.2f} Lei</p>', unsafe_allow_html=True)
    st.markdown('<p class="stat-label">Valoare Stoc</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="stat-card">', unsafe_allow_html=True)
    st.markdown(f'<p class="stat-value">{low_stock_count}</p>', unsafe_allow_html=True)
    st.markdown('<p class="stat-label">Alerte Stoc</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Secțiune alertă stoc
st.subheader('Produse cu Stoc Scăzut')

try:
    stock_alerts = db.get_stock_alerts()
    
    if not stock_alerts:
        st.success("Nu există produse cu stoc sub limita de alertă.")
    else:
        st.warning(f"{len(stock_alerts)} produse au stoc scăzut și necesită reaprovizionare.")
        
        # Tabel cu cele mai urgente 5 produse cu stoc scăzut
        top_alerts = sorted(stock_alerts, key=lambda x: x['stock_quantity'])[:5]
        
        table_data = []
        for p in top_alerts:
            table_data.append({
                "SKU": p['sku'],
                "Produs": p['name'],
                "Stoc Actual": p['stock_quantity'],
                "Limită Alertă": p['stock_alert_threshold'],
                "Furnizor": p['supplier_name']
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df)
        
        if len(stock_alerts) > 5:
            st.info(f"Se afișează primele 5 produse din {len(stock_alerts)} produse cu stoc scăzut. Vezi toate alertele în secțiunea Produse.")
except Exception as e:
    st.error(f"Eroare la încărcarea alertelor de stoc: {str(e)}")

# Ultimele intrări în stoc
st.subheader('Ultimele Intrări în Stoc')

try:
    stock_entries = db.get_stock_entries()
    
    if not stock_entries:
        st.info("Nu există înregistrări de intrări în stoc.")
    else:
        # Afișăm doar ultimele 5 intrări
        recent_entries = stock_entries[:5]
        
        table_data = []
        for entry in recent_entries:
            table_data.append({
                "Data": entry['entry_date'].strftime('%d.%m.%Y') if entry['entry_date'] else 'N/A',
                "Produs": entry['product_name'],
                "Cantitate": entry['quantity'],
                "Preț Unitar": f"{entry['unit_price']:.2f} Lei",
                "Furnizor": entry['supplier_name'],
                "Factură": entry['invoice_number']
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df)
except Exception as e:
    st.error(f"Eroare la încărcarea intrărilor de stoc: {str(e)}")

# Grafic furnizori principali
st.subheader('Distribuția Produselor pe Furnizori')

try:
    # Calculăm numărul de produse per furnizor
    supplier_products = {}
    for product in db.get_products():
        supplier_name = product['supplier_name']
        if supplier_name:
            if supplier_name in supplier_products:
                supplier_products[supplier_name] += 1
            else:
                supplier_products[supplier_name] = 1
    
    if supplier_products:
        supplier_data = pd.DataFrame({
            'Furnizor': list(supplier_products.keys()),
            'Număr Produse': list(supplier_products.values())
        })
        
        st.bar_chart(supplier_data.set_index('Furnizor'))
    else:
        st.info("Nu există date pentru a genera graficul.")
except Exception as e:
    st.error(f"Eroare la generarea graficului: {str(e)}")

# Activitate recentă
st.subheader('Activitate Recentă')

recent_activities = [
    {"timp": "Acum 2 ore", "tip": "Produs adăugat", "detalii": "LCD Display 24\" adăugat în sistem"},
    {"timp": "Acum 5 ore", "tip": "Stoc actualizat", "detalii": "10 unități adăugate la LCD Display 17\""},
    {"timp": "Ieri, 15:30", "tip": "Furnizor adăugat", "detalii": "Furnizorul Beijing Tech Electronics adăugat în sistem"},
    {"timp": "Ieri, 10:15", "tip": "Document încărcat", "detalii": "Factură pentru comandă Shenzhen Display Tech"},
    {"timp": "2 zile în urmă", "tip": "Alertă stoc", "detalii": "Nivel scăzut de stoc pentru LED Panel 32\""}
]

for activity in recent_activities:
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"**{activity['timp']}**")
    with col2:
        st.markdown(f"**{activity['tip']}**: {activity['detalii']}")
    st.markdown("---")

# Data actualizării
st.caption(f"Date actualizate la: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}")