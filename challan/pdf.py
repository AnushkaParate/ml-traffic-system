"""Generates a simple e-challan PDF. Used both for emailing the challan as
an attachment and for letting the vehicle owner download it from their
dashboard.
"""

import io

from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas


def generate_challan_pdf(challan):
    """Returns the PDF as raw bytes (not saved to disk)."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    vehicle = challan.violation.vehicle
    owner = vehicle.owner

    c.setFillColor(colors.HexColor('#0F2440'))
    c.rect(0, height - 30 * mm, width, 30 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 18)
    c.drawString(20 * mm, height - 15 * mm, 'Traffic Management System')
    c.setFont('Helvetica', 11)
    c.drawString(20 * mm, height - 22 * mm, 'E-Challan Notice')

    c.setFillColor(colors.black)
    y = height - 45 * mm
    line_gap = 8 * mm

    def row(label, value):
        nonlocal y
        c.setFont('Helvetica-Bold', 11)
        c.drawString(20 * mm, y, f'{label}:')
        c.setFont('Helvetica', 11)
        c.drawString(70 * mm, y, str(value))
        y -= line_gap

    row('Challan No.', f'#{challan.pk}')
    row('Issued On', challan.issued_at.strftime('%d %b %Y, %I:%M %p'))
    row('Vehicle Plate', vehicle.plate_number)
    row('Vehicle Type', vehicle.get_vehicle_type_display())
    row('Owner Name', owner.username)
    row('Owner Email', owner.email)
    row('Violation Type', challan.violation.get_violation_type_display())
    row('Detected On', challan.violation.detected_at.strftime('%d %b %Y, %I:%M %p'))
    row('Video/Source', challan.violation.video_source)
    evidence = challan.violation.evidence_image
    if evidence and evidence.name:
        try:
            img = ImageReader(evidence.path)
            img_w, img_h = 60 * mm, 45 * mm
            c.drawImage(img, 120 * mm, height - 90 * mm, width=img_w, height=img_h,
                        preserveAspectRatio=True, anchor='n')
            c.setFont('Helvetica-Oblique', 8)
            c.drawString(120 * mm, height - 93 * mm, 'Evidence photo')
        except Exception:
            pass  # if the image file is missing/corrupt, skip it rather than fail the whole PDF

    y -= 4 * mm
    c.setFillColor(colors.HexColor('#C0392B') if challan.status == 'pending' else colors.HexColor('#2E7D53'))
    c.setFont('Helvetica-Bold', 14)
    c.drawString(20 * mm, y, f'Fine Amount: Rs. {challan.fine_amount}')
    y -= line_gap
    c.setFont('Helvetica-Bold', 12)
    c.drawString(20 * mm, y, f'Status: {challan.get_status_display().upper()}')

    c.setFillColor(colors.grey)
    c.setFont('Helvetica-Oblique', 9)
    c.drawString(20 * mm, 15 * mm, 'This is a system-generated challan. Log in to the Traffic Management System to pay your fine.')

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()