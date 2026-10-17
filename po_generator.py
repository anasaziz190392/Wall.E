"""Auto-generate the final Purchase Order PDF with ReportLab."""
from __future__ import annotations

import datetime as dt
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from models import RFQ, Room


def generate_po_pdf(rfq: RFQ, room: Room, buyer_company: str = "Acme Manufacturing Ltd.") -> bytes:
    f = room.final_offer
    assert f is not None, "No agreed deal to turn into a PO"
    today = dt.date.today()
    po_no = f"PO-{today:%Y%m%d}-{abs(hash(room.supplier)) % 9000 + 1000}"
    delivery_date = today + dt.timedelta(days=f.delivery_days)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                            topMargin=20 * mm, bottomMargin=20 * mm, title=po_no)
    ss = getSampleStyleSheet()
    small = ParagraphStyle("small", parent=ss["Normal"], fontSize=8, textColor=colors.grey)
    story = [Paragraph("PURCHASE ORDER", ss["Title"]),
             Paragraph(f"<b>PO Number:</b> {po_no} &nbsp;&nbsp; <b>Date:</b> {today:%d %b %Y}", ss["Normal"]),
             Spacer(1, 8 * mm)]

    parties = Table([["BUYER", "SUPPLIER"], [buyer_company, room.supplier]], colWidths=[85 * mm, 85 * mm])
    parties.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                                 ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a5f")),
                                 ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                 ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                                 ("PADDING", (0, 0), (-1, -1), 6)]))
    story += [parties, Spacer(1, 8 * mm)]

    unit = f.price / rfq.quantity
    lines = Table([["Description", "Qty", "Unit price (USD)", "Total (USD)"],
                   [rfq.item, f"{rfq.quantity:,}", f"{unit:,.2f}", f"{f.price:,.2f}"],
                   ["", "", "TOTAL", f"{f.price:,.2f}"]],
                  colWidths=[80 * mm, 20 * mm, 35 * mm, 35 * mm])
    lines.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef5")),
                               ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                               ("FONTNAME", (-2, -1), (-1, -1), "Helvetica-Bold"),
                               ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                               ("GRID", (0, 0), (-1, -2), 0.5, colors.lightgrey),
                               ("PADDING", (0, 0), (-1, -1), 6)]))
    story += [lines, Spacer(1, 8 * mm)]

    terms = Table([["Delivery lead time", f"{f.delivery_days} days (by {delivery_date:%d %b %Y})"],
                   ["Payment terms", f"Net {f.payment_days} days"],
                   ["Negotiation rounds", f"{max(o.round for o in room.offers)} of {rfq.max_rounds}"],
                   ["Selection score", f"{room.score}/100"]], colWidths=[50 * mm, 120 * mm])
    terms.setStyle(TableStyle([("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                               ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                               ("PADDING", (0, 0), (-1, -1), 5)]))
    story += [Paragraph("Commercial Terms", ss["Heading3"]), terms, Spacer(1, 8 * mm)]

    hist = [["Rnd", "Party", "Action", "Price (USD)", "Days", "Net"]]
    for o in room.offers:
        hist.append([o.round, o.party.title(), o.action.title(), f"{o.price:,.0f}", o.delivery_days, o.payment_days])
    h = Table(hist, colWidths=[15 * mm, 30 * mm, 30 * mm, 40 * mm, 20 * mm, 20 * mm], repeatRows=1)
    h.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef5")),
                           ("FONTSIZE", (0, 0), (-1, -1), 8), ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey)]))
    story += [Paragraph("Negotiation Audit Trail", ss["Heading3"]), h, Spacer(1, 10 * mm),
              Paragraph("Generated automatically by the Closed-Room B2B Negotiation Hub. "
                        "Private budget and supplier floor margins are not disclosed in this document.", small)]
    doc.build(story)
    return buf.getvalue()
