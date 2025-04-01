// Main JavaScript file for SmartLogistics

document.addEventListener('DOMContentLoaded', function() {
    console.log('SmartLogistics application initialized');
    
    // Add input validation for forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Add animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.1)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';
        });
    });
    
    // Handle shipment tracking form
    const trackingForm = document.getElementById('shipment-tracking-form');
    if (trackingForm) {
        trackingForm.addEventListener('submit', function(event) {
            const shipmentId = document.getElementById('shipment_id').value;
            if (!shipmentId || isNaN(shipmentId) || shipmentId <= 0) {
                event.preventDefault();
                alert('Please enter a valid shipment ID');
            }
        });
    }
});