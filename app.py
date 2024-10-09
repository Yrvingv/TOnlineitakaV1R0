# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import pandas as pd
from urllib.parse import quote
from flask_mail import Mail, Message  # Import Flask-Mail para enviar correos
import pdfkit
from flask import session, make_response
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'isabellaV12'  # Cambia esto a una clave secreta segura

# Configuración del correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'yrving.viera@gmail.com'  # Reemplaza con tu correo
app.config['MAIL_PASSWORD'] = 'jmpn yctp qeac kdgc'  # Reemplaza con tu contraseña
app.config['MAIL_DEFAULT_SENDER'] = 'yrving.viera@gmail.com'

mail = Mail(app)  # Inicializa el servicio de correo

# Función para conectar a la base de datos
def get_db_connection():
    conn = sqlite3.connect('store.db')
    conn.row_factory = sqlite3.Row
    return conn

# Ruta para la página principal y filtrar por categoría
@app.route('/')
@app.route('/category/<category_name>')
def index(category_name=None):
    conn = get_db_connection()
    
    if category_name:
        products = conn.execute('SELECT * FROM products WHERE category = ?', (category_name,)).fetchall()
    else:
        products = conn.execute('SELECT * FROM products').fetchall()
    
    conn.close()
    return render_template('index.html', products=products, category_name=category_name)

# Ruta para agregar un producto al carrito
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    
    if product:
        # Inicializar el carrito en la sesión si no existe
        if 'cart' not in session:
            session['cart'] = []
        
        # Verificar si el producto ya está en el carrito
        cart = session['cart']
        for item in cart:
            if item['id'] == product['id']:
                if item['quantity'] < product['stock']:
                    item['quantity'] += 1
                    flash(f"Se ha incrementado la cantidad de {product['name']} en el carrito.", 'success')
                else:
                    flash(f"No hay suficiente stock para {product['name']}.", 'warning')
                break
        else:
            # Agregar el producto al carrito
            if product['stock'] > 0:
                cart.append({
                    'id': product['id'],
                    'name': product['name'],
                    'price': product['price'],
                    'quantity': 1,
                    'stock': product['stock']
                })
                flash(f"{product['name']} ha sido añadido al carrito.", 'success')
            else:
                flash(f"{product['name']} está sin stock.", 'warning')
        
        session['cart'] = cart
    else:
        flash("Producto no encontrado.", 'danger')
    
    return redirect(request.referrer or url_for('index'))

# Ruta para mostrar el carrito de compras
@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)  # Calcular el total
    return render_template('cart.html', cart=cart, total=total)  # Pasar el total a la plantilla

# Ruta para actualizar las cantidades en el carrito
@app.route('/update_cart', methods=['POST'])
def update_cart():
    cart = session.get('cart', [])
    for item in cart:
        new_quantity = int(request.form.get(f'quantity_{item["id"]}', item['quantity']))
        if new_quantity <= 0:
            cart.remove(item)
            flash(f"{item['name']} ha sido eliminado del carrito.", 'info')
        elif new_quantity <= item['stock']:
            item['quantity'] = new_quantity
            flash(f"Cantidad de {item['name']} actualizada a {new_quantity}.", 'success')
        else:
            flash(f"No hay suficiente stock para {item['name']}.", 'warning')
    session['cart'] = cart
    return redirect(url_for('cart'))

# Ruta para eliminar un producto del carrito
@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != product_id]
    session['cart'] = cart
    flash("Producto eliminado del carrito.", 'info')
    return redirect(url_for('cart'))

#al cliente new code
from flask import render_template, session, request, flash, redirect, url_for
from urllib.parse import quote

# Ruta para finalizar la compra
@app.route('/checkout', methods=['POST'])
def checkout():
    # Capturar los datos del cliente desde el formulario
    nombre_cliente = request.form['name']
    email_cliente = request.form['email']
    cart = session.get('cart', [])
    
    if not cart:
        flash("Tu carrito está vacío.", 'warning')
        return redirect(url_for('cart'))

    # Crear el mensaje del correo con los productos y datos del cliente
    email_message = f"Pedido de compra:\n\n"
    total = 0
    for item in cart:
        subtotal = item['price'] * item['quantity']
        email_message += f"- {item['name']} x {item['quantity']} unidades (${item['price']} cada uno) = ${subtotal}\n"
        total += subtotal
    email_message += f"\nTotal: ${total}\n\n"
    email_message += f"Datos del cliente:\nNombre: {nombre_cliente}\nEmail: {email_cliente}"
    
    # Enviar el correo al vendedor
    msg = Message("Nuevo Pedido de Compra", recipients=['yrving.viera@gmail.com'])
    msg.body = email_message
    mail.send(msg)

    # Redirigir a WhatsApp
    whatsapp_message = "Hola! Quiero comprar los siguientes productos:\n"
    for item in cart:
        subtotal = item['price'] * item['quantity']
        whatsapp_message += f"- {item['name']} x {item['quantity']} unidades (${item['price']} cada uno) = ${subtotal}\n"
    total = sum(item['price'] * item['quantity'] for item in cart)
    whatsapp_message += f"\nTotal: ${total}\n\n"
    whatsapp_message += "¿Cuáles son los medios de pago disponibles?"

    encoded_message = quote(whatsapp_message)
    whatsapp_number = "+5491128390182"  # Número de WhatsApp del vendedor
    whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_message}"

    # Actualizar el stock en la base de datos
    conn = get_db_connection()
    for item in cart:
        conn.execute('UPDATE products SET stock = stock - ? WHERE id = ?', (item['quantity'], item['id']))
    conn.commit()
    conn.close()

    # Limpiar el carrito después de la compra
    session.pop('cart', None)

    # Redirigir al cliente a WhatsApp en una nueva ventana y mantener la página abierta
    return f"""
        <script>
            window.open('{whatsapp_url}', '_blank');  // Abrir WhatsApp en una nueva pestaña
            window.location.href = '{url_for('cart')}';  // Mantener la página actual abierta y vaciar el carrito
        </script>
    """

# Ruta para descargar el pdf del carrito
@app.route('/download_order', methods=['GET'])
def download_order():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    
    # Obtener la fecha y hora actual
    current_date_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Renderizar la plantilla HTML
    rendered = render_template('order_pdf.html', cart=cart, total=total, current_date_time=current_date_time)
    
    # Convertir el HTML en PDF, permitiendo rutas locales
    options = {
        'enable-local-file-access': None  # Esto permite el acceso a archivos locales como imágenes o CSS
    }
    
    # Generar el PDF usando pdfkit y permitir rutas locales
    pdf = pdfkit.from_string(rendered, False, options=options)
    
    # Crear la respuesta con el PDF adjunto
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=order.pdf'
    
    return response


# Ruta para la página de contactos
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Ruta para manejar la búsqueda de productos
@app.route('/search')
def search():
    query = request.args.get('search', '')
    conn = get_db_connection()
    like_query = f"%{query}%"
    products = conn.execute('''
        SELECT * FROM products 
        WHERE name LIKE ? OR description LIKE ?
    ''', (like_query, like_query)).fetchall()
    conn.close()
    return render_template('index.html', products=products, search_query=query)


# Ruta para mostrar "Mis Compras" (Funcionalidad futura)
@app.route('/my-orders')
def my_orders():
    # Esta funcionalidad puede ser desarrollada con autenticación de usuarios
    return "Funcionalidad 'Mis Compras' en desarrollo."


if __name__ == '__main__':
    app.run(debug=True)
