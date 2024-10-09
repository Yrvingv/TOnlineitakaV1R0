// static/js/scripts.js

// Ejemplo: Resaltar una tarjeta de producto al hacer clic
document.addEventListener('DOMContentLoaded', () => {
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
        card.addEventListener('click', () => {
            card.classList.toggle('highlight');
        });
    });
});

function updateSubtotal(itemId, itemPrice) {
    const quantityInput = document.querySelector(`input[name="quantity_${itemId}"]`);
    const quantity = parseInt(quantityInput.value) || 0;
    const subtotalElement = document.querySelector(`#subtotal_${itemId}`);
    const subtotal = itemPrice * quantity;
    subtotalElement.textContent = `$${subtotal.toFixed(2)}`;

    updateTotal();
}

function updateTotal() {
    let total = 0;
    const subtotals = document.querySelectorAll('[id^="subtotal_"]');
    subtotals.forEach(subtotal => {
        const value = parseFloat(subtotal.textContent.replace('$', ''));
        total += value;
    });
    document.querySelector('#totalAmount').textContent = `$${total.toFixed(2)}`;
}


