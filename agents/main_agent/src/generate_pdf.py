from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_rfp_response_pdf(final_response: dict, output_path: str):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    y = height - 40

    # Title
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, f"RFP RESPONSE : {final_response['rfp_reference']}")
    y -= 30

    # Products Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "OEM Product Recommendations")
    y -= 20

    c.setFont("Helvetica", 10)
    for p in final_response["products"]:
        c.drawString(
            40, y,
            f"Item {p['rfp_item_id']} | SKU: {p['sku']} | "
            f"{p['product_name']} | Price: Rs {p['unit_price']}"
        )
        y -= 15

    y -= 20

    # Tests Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Testing & Acceptance Costs")
    y -= 20

    c.setFont("Helvetica", 10)
    for t in final_response["tests"]:
        c.drawString(
            40, y,
            f"{t['test_name']} | Cost: Rs {t['price']}"
        )
        y -= 15

    y -= 20

    # Totals
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Cost Summary")
    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"Material Cost : Rs {final_response['totals']['material_cost']}")
    y -= 15
    c.drawString(40, y, f"Test Cost     : Rs {final_response['totals']['test_cost']}")
    y -= 15
    c.drawString(40, y, f"Grand Total   : Rs {final_response['totals']['grand_total']}")

    c.save()
