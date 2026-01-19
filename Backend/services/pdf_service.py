from reportlab.pdfgen import canvas

def generate_invoice_pdf(file_path, invoice, items):
    c = canvas.Canvas(file_path)
    c.drawString(100, 800, f"Invoice #{invoice.invoice_number}")
    c.drawString(100, 780, f"Customer: {invoice.customer_name}")
    c.drawString(100, 760, f"Email: {invoice.customer_email}")
    c.drawString(100, 740, f"Phone: {invoice.customer_phone}")

    y = 720
    for item in items:
        c.drawString(100, y, f"{item.description} x {item.quantity} = {item.price * item.quantity}")
        y -= 20

    c.drawString(100, y-20, f"Subtotal: {invoice.subtotal}")
    c.drawString(100, y-40, f"Tax: {invoice.tax}")
    c.drawString(100, y-60, f"Total: {invoice.total}")

    c.save()
