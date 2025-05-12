import os
import psycopg2
import datetime
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Obține detaliile de conexiune din variabilele de mediu
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_connection():
    """Creează și returnează o conexiune la baza de date."""
    return psycopg2.connect(DATABASE_URL)

def create_tables():
    """Creează tabelele necesare în baza de date."""
    
    conn = get_connection()
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Tabelul utilizatori
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(20) NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )
    ''')
    
    # Tabelul furnizori
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS suppliers (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        contact_person VARCHAR(100),
        email VARCHAR(100),
        phone VARCHAR(20),
        country VARCHAR(50) DEFAULT 'China',
        city VARCHAR(50),
        address TEXT,
        postal_code VARCHAR(20),
        tax_id VARCHAR(50),
        ce_certification BOOLEAN DEFAULT FALSE,
        rohs_certification BOOLEAN DEFAULT FALSE,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabelul produse
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        sku VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        category VARCHAR(50),
        supplier_id INTEGER REFERENCES suppliers(id),
        purchase_price DECIMAL(10, 2),
        stock_quantity INTEGER DEFAULT 0,
        stock_alert_threshold INTEGER DEFAULT 5,
        image_path VARCHAR(255),
        dimensions VARCHAR(50),
        weight DECIMAL(8, 2),
        technical_specs TEXT,
        last_purchase_date TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabelul intrări stoc
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_entries (
        id SERIAL PRIMARY KEY,
        product_id INTEGER REFERENCES products(id),
        quantity INTEGER NOT NULL,
        unit_price DECIMAL(10, 2) NOT NULL,
        supplier_id INTEGER REFERENCES suppliers(id),
        entry_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        invoice_number VARCHAR(50),
        notes TEXT
    )
    ''')
    
    # Tabelul documente
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        title VARCHAR(100) NOT NULL,
        file_name VARCHAR(255) NOT NULL,
        file_path VARCHAR(255) NOT NULL,
        file_size INTEGER NOT NULL,
        category VARCHAR(50) NOT NULL,
        supplier_id INTEGER REFERENCES suppliers(id),
        product_id INTEGER REFERENCES products(id),
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        uploaded_by INTEGER REFERENCES users(id)
    )
    ''')
    
    # Tabelul jurnal audit
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_log (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        action_type VARCHAR(50) NOT NULL,
        table_name VARCHAR(50) NOT NULL,
        record_id INTEGER,
        action_details TEXT,
        ip_address VARCHAR(50),
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.close()
    conn.close()

def insert_sample_data():
    """Inserează date demonstrative în tabele."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Inserare utilizator admin
    cursor.execute('''
    INSERT INTO users (username, email, password_hash, role) 
    VALUES ('admin', 'admin@example.com', '$2y$10$AbC123XyZ456DefGhI789O1234567890123456789012345678901234', 'Admin')
    ON CONFLICT (username) DO NOTHING
    ''')
    
    # Inserare furnizori
    cursor.execute('''
    INSERT INTO suppliers (name, contact_person, email, phone, country, city, ce_certification, rohs_certification) 
    VALUES 
    ('Shenzhen Display Tech', 'Li Wei', 'contact@szdisplay.com', '+86 12345678', 'China', 'Shenzhen', TRUE, TRUE),
    ('Guangzhou LED Solutions', 'Zhang Min', 'info@gzled.cn', '+86 87654321', 'China', 'Guangzhou', TRUE, FALSE),
    ('Hong Kong Electronics Ltd', 'John Chen', 'sales@hkel.hk', '+852 23456789', 'Hong Kong', 'Kowloon', TRUE, TRUE)
    ON CONFLICT DO NOTHING
    ''')
    
    # Obține ID-urile furnizorilor
    cursor.execute("SELECT id FROM suppliers LIMIT 3")
    supplier_ids = [row[0] for row in cursor.fetchall()]
    
    if supplier_ids:
        # Inserare produse
        for i, supplier_id in enumerate(supplier_ids):
            cursor.execute('''
            INSERT INTO products (sku, name, description, category, supplier_id, purchase_price, stock_quantity, stock_alert_threshold, image_path) 
            VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (sku) DO NOTHING
            ''', [
                f'LCD-{1000+i}', 
                f'LCD Display {15+i}"', 
                f'High quality LCD display, {15+i} inch, HD resolution', 
                'LCD Panels', 
                supplier_id, 
                100.00 + (i * 50), 
                10 + i, 
                5,
                f'product_images/lcd_{15+i}_inch.jpg'  # Cale pentru imaginea produsului
            ])
        
        # Verifică dacă produsele au fost inserate
        cursor.execute("SELECT id FROM products LIMIT 3")
        product_ids = [row[0] for row in cursor.fetchall()]
        
        if product_ids and supplier_ids:
            # Inserare intrări stoc
            for i, product_id in enumerate(product_ids):
                cursor.execute('''
                INSERT INTO stock_entries (product_id, quantity, unit_price, supplier_id, invoice_number) 
                VALUES (%s, %s, %s, %s, %s)
                ''', [
                    product_id, 
                    10 + i, 
                    95.00 + (i * 45), 
                    supplier_ids[i % len(supplier_ids)],
                    f'INV-2025-{1000+i}'
                ])
            
            # Inserare documente
            for i, supplier_id in enumerate(supplier_ids):
                cursor.execute('''
                INSERT INTO documents (title, file_name, file_path, file_size, category, supplier_id, upload_date, uploaded_by)
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, 1)
                ''', [
                    f'Factură {i+1}',
                    f'invoice_{i+1}.pdf',
                    f'uploaded_documents/invoice_{i+1}.pdf',
                    1024 * (i+1),  # Simulăm dimensiunea fișierului
                    'Factură',
                    supplier_id
                ])
                
                if i < len(product_ids):
                    cursor.execute('''
                    INSERT INTO documents (title, file_name, file_path, file_size, category, product_id, upload_date, uploaded_by)
                    VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, 1)
                    ''', [
                        f'Specificații Tehnice Produs {i+1}',
                        f'specs_{i+1}.pdf',
                        f'uploaded_documents/specs_{i+1}.pdf',
                        512 * (i+1),  # Simulăm dimensiunea fișierului
                        'Specificații',
                        product_ids[i]
                    ])
    
    conn.commit()
    cursor.close()
    conn.close()

def save_product_image(product_id, file_data, file_name):
    """Salvează imaginea produsului pe disc și actualizează calea în baza de date."""
    # Creăm directorul pentru imagini produse dacă nu există
    image_dir = "product_images"
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    
    # Generăm un nume de fișier unic bazat pe ID-ul produsului și numele original
    file_extension = os.path.splitext(file_name)[1]
    new_file_name = f"product_{product_id}{file_extension}"
    file_path = os.path.join(image_dir, new_file_name)
    
    # Salvăm fișierul pe disc
    with open(file_path, "wb") as f:
        f.write(file_data)
    
    # Actualizăm calea imaginii în baza de date
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET image_path = %s WHERE id = %s", [file_path, product_id])
    conn.commit()
    cursor.close()
    conn.close()
    
    return file_path

def save_document(title, file_name, file_data, category, supplier_id=None, product_id=None, notes=None, user_id=1):
    """Salvează un document în baza de date și pe disc."""
    # Creăm directorul pentru documente dacă nu există
    doc_dir = "uploaded_documents"
    if not os.path.exists(doc_dir):
        os.makedirs(doc_dir)
    
    # Generăm un nume de fișier unic pentru a evita suprascrierea
    file_extension = os.path.splitext(file_name)[1]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    new_file_name = f"{timestamp}_{file_name}"
    file_path = os.path.join(doc_dir, new_file_name)
    
    # Salvăm fișierul pe disc
    with open(file_path, "wb") as f:
        f.write(file_data)
    
    # Obținem dimensiunea fișierului
    file_size = os.path.getsize(file_path)
    
    # Inserăm înregistrarea în baza de date
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO documents (title, file_name, file_path, file_size, category, 
                                supplier_id, product_id, upload_date, uploaded_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s)
            RETURNING id
        """, [title, new_file_name, file_path, file_size, category, supplier_id, product_id, user_id])
        
        result = cursor.fetchone()
        document_id = result[0] if result else None
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"id": document_id, "file_path": file_path}
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        print(f"Eroare la salvarea documentului: {str(e)}")
        return None

def get_documents(supplier_id=None, product_id=None, category=None, limit=None):
    """Returnează lista de documente cu filtrare opțională."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT id, title, file_name, file_path, file_size, category, supplier_id, product_id, upload_date, uploaded_by FROM documents WHERE 1=1"
    params = []
    
    if supplier_id:
        query += " AND supplier_id = %s"
        params.append(supplier_id)
    
    if product_id:
        query += " AND product_id = %s"
        params.append(product_id)
    
    if category:
        query += " AND category = %s"
        params.append(category)
    
    query += " ORDER BY upload_date DESC"
    
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    documents = []
    for row in results:
        documents.append({
            'id': row[0],
            'title': row[1],
            'file_name': row[2],
            'file_path': row[3],
            'file_size': row[4],
            'category': row[5],
            'supplier_id': row[6],
            'product_id': row[7],
            'upload_date': row[8],
            'uploaded_by': row[9]
        })
    
    return documents

def get_user_by_email(email):
    """Caută un utilizator după adresa de email."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, email, password_hash, role FROM users WHERE email = %s", [email])
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if result:
        return {
            'id': result[0],
            'username': result[1],
            'email': result[2],
            'password_hash': result[3],
            'role': result[4]
        }
    return None

def verify_user_credentials(username, password_hash):
    """Verifică credențialele utilizatorului."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificăm atât după username cât și după email
    cursor.execute("SELECT id, username, email, password_hash, role FROM users WHERE username = %s OR email = %s", [username, username])
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if result and result[3] == password_hash:
        return {
            'id': result[0],
            'username': result[1],
            'email': result[2],
            'password_hash': result[3],
            'role': result[4]
        }
    return None

def save_user(username, email, password_hash, role='Vizualizator'):
    """Adaugă sau actualizează un utilizator în baza de date."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Verificăm dacă utilizatorul există deja
        cursor.execute("SELECT id FROM users WHERE email = %s", [email])
        result = cursor.fetchone()
        
        if result:
            # Actualizăm utilizatorul existent
            user_id = result[0]
            cursor.execute("""
                UPDATE users 
                SET username = %s, password_hash = %s, role = %s
                WHERE id = %s
            """, [username, password_hash, role, user_id])
        else:
            # Adăugăm un utilizator nou
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, is_active, created_at)
                VALUES (%s, %s, %s, %s, TRUE, CURRENT_TIMESTAMP)
                RETURNING id
            """, [username, email, password_hash, role])
            
            result = cursor.fetchone()
            user_id = result[0] if result else None
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return user_id
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        print(f"Eroare la salvarea utilizatorului: {str(e)}")
        return None

def log_user_activity(user_id, action_type, table_name, record_id=None, action_details=None, ip_address=None):
    """Înregistrează o acțiune a utilizatorului în jurnalul de audit."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO audit_log (user_id, action_type, table_name, record_id, action_details, ip_address, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """, [user_id, action_type, table_name, record_id, action_details, ip_address])
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        print(f"Eroare la înregistrarea acțiunii: {str(e)}")
        return False

def get_suppliers():
    """Returnează lista de furnizori."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, contact_person, email, phone, country, city FROM suppliers ORDER BY name")
    suppliers = cursor.fetchall()
    cursor.close()
    conn.close()
    
    result = []
    for supplier in suppliers:
        result.append({
            'id': supplier[0],
            'name': supplier[1],
            'contact_person': supplier[2] or '',
            'email': supplier[3] or '',
            'phone': supplier[4] or '',
            'country': supplier[5] or '',
            'city': supplier[6] or ''
        })
    
    return result

def get_products():
    """Returnează lista de produse cu informații despre furnizor."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            p.id, p.sku, p.name, p.category, p.purchase_price, p.stock_quantity, 
            p.stock_alert_threshold, p.last_purchase_date, 
            s.id as supplier_id, s.name as supplier_name
        FROM 
            products p
        LEFT JOIN 
            suppliers s ON p.supplier_id = s.id
        ORDER BY 
            p.name
    """)
    
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    
    result = []
    for product in products:
        result.append({
            'id': product[0],
            'sku': product[1],
            'name': product[2],
            'category': product[3] or '',
            'purchase_price': float(product[4]) if product[4] else None,
            'stock_quantity': product[5] or 0,
            'stock_alert_threshold': product[6] or 5,
            'last_purchase_date': product[7],
            'supplier_id': product[8],
            'supplier_name': product[9] or ''
        })
    
    return result

def get_stock_entries():
    """Returnează toate intrările de stoc cu informații despre produs și furnizor."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            se.id, se.quantity, se.unit_price, se.entry_date, se.invoice_number,
            p.id as product_id, p.name as product_name, p.sku,
            s.id as supplier_id, s.name as supplier_name
        FROM 
            stock_entries se
        JOIN 
            products p ON se.product_id = p.id
        JOIN 
            suppliers s ON se.supplier_id = s.id
        ORDER BY 
            se.entry_date DESC
    """)
    
    entries = cursor.fetchall()
    cursor.close()
    conn.close()
    
    result = []
    for entry in entries:
        result.append({
            'id': entry[0],
            'quantity': entry[1],
            'unit_price': float(entry[2]) if entry[2] else 0.0,
            'entry_date': entry[3],
            'invoice_number': entry[4] or '',
            'product_id': entry[5],
            'product_name': entry[6],
            'sku': entry[7],
            'supplier_id': entry[8],
            'supplier_name': entry[9]
        })
    
    return result

def get_stock_alerts():
    """Returnează produsele cu stoc sub pragul de alertă."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            p.id, p.sku, p.name, p.stock_quantity, p.stock_alert_threshold,
            s.name as supplier_name
        FROM 
            products p
        LEFT JOIN 
            suppliers s ON p.supplier_id = s.id
        WHERE 
            p.stock_quantity <= p.stock_alert_threshold
        ORDER BY 
            p.stock_quantity
    """)
    
    alerts = cursor.fetchall()
    cursor.close()
    conn.close()
    
    result = []
    for alert in alerts:
        result.append({
            'id': alert[0],
            'sku': alert[1],
            'name': alert[2],
            'stock_quantity': alert[3],
            'stock_alert_threshold': alert[4],
            'supplier_name': alert[5] or ''
        })
    
    return result

def get_stats():
    """Returnează statistici generale despre sistem."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Număr furnizori
        cursor.execute("SELECT COUNT(*) FROM suppliers")
        suppliers_count_result = cursor.fetchone()
        suppliers_count = suppliers_count_result[0] if suppliers_count_result else 0
        
        # Număr produse
        cursor.execute("SELECT COUNT(*) FROM products")
        products_count_result = cursor.fetchone()
        products_count = products_count_result[0] if products_count_result else 0
        
        # Total valoare stoc
        cursor.execute("SELECT SUM(stock_quantity * purchase_price) FROM products WHERE purchase_price IS NOT NULL")
        stock_value_result = cursor.fetchone()
        stock_value = stock_value_result[0] if stock_value_result and stock_value_result[0] else 0
        
        # Produse cu stoc scăzut
        cursor.execute("SELECT COUNT(*) FROM products WHERE stock_quantity <= stock_alert_threshold")
        low_stock_count_result = cursor.fetchone()
        low_stock_count = low_stock_count_result[0] if low_stock_count_result else 0
        
        # Număr utilizatori
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count_result = cursor.fetchone()
        users_count = users_count_result[0] if users_count_result else 0
        
        # Număr documente
        cursor.execute("SELECT COUNT(*) FROM documents")
        documents_count_result = cursor.fetchone()
        documents_count = documents_count_result[0] if documents_count_result else 0
        
        cursor.close()
        conn.close()
        
        return {
            'suppliers_count': suppliers_count,
            'products_count': products_count,
            'stock_value': float(stock_value),
            'low_stock_count': low_stock_count,
            'users_count': users_count,
            'documents_count': documents_count
        }
    except Exception as e:
        print(f"Eroare în get_stats: {str(e)}")
        return {
            'suppliers_count': 0,
            'products_count': 0,
            'stock_value': 0.0,
            'low_stock_count': 0,
            'users_count': 0,
            'documents_count': 0
        }

# Inițializare bază de date
if __name__ == '__main__':
    create_tables()
    insert_sample_data()