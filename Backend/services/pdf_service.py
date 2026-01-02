from reportlab.pdfgen import canvas

def generate_invoice_pdf(file_path, invoice, items):
    c = canvas.Canvas(file_path)
    c.drawString(100, 800, f"Invoice #{invoice.invoice_number}")

    y = 760
    for item in items:
        c.drawString(100, y, f"{item.description} x {item.quantity} = {item.price}")
        y -= 20

    c.save()
