# create_db.py
import sqlite3
import pandas as pd

def create_database():
    conn = sqlite3.connect('store.db')
    cur = conn.cursor()

    # Eliminar la tabla products si existe (para reiniciar todo)
    cur.execute('DROP TABLE IF EXISTS products')
    
    # Crear la tabla de productos con el campo ID sin autoincremento
    cur.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            condition TEXT NOT NULL,
            image_url TEXT
        )
    ''')
    
    # Leer los datos desde el archivo Excel, incluyendo la columna 'id'
    df = pd.read_excel('products.xlsx')
    
    # Insertar los datos del Excel en la tabla
    for _, row in df.iterrows():
        cur.execute('''
            INSERT INTO products (id, name, description, category, price, stock, condition, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (row['id'], row['name'], row['description'], row['category'], row['price'], row['stock'], row['condition'], row['image_url']))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("Base de datos creada y datos importados desde Excel con IDs exitosamente.")
