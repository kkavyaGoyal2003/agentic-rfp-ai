from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def generate_rfp_response_pdf(final_response: dict, output_path: str):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    y = height - 40

    # ==================================================
    # Title
    # ==================================================
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, f"RFP RESPONSE : {final_response['rfp_reference']}")
    y -= 30

    # ==================================================
    # OEM PRODUCT & PRICING SUMMARY
    # ==================================================
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "OEM Product & Pricing Summary")
    y -= 20

    # --------------------------------------------------
    # Prepare table data (NO COMPLIANCE)
    # --------------------------------------------------
    table_data = [[
        "Item",
        "SKU",
        "Product Description",
        "Qty",
        "Unit Price",
        "Total Price"
    ]]

    styles = getSampleStyleSheet()
    product_style = styles["Normal"]
    product_style.fontSize = 9
    product_style.leading = 11

    for p in final_response["consolidated_pricing_table"]:
        product_para = Paragraph(p["product_name"], product_style)

        table_data.append([
            p["item_no"],
            p["sku"],
            product_para,
            p["quantity"],
            f"{p['unit_price']:.2f}",
            f"{p['total_price']:.2f}"
        ])

    # --------------------------------------------------
    # Create table (A4-safe column widths)
    # --------------------------------------------------
    table = Table(
        table_data,
        colWidths=[35, 105, 215, 35, 60, 65]
    )

    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    # Draw table
    table.wrapOn(c, width, height)
    table_height = table._height
    table.drawOn(c, 40, y - table_height)

    y -= table_height + 30

    # ==================================================
    # TESTING & ACCEPTANCE COSTS
    # ==================================================
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Testing & Acceptance Costs")
    y -= 18

    c.setFont("Helvetica", 10)
    for t in final_response["tests"]:
        c.drawString(
            40, y,
            f"{t['test_name']}  |  Cost: Rs {t['price']:.2f}"
        )
        y -= 15

    y -= 20

    # ==================================================
    # COST SUMMARY
    # ==================================================
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Cost Summary")
    y -= 18

    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"Material Cost : Rs {final_response['totals']['material_cost']:.2f}")
    y -= 14
    c.drawString(40, y, f"Test Cost     : Rs {final_response['totals']['test_cost']:.2f}")
    y -= 14

    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, f"Grand Total   : Rs {final_response['totals']['grand_total']:.2f}")

    c.save()
