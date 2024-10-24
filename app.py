# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from urllib.parse import quote
from flask_mail import Mail, Message
import os
import sqlite3

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

#Ruta para finalizar la compra
@app.route('/checkout', methods=['POST'])
def checkout():
    # 1. Capturar los datos del cliente desde el formulario
    nombre_cliente = request.form['name']
    email_cliente = request.form['email']
    cart = session.get('cart', [])
    
    if not cart:
        flash("Tu carrito está vacío.", 'warning')
        return redirect(url_for('cart'))

    # 2. Crear el mensaje del correo con los productos y datos del cliente
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

    # 3. Crear el mensaje de WhatsApp con las especificaciones de la compra
    whatsapp_message = "Hola! Quiero comprar los siguientes productos:\n"
    for item in cart:
        subtotal = item['price'] * item['quantity']
        whatsapp_message += f"- {item['name']} x {item['quantity']} unidades (${item['price']} cada uno) = ${subtotal}\n"
    total = sum(item['price'] * item['quantity'] for item in cart)
    whatsapp_message += f"\nTotal: ${total}\n\n"
    whatsapp_message += "¿Cuáles son los medios de pago disponibles?"

    # Codificar el mensaje
    encoded_message = quote(whatsapp_message)

    # Número de WhatsApp del vendedor
    whatsapp_number = "+5491128390182"

    # Generar la URL para WhatsApp
    whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_message}"

    # 4. Actualizar el stock en la base de datos
    conn = get_db_connection()
    for item in cart:
        conn.execute('UPDATE products SET stock = stock - ? WHERE id = ?', (item['quantity'], item['id']))
    conn.commit()
    conn.close()

    # 5. Limpiar el carrito después de la compra
    session.pop('cart', None)

    # Redirigir a WhatsApp
    return redirect(whatsapp_url)

# Ruta para descargar el pdf del carrito (BORRADO)

# Ruta para la página de contactos
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Capturar los datos del formulario
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        # Enviar el correo al vendedor
        msg = Message("Nuevo Mensaje de Contacto", recipients=['yrving.viera@gmail.com'])
        msg.body = f"Nombre: {name}\nEmail: {email}\nMensaje: {message}"
        mail.send(msg)
        
        flash('Tu mensaje ha sido enviado. Nos pondremos en contacto contigo pronto.', 'success')
        return redirect(url_for('contact'))
    
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


# Ruta para mostrar "Mis Clientes"
@app.route('/mis_clientes')
def mis_clientes():
    videos = [
        {"cliente": "Adriana Mendez, Carolina Becerra, Nathaly Rivas", "modelo": "Sets Shorts", "instagram": "@itacasfitnesswear", "video": "V1.mp4"},
        {"cliente": "Valeria Puccia", "modelo": "Enterizo Morado", "instagram": "@valeriapuccia", "video": "V2.mp4"},
        {"cliente": "Nathaly Rivas", "modelo": "Enterizo para gym", "instagram": "@nathalyrivas", "video": "V3.mp4"},
    ]
    return render_template('mis_clientes.html', videos=videos)

# Ruta para mostrar "Mi Blog"
@app.route('/mi_blog')
def mi_blog():
    articulos = [
        {
            "titulo": "La Evolución del Fitnesswear: Moda, Comodidad y Rendimiento",
            "imagen": "articulo1.webp",
            "resumen": "El fitnesswear ha evolucionado para combinar estilo y funcionalidad, permitiendo que la ropa deportiva sea ideal tanto para entrenar como para el uso diario. La moda fitness actual se centra en ofrecer conjuntos para gimnasio que se adapten a cualquier actividad, manteniendo comodidad y rendimiento.",
            "contenido": [
                "En los últimos años, la ropa deportiva ha experimentado una gran transformación, pasando de ser simple y funcional a convertirse en un elemento clave en la moda. La tendencia hacia un estilo de vida saludable ha impulsado la creación de prendas que no solo ofrecen comodidad y rendimiento, sino que también reflejan las últimas tendencias. Los materiales de alta tecnología, como telas transpirables y elásticas, permiten que los usuarios se sientan cómodos y seguros durante su entrenamiento. Además, las marcas de ropa deportiva han ampliado sus catálogos para ofrecer una gran variedad de opciones que se adaptan a diferentes tipos de ejercicios, desde yoga hasta running, garantizando el máximo rendimiento.",
                "La moda fitness no solo está pensada para el gimnasio, sino que también ha ganado terreno en el día a día. Muchas personas prefieren usar ropa deportiva fuera de sus entrenamientos por su comodidad y versatilidad. Esta tendencia, conocida como athleisure, combina la estética del fitness con la moda casual, permitiendo que las personas se vean bien mientras se mantienen activas. Las colecciones de moda fitness incluyen colores vibrantes, diseños innovadores y estilos que hacen que las prendas sean apropiadas tanto para entrenar como para salir a la calle, dando lugar a un nuevo enfoque en el vestuario diario.",
                "Elegir el conjunto para ir al gym adecuado implica más que solo pensar en el estilo. La ropa debe ser funcional y adecuada para el tipo de entrenamiento que se va a realizar. Para ejercicios de alta intensidad, es importante elegir prendas que absorban el sudor y permitan libertad de movimiento, mientras que para actividades más relajadas, como el yoga, es mejor optar por ropa más suave y flexible. Además, un buen conjunto para gimnasio puede motivar a las personas a sentirse más seguras y listas para enfrentar cualquier desafío físico, mejorando su rendimiento y ayudando a alcanzar sus objetivos de fitness."
            ],
            "Fecha": "Fecha de publicación: 15 de septiembre de 2024"
        },
        {
            "titulo": "Cómo Elegir la Ropa Deportiva Ideal: Consejos para elegir bien",
            "imagen": "articulo2.webp",
            "resumen": "Escoger la ropa deportiva adecuada puede marcar la diferencia en tu rendimiento. Conoce cómo elegir el outfit perfecto para cada tipo de ejercicio y aumenta tu comodidad y estilo en cada entrenamiento.",
            "contenido": [
                "Cuando se trata de mejorar el rendimiento físico, seleccionar la ropa deportiva adecuada es crucial. No solo se trata de estilo, sino también de funcionalidad y comodidad. Cada tipo de actividad física tiene sus propias demandas y, por lo tanto, requiere diferentes tipos de prendas. Por ejemplo, si practicas running, necesitarás ropa ligera, que absorba el sudor rápidamente y te permita moverte con libertad. Los pantalones ajustados y camisetas de material técnico son ideales para este tipo de ejercicio, ya que reducen la fricción y ayudan a mantener la frescura.",
                "Por otro lado, para ejercicios de bajo impacto como el yoga o pilates, la flexibilidad y comodidad son esenciales. En este caso, elegir un conjunto para gimnasio con telas suaves y elásticas, que se adapten a tu cuerpo, es lo más recomendable. Las prendas ajustadas permiten moverse sin restricciones, mientras que los tejidos transpirables aseguran que te mantengas fresco durante toda la práctica. Además, optar por tops o sujetadores deportivos de soporte medio o alto te proporcionará la estabilidad que necesitas en las posturas más exigentes.",
                "Al final del día, la clave está en conocer las exigencias de tu actividad física y adaptar tu vestimenta en consecuencia. Además, las nuevas tendencias en moda fitness permiten que el fitnesswear no solo sea funcional, sino también elegante. Al elegir prendas de calidad y con características técnicas, te aseguras no solo de obtener el máximo rendimiento, sino también de verte bien mientras entrenas. Ya sea que prefieras un estilo más clásico o sigas las últimas tendencias, invertir en ropa deportiva adecuada elevará tu experiencia de entrenamiento a otro nivel." ,
            ],
            "Fecha": "Fecha de publicación: 10 de octubre de 2024"
        },
        {
            "titulo": "Los Beneficios de Invertir en Ropa Deportiva de Alta Calidad",
            "imagen": "articulo3.webp",
            "resumen": "La ropa deportiva de alta calidad puede mejorar tu rendimiento, aumentar tu comodidad y hacer que te sientas más motivado para entrenar. Aprende por qué es importante elegir fitnesswear de primera.",
            "contenido": [
                "Invertir en fitnesswear de alta calidad no es solo una cuestión de moda, sino una decisión clave que puede afectar directamente tu rendimiento y comodidad durante el entrenamiento. La ropa deportiva premium está diseñada con materiales avanzados que proporcionan una mayor transpirabilidad, mejor ajuste y mayor durabilidad en comparación con las prendas más económicas. Los tejidos de calidad, como el poliéster reciclado o las mezclas de algodón técnico, están pensados para soportar sesiones intensas de ejercicio, absorbiendo el sudor y manteniéndote seco durante más tiempo.",
                "Otra gran ventaja de optar por moda fitness duradera es la inversión a largo plazo. Aunque inicialmente el precio pueda ser más elevado, estas prendas están diseñadas para durar más tiempo, resistiendo múltiples lavados sin perder su forma, color o propiedades técnicas. Además, la comodidad que ofrecen es incomparable. Las costuras planas, las telas elásticas y los cortes ergonómicos permiten libertad de movimiento y evitan irritaciones en la piel, algo fundamental cuando entrenas con regularidad.",
                "Finalmente, no se puede subestimar el impacto psicológico de llevar un conjunto para gimnasio de alta calidad. Cuando te sientes bien con lo que llevas puesto, aumenta tu confianza y motivación para alcanzar tus objetivos de fitness. Usar ropa deportiva que se ajuste perfectamente a tu cuerpo, que te haga sentir cómodo y que además esté en línea con las últimas tendencias en moda, puede ser un factor determinante para mantener una rutina constante de ejercicio. En resumen, invertir en fitnesswear de primera calidad no solo optimiza tu rendimiento físico, sino que también mejora tu bienestar general."
            ],
            "Fecha": "Fecha de publicación: 21 de enero de 2024"
            
        }
    ]
    return render_template('mi_blog.html', articulos=articulos)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
