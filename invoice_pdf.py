
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime


def generate_invoice(business, customer, items, grand_total):

    filename = f"Invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    pdf = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Professional color palette
    navy = colors.HexColor("#142D4E")
    blue = colors.HexColor("#2878D0")
    light_blue = colors.HexColor("#EEF5FC")
    dark = colors.HexColor("#263445")
    grey = colors.HexColor("#718096")
    border = colors.HexColor("#DCE5EF")
    white = colors.white

    def draw_header(page_number):

        # Header background
        pdf.setFillColor(navy)
        pdf.rect(0, height - 125, width, 125, fill=1, stroke=0)

        # Decorative blue strip
        pdf.setFillColor(blue)
        pdf.rect(0, height - 130, width, 5, fill=1, stroke=0)

        # Brand
        pdf.setFillColor(white)
        pdf.setFont("Helvetica-Bold", 25)
        pdf.drawString(40, height - 52, "SMARTBIZ")

        pdf.setFont("Helvetica", 9)
        pdf.drawString(42, height - 70, "BUSINESS BILLING SOLUTIONS")

        # Invoice title
        pdf.setFont("Helvetica-Bold", 23)
        pdf.drawRightString(width - 40, height - 50, "INVOICE")

        pdf.setFont("Helvetica", 9)
        pdf.drawRightString(
            width - 40, height - 70,
            "ORIGINAL FOR RECIPIENT"
        )

        # Date
        pdf.setFillColor(dark)
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawRightString(width - 40, height - 155, "INVOICE DATE")

        pdf.setFont("Helvetica", 10)
        pdf.drawRightString(
            width - 40, height - 172,
            datetime.now().strftime("%d %B %Y")
        )

        # Page number
        pdf.setFillColor(grey)
        pdf.setFont("Helvetica", 8)
        pdf.drawRightString(width - 40, 20, f"Page {page_number}")

    def draw_footer():

        pdf.setStrokeColor(border)
        pdf.line(40, 48, width - 40, 48)

        pdf.setFillColor(grey)
        pdf.setFont("Helvetica", 9)
        pdf.drawCentredString(
            width / 2, 32,
            "Thank you for choosing our business!"
        )

        pdf.setFont("Helvetica", 8)
        pdf.drawCentredString(
            width / 2, 19,
            "Generated with SmartBiz"
        )

    # First page
    page_number = 1
    draw_header(page_number)

    # Business and customer information cards
    card_y = height - 325
    card_height = 115
    card_width = (width - 100) / 2

    # Extract business information
    business_name = business[0]
    owner_name = business[1]
    business_phone = business[2]
    business_email = business[3]
    business_address = business[4]
    business_gstin = business[5]

    # Business card
    pdf.setFillColor(light_blue)
    pdf.roundRect(
        40, card_y, card_width, card_height,
        8, fill=1, stroke=0
    )

    pdf.setFillColor(blue)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(53, card_y + 94, "FROM")

    pdf.setFillColor(dark)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(53, card_y + 73, str(business_name)[:35])

    pdf.setFillColor(grey)
    pdf.setFont("Helvetica", 8)

    pdf.drawString(53, card_y + 55, f"Owner: {str(owner_name or 'N/A')[:30]}")
    pdf.drawString(53, card_y + 40, f"Phone: {str(business_phone or 'N/A')[:30]}")
    pdf.drawString(53, card_y + 25, f"Email: {str(business_email or 'N/A')[:30]}")
    pdf.drawString(53, card_y + 10, f"GSTIN: {str(business_gstin or 'N/A')[:30]}")

    # Customer card
    customer_x = 60 + card_width

    pdf.setFillColor(light_blue)
    pdf.roundRect(
        customer_x, card_y, card_width, card_height,
        8, fill=1, stroke=0
    )

    pdf.setFillColor(blue)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(customer_x + 13, card_y + 94, "BILL TO")

    pdf.setFillColor(dark)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(
        customer_x + 13, card_y + 73,
        str(customer[2])[:35]
    )

    pdf.setFillColor(grey)
    pdf.setFont("Helvetica", 8)

    pdf.drawString(customer_x + 13, card_y + 55, f"Phone: {str(customer[3] or 'N/A')[:30]}")
    pdf.drawString(customer_x + 13, card_y + 40, f"Email: {str(customer[4] or 'N/A')[:30]}")
    pdf.drawString(customer_x + 13, card_y + 25, f"Address: {str(customer[5] or 'N/A')[:30]}")
    pdf.drawString(customer_x + 13, card_y + 10, f"GSTIN: {str(customer[6] or 'N/A')[:30]}")

    # Section heading
    table_top = card_y - 42

    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(40, table_top, "INVOICE SUMMARY")

    pdf.setFillColor(grey)
    pdf.setFont("Helvetica", 8)
    pdf.drawRightString(width - 40, table_top, f"{len(items)} item(s)")

    # Table heading
    table_y = table_top - 30

    pdf.setFillColor(navy)
    pdf.roundRect(
        40, table_y - 12, width - 80, 30,
        5, fill=1, stroke=0
    )

    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 8)

    pdf.drawString(49, table_y - 2, "PRODUCT")
    pdf.drawCentredString(235, table_y - 2, "QTY")
    pdf.drawRightString(315, table_y - 2, "PRICE")
    pdf.drawRightString(390, table_y - 2, "GST")
    pdf.drawRightString(490, table_y - 2, "TOTAL")

    # Product rows
    row_y = table_y - 35
    pdf.setFont("Helvetica", 9)

    for index, item in enumerate(items):

        if row_y < 125:

            draw_footer()
            pdf.showPage()

            page_number += 1
            draw_header(page_number)

            row_y = height - 175

            pdf.setFillColor(navy)
            pdf.setFont("Helvetica-Bold", 8)

            pdf.drawString(49, row_y, "PRODUCT")
            pdf.drawCentredString(235, row_y, "QTY")
            pdf.drawRightString(315, row_y, "PRICE")
            pdf.drawRightString(390, row_y, "GST")
            pdf.drawRightString(490, row_y, "TOTAL")

            row_y -= 25
            pdf.setFont("Helvetica", 9)

        # Alternating row backgrounds
        if index % 2 == 0:
            pdf.setFillColor(light_blue)
            pdf.rect(
                40, row_y - 10, width - 80, 27,
                fill=1, stroke=0
            )

        name = str(item["product_name"])[:27]
        quantity = item["quantity"]

        price = item["unit_price_paise"] / 100
        tax = item["tax_paise"] / 100
        total = item["total_paise"] / 100

        pdf.setFillColor(dark)
        pdf.drawString(49, row_y, name)

        pdf.drawCentredString(235, row_y, str(quantity))
        pdf.drawRightString(315, row_y, f"{price:.2f}")
        pdf.drawRightString(390, row_y, f"{tax:.2f}")

        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawRightString(490, row_y, f"{total:.2f}")

        pdf.setFont("Helvetica", 9)
        row_y -= 30

    # Total section
    total_y = row_y - 35

    if total_y < 100:
        draw_footer()
        pdf.showPage()

        page_number += 1
        draw_header(page_number)
        total_y = height - 180

    # Total card
    pdf.setFillColor(navy)
    pdf.roundRect(
        275, total_y - 20, 215, 65,
        8, fill=1, stroke=0
    )

    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(292, total_y + 20, "GRAND TOTAL")

    pdf.setFont("Helvetica-Bold", 19)
    pdf.drawRightString(
        475, total_y - 3,
        f"Rs. {grand_total / 100:,.2f}"
    )

    # Thank you message
    pdf.setFillColor(blue)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, total_y - 75, "Thank you for your purchase!")

    pdf.setFillColor(grey)
    pdf.setFont("Helvetica", 9)
    pdf.drawString(40, total_y - 92, "We appreciate your business.")

    draw_footer()

    pdf.save()

    return filename
