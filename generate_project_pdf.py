import os
import textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

def build_pdf(output_path):
    page_w = 595.27
    page_h = 841.89
    pdf = canvas.Canvas(output_path, pagesize=(page_w, page_h))

    # Color Palette Tokens
    c_brand = HexColor("#e11d48")      # Crimson Red
    c_brand_dark = HexColor("#be123c") # Deep Crimson
    c_slate_900 = HexColor("#0f172a")  # Dark Slate
    c_slate_700 = HexColor("#334155")  # Secondary Text
    c_slate_500 = HexColor("#64748b")  # Muted Text
    c_slate_200 = HexColor("#e2e8f0")  # Subtle Border
    c_slate_300 = HexColor("#cbd5e1")  # Medium Border
    c_slate_100 = HexColor("#f1f5f9")  # Subtle Surface
    c_slate_50 = HexColor("#f8fafc")   # Page Canvas
    c_white = HexColor("#ffffff")      # Card Surface
    c_green = HexColor("#047857")      # Success
    c_green_bg = HexColor("#ecfdf5")   # Green Pill
    c_green_bdr = HexColor("#a7f3d0")  # Green Border
    c_blue = HexColor("#2563eb")       # Accent Blue
    c_blue_bg = HexColor("#eff6ff")    # Blue Pill
    c_rose_bg = HexColor("#fff1f2")    # Rose Pill
    c_rose_bdr = HexColor("#fecdd3")   # Rose Border

    margin_x = 36
    content_w = page_w - (margin_x * 2)

    def draw_page_frame(page_num, total_pages, title_subtitle):
        # Canvas Background
        pdf.setFillColor(c_slate_50)
        pdf.rect(0, 0, page_w, page_h, fill=1, stroke=0)

        # Top Accent Strip
        pdf.setFillColor(c_brand)
        pdf.rect(0, page_h - 4, page_w, 4, fill=1, stroke=0)

        # Header Bar
        header_h = 44
        header_y = page_h - 4 - header_h
        pdf.setFillColor(c_white)
        pdf.rect(0, header_y, page_w, header_h, fill=1, stroke=0)
        pdf.setStrokeColor(c_slate_200)
        pdf.setLineWidth(1)
        pdf.line(0, header_y, page_w, header_y)

        # Brand Icon
        icon_s = 24
        icon_x = margin_x
        icon_y = header_y + 10
        pdf.setFillColor(c_brand)
        pdf.roundRect(icon_x, icon_y, icon_s, icon_s, 4, fill=1, stroke=0)
        pdf.setFillColor(c_white)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawCentredString(icon_x + 12, icon_y + 7, "K")

        # Brand Title
        pdf.setFillColor(c_slate_900)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(icon_x + 32, icon_y + 11, "Kamnath")
        kw = pdf.stringWidth("Kamnath", "Helvetica-Bold", 13)
        pdf.setFillColor(c_brand)
        pdf.drawString(icon_x + 32 + kw + 2, icon_y + 11, "Events")

        pdf.setFillColor(c_slate_500)
        pdf.setFont("Helvetica-Bold", 6.5)
        pdf.drawString(icon_x + 32, icon_y + 1, "SYSTEM ARCHITECTURE & TECHNICAL SPECIFICATION")

        # Header Right Meta
        pdf.setFillColor(c_slate_700)
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawRightString(page_w - margin_x, icon_y + 10, title_subtitle)
        pdf.setFillColor(c_slate_500)
        pdf.setFont("Helvetica", 7)
        pdf.drawRightString(page_w - margin_x, icon_y + 1, f"Document Page {page_num} of {total_pages} • Academic & Production Reference")

        # Footer Bar
        footer_h = 28
        pdf.setFillColor(c_white)
        pdf.rect(0, 0, page_w, footer_h, fill=1, stroke=0)
        pdf.setStrokeColor(c_slate_200)
        pdf.setLineWidth(1)
        pdf.line(0, footer_h, page_w, footer_h)

        pdf.setFillColor(c_slate_500)
        pdf.setFont("Helvetica", 7)
        pdf.drawString(margin_x, 10, "Kamnath Events Platform • Python Django Framework • MySQL Relational Database • ReportLab Vector Engine")
        pdf.drawRightString(page_w - margin_x, 10, f"Page {page_num} of {total_pages}")

    # =========================================================================
    # PAGE 1: SYSTEM OVERVIEW & ARCHITECTURE DIAGRAM
    # =========================================================================
    draw_page_frame(1, 4, "System Overview & MTV Architecture")

    # Banner Hero Card
    hero_y = page_h - 48 - 68
    hero_h = 64
    pdf.setFillColor(c_white)
    pdf.setStrokeColor(c_slate_300)
    pdf.roundRect(margin_x, hero_y, content_w, hero_h, 6, fill=1, stroke=1)

    pdf.setFillColor(c_rose_bg)
    pdf.setStrokeColor(c_rose_bdr)
    pdf.roundRect(margin_x + 14, hero_y + hero_h - 20, 110, 14, 3, fill=1, stroke=1)
    pdf.setFillColor(c_brand)
    pdf.setFont("Helvetica-Bold", 6.5)
    pdf.drawCentredString(margin_x + 14 + 55, hero_y + hero_h - 16, "FULL-STACK DJANGO WEB APP")

    pdf.setFillColor(c_slate_900)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(margin_x + 14, hero_y + 24, "Kamnath Events Ticketing & Management Platform")

    pdf.setFillColor(c_slate_700)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(
        margin_x + 14,
        hero_y + 10,
        "Production-grade event discovery, direct pass reservation, automated PDF ticket rendering, and admin console."
    )

    # Section 1 Title
    s1_y = hero_y - 20
    pdf.setFillColor(c_slate_900)
    pdf.setFont("Helvetica-Bold", 10.5)
    pdf.drawString(margin_x, s1_y, "1. High-Level Model-Template-View (MTV) Architecture")
    pdf.setFillColor(c_slate_500)
    pdf.setFont("Helvetica", 7.5)
    pdf.drawString(margin_x + 310, s1_y, "Data Flow from Browser Request to Response")

    # Architecture Diagram Container
    diag_y = s1_y - 170
    diag_h = 162
    pdf.setFillColor(c_white)
    pdf.setStrokeColor(c_slate_200)
    pdf.roundRect(margin_x, diag_y, content_w, diag_h, 6, fill=1, stroke=1)

    # Box 1: Client / Browser
    b1_x, b1_y, b1_w, b1_h = margin_x + 14, diag_y + 86, 96, 62
    pdf.setFillColor(c_slate_100)
    pdf.setStrokeColor(c_slate_300)
    pdf.roundRect(b1_x, b1_y, b1_w, b1_h, 5, fill=1, stroke=1)
    pdf.setFillColor(c_slate_900)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(b1_x + 48, b1_y + 46, "CLIENT BROWSER")
    pdf.setFillColor(c_slate_500)
    pdf.setFont("Helvetica", 6.5)
    pdf.drawCentredString(b1_x + 48, b1_y + 32, "HTML5 / ES6 JS")
    pdf.drawCentredString(b1_x + 48, b1_y + 20, "design-system.css")
    pdf.drawCentredString(b1_x + 48, b1_y + 9, "Booking & Modals")

    def draw_arrow_head(x1, y1, x2, y2, x3, y3, color):
        p = pdf.beginPath()
        p.moveTo(x1, y1)
        p.lineTo(x2, y2)
        p.lineTo(x3, y3)
        p.close()
        pdf.setFillColor(color)
        pdf.setStrokeColor(color)
        pdf.drawPath(p, fill=1, stroke=0)

    # Arrow 1: Browser -> URL Router
    pdf.setStrokeColor(c_brand)
    pdf.setLineWidth(1.5)
    pdf.line(b1_x + b1_w, b1_y + 31, b1_x + b1_w + 24, b1_y + 31)
    draw_arrow_head(b1_x + b1_w + 24, b1_y + 35, b1_x + b1_w + 24, b1_y + 27, b1_x + b1_w + 30, b1_y + 31, c_brand)
    pdf.setFillColor(c_brand)
    pdf.setFont("Helvetica-Bold", 6)
    pdf.drawCentredString(b1_x + b1_w + 14, b1_y + 36, "HTTP")

    # Box 2: URL Dispatcher (urls.py)
    b2_x, b2_y, b2_w, b2_h = b1_x + b1_w + 32, diag_y + 86, 96, 62
    pdf.setFillColor(c_slate_100)
    pdf.setStrokeColor(c_slate_300)
    pdf.roundRect(b2_x, b2_y, b2_w, b2_h, 5, fill=1, stroke=1)
    pdf.setFillColor(c_slate_900)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(b2_x + 48, b2_y + 46, "URL ROUTER")
    pdf.setFillColor(c_slate_500)
    pdf.setFont("Helvetica", 6.5)
    pdf.drawCentredString(b2_x + 48, b2_y + 32, "EventManagement/")
    pdf.drawCentredString(b2_x + 48, b2_y + 20, "urls.py path table")
    pdf.drawCentredString(b2_x + 48, b2_y + 9, "Regex / Slugs")

    # Arrow 2: URL Router -> Views
    pdf.setStrokeColor(c_brand)
    pdf.setLineWidth(1.5)
    pdf.line(b2_x + b2_w, b2_y + 31, b2_x + b2_w + 24, b2_y + 31)
    draw_arrow_head(b2_x + b2_w + 24, b2_y + 35, b2_x + b2_w + 24, b2_y + 27, b2_x + b2_w + 30, b2_y + 31, c_brand)
    pdf.setFillColor(c_brand)
    pdf.setFont("Helvetica-Bold", 6)
    pdf.drawCentredString(b2_x + b2_w + 14, b2_y + 36, "ROUTE")

    # Box 3: View Logic (views.py)
    b3_x, b3_y, b3_w, b3_h = b2_x + b2_w + 32, diag_y + 86, 108, 62
    pdf.setFillColor(c_rose_bg)
    pdf.setStrokeColor(c_brand)
    pdf.roundRect(b3_x, b3_y, b3_w, b3_h, 5, fill=1, stroke=1)
    pdf.setFillColor(c_brand)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(b3_x + 54, b3_y + 46, "VIEWS (LOGIC)")
    pdf.setFillColor(c_slate_700)
    pdf.setFont("Helvetica", 6.5)
    pdf.drawCentredString(b3_x + 54, b3_y + 32, "main/views.py")
    pdf.drawCentredString(b3_x + 54, b3_y + 20, "Auth, Booking, Admin")
    pdf.drawCentredString(b3_x + 54, b3_y + 9, "Business Rules Engine")

    # Arrow 3: Views <-> Models
    pdf.setStrokeColor(c_blue)
    pdf.setLineWidth(1.5)
    pdf.line(b3_x + b3_w, b3_y + 31, b3_x + b3_w + 24, b3_y + 31)
    draw_arrow_head(b3_x + b3_w + 24, b3_y + 35, b3_x + b3_w + 24, b3_y + 27, b3_x + b3_w + 30, b3_y + 31, c_blue)
    pdf.setFillColor(c_blue)
    pdf.setFont("Helvetica-Bold", 6)
    pdf.drawCentredString(b3_x + b3_w + 14, b3_y + 36, "ORM")

    # Box 4: Models & Database
    b4_x, b4_y, b4_w, b4_h = b3_x + b3_w + 32, diag_y + 86, 96, 62
    pdf.setFillColor(c_blue_bg)
    pdf.setStrokeColor(c_blue)
    pdf.roundRect(b4_x, b4_y, b4_w, b4_h, 5, fill=1, stroke=1)
    pdf.setFillColor(c_blue)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(b4_x + 48, b4_y + 46, "MODELS & DB")
    pdf.setFillColor(c_slate_700)
    pdf.setFont("Helvetica", 6.5)
    pdf.drawCentredString(b4_x + 48, b4_y + 32, "Django ORM Engine")
    pdf.drawCentredString(b4_x + 48, b4_y + 20, "MySQL Relational")
    pdf.drawCentredString(b4_x + 48, b4_y + 9, "7 Schema Tables")

    # Bottom Branches from Views: Templates vs PDF Stream
    # Down Arrow from Views to lower branch
    mid_vx = b3_x + 54
    pdf.setStrokeColor(c_slate_300)
    pdf.setLineWidth(1.2)
    pdf.line(mid_vx, b3_y, mid_vx, diag_y + 60)

    # Left Branch: Templates (HTML/DTL)
    t_box_x, t_box_y, t_box_w, t_box_h = margin_x + 50, diag_y + 14, 180, 42
    pdf.line(mid_vx, diag_y + 60, t_box_x + (t_box_w / 2), diag_y + 60)
    pdf.line(t_box_x + (t_box_w / 2), diag_y + 60, t_box_x + (t_box_w / 2), t_box_y + t_box_h)
    pdf.setFillColor(c_white)
    pdf.setStrokeColor(c_slate_300)
    pdf.roundRect(t_box_x, t_box_y, t_box_w, t_box_h, 4, fill=1, stroke=1)
    pdf.setFillColor(c_slate_900)
    pdf.setFont("Helvetica-Bold", 7.5)
    pdf.drawString(t_box_x + 10, t_box_y + 28, "TEMPLATES (DTL Rendering)")
    pdf.setFillColor(c_slate_500)
    pdf.setFont("Helvetica", 6.5)
    pdf.drawString(t_box_x + 10, t_box_y + 17, "base.html, events.html, my_bookings.html")
    pdf.drawString(t_box_x + 10, t_box_y + 7, "Returns dynamic HTML5 to client browser")

    # Right Branch: ReportLab PDF Engine
    p_box_x, p_box_y, p_box_w, p_box_h = margin_x + 280, diag_y + 14, 180, 42
    pdf.line(mid_vx, diag_y + 60, p_box_x + (p_box_w / 2), diag_y + 60)
    pdf.line(p_box_x + (p_box_w / 2), diag_y + 60, p_box_x + (p_box_w / 2), p_box_y + p_box_h)
    pdf.setFillColor(c_white)
    pdf.setStrokeColor(c_brand)
    pdf.roundRect(p_box_x, p_box_y, p_box_w, p_box_h, 4, fill=1, stroke=1)
    pdf.setFillColor(c_brand)
    pdf.setFont("Helvetica-Bold", 7.5)
    pdf.drawString(p_box_x + 10, p_box_y + 28, "REPORTLAB PDF GENERATOR")
    pdf.setFillColor(c_slate_500)
    pdf.setFont("Helvetica", 6.5)
    pdf.drawString(p_box_x + 10, p_box_y + 17, "download_ticket() -> Canvas drawing engine")
    pdf.drawString(p_box_x + 10, p_box_y + 7, "Streams binary application/pdf pass with barcode")

    # Section 2: Technology Stack Cards (2x3 Grid)
    s2_y = diag_y - 20
    pdf.setFillColor(c_slate_900)
    pdf.setFont("Helvetica-Bold", 10.5)
    pdf.drawString(margin_x, s2_y, "2. Technology Stack & Architectural Decisions")

    grid_y = s2_y - 275
    cards = [
        ("Python 3.14 & Django 6.0", "Core Back-End Web Framework", [
            "MTV design pattern ensures strict separation of concerns.",
            "Built-in session management isolates customer & admin state.",
            "Django ORM provides SQL injection immunity via parameterization."
        ], c_brand),
        ("MySQL Relational Database", "Persistence & Relational Integrity", [
            "Normalized 7-table schema with foreign key constraints.",
            "ACID transaction compliance guarantees zero booking collision.",
            "Django migrations allow repeatable schema versioning across teams."
        ], c_blue),
        ("ReportLab Vector PDF Engine", "Programmatic Ticket Generation", [
            "Native vector rendering eliminates slow external HTML converters.",
            "Generates scannable barcodes, ticket stubs, and entry guidelines.",
            "Embeds dynamic event thumbnails directly onto the pass canvas."
        ], c_green),
        ("Semantic HTML5 & Vanilla ES6 JS", "Lightweight Client Architecture", [
            "Zero heavy front-end framework dependencies (No React/Node).",
            "Instant page load speeds with modular scripts (auth.js, booking.js).",
            "Client-side instant filtering for events without page reloads."
        ], c_slate_900),
        ("Custom Modular Design System", "High-Contrast Light Theme UI", [
            "Standardized tokens in design-system.css (colors, radii, spacing).",
            "Responsive layout using Bootstrap 5 Grid without bloat.",
            "Clean aesthetic inspired by modern portals like BookMyShow."
        ], c_brand_dark),
        ("Session-Based Security Architecture", "Role-Based Access Control (RBAC)", [
            "Admin views verify request.session['admin_id'] strictly.",
            "Customer views verify request.session['user_id'] on checkout.",
            "CSRF token verification protects all state-changing POST requests."
        ], c_blue)
    ]

    card_w = (content_w - 14) / 2
    card_h = 82
    for idx, (ctitle, csub, points, acc_col) in enumerate(cards):
        col = idx % 2
        row = idx // 2
        cx = margin_x + (col * (card_w + 14))
        cy = grid_y + (2 - row) * (card_h + 10)

        pdf.setFillColor(c_white)
        pdf.setStrokeColor(c_slate_200)
        pdf.roundRect(cx, cy, card_w, card_h, 5, fill=1, stroke=1)

        # Accent pip
        pdf.setFillColor(acc_col)
        pdf.rect(cx, cy + card_h - 3, card_w, 3, fill=1, stroke=0)

        pdf.setFillColor(c_slate_900)
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawString(cx + 10, cy + card_h - 15, ctitle)

        pdf.setFillColor(c_slate_500)
        pdf.setFont("Helvetica-Bold", 6.5)
        pdf.drawString(cx + 10, cy + card_h - 25, csub.upper())

        pdf.setFillColor(c_slate_700)
        pdf.setFont("Helvetica", 6.5)
        py = cy + card_h - 37
        for pt in points:
            pdf.drawString(cx + 10, py, f"•  {pt}")
            py -= 11

    pdf.showPage()

    # =========================================================================
    # PAGE 2: DATABASE SCHEMA & ENTITY RELATIONSHIPS
    # =========================================================================
    draw_page_frame(2, 4, "Database Schema & Relational Design")

    p2_top = page_h - 48 - 18
    pdf.setFillColor(c_slate_900)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(margin_x, p2_top, "1. Relational Database Schema (7 Models)")
    pdf.setFillColor(c_slate_500)
    pdf.setFont("Helvetica", 7.5)
    pdf.drawString(margin_x + 280, p2_top, "Managed via main/models.py & Django ORM")

    # ER Flow visual banner
    er_y = p2_top - 58
    er_h = 50
    pdf.setFillColor(c_white)
    pdf.setStrokeColor(c_slate_200)
    pdf.roundRect(margin_x, er_y, content_w, er_h, 5, fill=1, stroke=1)

    # Diagram pills: Category (1) -> (N) Event (1) -> (N) Booking (N) <- (1) User
    pill_w = 90
    p_cat_x = margin_x + 12
    pdf.setFillColor(c_rose_bg)
    pdf.setStrokeColor(c_rose_bdr)
    pdf.roundRect(p_cat_x, er_y + 10, pill_w, 30, 4, fill=1, stroke=1)
    pdf.setFillColor(c_brand)
    pdf.setFont("Helvetica-Bold", 7.5)
    pdf.drawCentredString(p_cat_x + 45, er_y + 24, "Category (1)")
    pdf.setFont("Helvetica", 6)
    pdf.drawCentredString(p_cat_x + 45, er_y + 15, "Music, Fashion, Tech")

    # Arrow 1
    pdf.setStrokeColor(c_slate_500)
    pdf.line(p_cat_x + pill_w, er_y + 25, p_cat_x + pill_w + 18, er_y + 25)
    pdf.drawString(p_cat_x + pill_w + 4, er_y + 28, "1:N")

    # Event Pill
    p_evt_x = p_cat_x + pill_w + 22
    pdf.setFillColor(c_blue_bg)
    pdf.setStrokeColor(c_blue)
    pdf.roundRect(p_evt_x, er_y + 10, pill_w + 15, 30, 4, fill=1, stroke=1)
    pdf.setFillColor(c_blue)
    pdf.setFont("Helvetica-Bold", 7.5)
    pdf.drawCentredString(p_evt_x + 52, er_y + 24, "Event (N)")
    pdf.setFont("Helvetica", 6)
    pdf.drawCentredString(p_evt_x + 52, er_y + 15, "title, venue, price, img")

    # Arrow 2
    pdf.setStrokeColor(c_slate_500)
    pdf.line(p_evt_x + pill_w + 15, er_y + 25, p_evt_x + pill_w + 33, er_y + 25)
    pdf.drawString(p_evt_x + pill_w + 19, er_y + 28, "1:N")

    # Booking Pill
    p_bkg_x = p_evt_x + pill_w + 37
    pdf.setFillColor(c_green_bg)
    pdf.setStrokeColor(c_green_bdr)
    pdf.roundRect(p_bkg_x, er_y + 10, pill_w + 20, 30, 4, fill=1, stroke=1)
    pdf.setFillColor(c_green)
    pdf.setFont("Helvetica-Bold", 7.5)
    pdf.drawCentredString(p_bkg_x + 55, er_y + 24, "Booking (Pivot)")
    pdf.setFont("Helvetica", 6)
    pdf.drawCentredString(p_bkg_x + 55, er_y + 15, "user_id, event_id, status")

    # Arrow 3 (from User to Booking)
    p_usr_x = p_bkg_x + pill_w + 42
    pdf.setStrokeColor(c_slate_500)
    pdf.line(p_usr_x, er_y + 25, p_bkg_x + pill_w + 20, er_y + 25)
    pdf.drawString(p_usr_x - 18, er_y + 28, "N:1")

    # User Pill
    pdf.setFillColor(c_slate_100)
    pdf.setStrokeColor(c_slate_300)
    pdf.roundRect(p_usr_x + 4, er_y + 10, pill_w, 30, 4, fill=1, stroke=1)
    pdf.setFillColor(c_slate_900)
    pdf.setFont("Helvetica-Bold", 7.5)
    pdf.drawCentredString(p_usr_x + 49, er_y + 24, "User (Customer)")
    pdf.setFont("Helvetica", 6)
    pdf.drawCentredString(p_usr_x + 49, er_y + 15, "name, email, city")

    # Detailed Table Cards (4 Key Relational Models + 3 Support Models)
    tables_data = [
        ("Booking", "Core Transaction Ledger", [
            ("id", "AutoField (PK)", "Unique ticket booking reference (e.g. #35)."),
            ("user", "ForeignKey -> User", "Links ticket pass to registered customer."),
            ("event", "ForeignKey -> Event", "Links registration to target scheduled event."),
            ("booking_date", "DateField", "Date of order confirmation."),
            ("status", "CharField", "Lifecycle: 'Confirmed', 'Pending', 'Cancelled'.")
        ], c_green),
        ("Event", "Event Catalogs & Listings", [
            ("id", "AutoField (PK)", "Unique event identifier."),
            ("title", "CharField(100)", "Headline name of the concert or conference."),
            ("category", "ForeignKey -> Category", "Classifies event into Music, Tech, Fashion, etc."),
            ("event_date", "DateTimeField", "Exact date and time of event execution."),
            ("venue", "CharField(150)", "Auditorium address or stadium hall name."),
            ("price", "FloatField", "Admission fee per pass (e.g. Rs. 5999.00)."),
            ("image", "ImageField", "Poster image stored in media/events/.")
        ], c_blue),
        ("User", "Customer & Attendee Profiles", [
            ("id", "AutoField (PK)", "Unique attendee system ID."),
            ("name", "CharField(50)", "Full legal name printed on ticket pass."),
            ("email", "EmailField", "Unique identity used for sign-in & ticket delivery."),
            ("password", "CharField(255)", "Authentication credentials."),
            ("phone", "CharField(15)", "Contact mobile number for SMS/Emergency updates."),
            ("city", "CharField(50)", "City of residence for localized event recommendations.")
        ], c_slate_900),
        ("Admin", "Platform Administrators", [
            ("id", "AutoField (PK)", "Administrator account key."),
            ("name", "CharField(50)", "Admin login username."),
            ("email", "EmailField", "Administrative contact address."),
            ("password", "CharField(255)", "Admin authentication credential."),
            ("role", "CharField(50)", "Privilege level: Super Admin, Event Manager.")
        ], c_brand)
    ]

    t_grid_y = er_y - 20
    t_card_w = (content_w - 14) / 2
    t_card_h = 138

    for idx, (tname, tdesc, fields, border_col) in enumerate(tables_data):
        col = idx % 2
        row = idx // 2
        tx = margin_x + (col * (t_card_w + 14))
        ty = t_grid_y - ((row + 1) * t_card_h) - (row * 12)

        pdf.setFillColor(c_white)
        pdf.setStrokeColor(c_slate_200)
        pdf.roundRect(tx, ty, t_card_w, t_card_h, 5, fill=1, stroke=1)

        # Header of card
        pdf.setFillColor(c_slate_100)
        pdf.roundRect(tx, ty + t_card_h - 24, t_card_w, 24, 4, fill=1, stroke=0)
        pdf.rect(tx, ty + t_card_h - 24, t_card_w, 6, fill=1, stroke=0)

        pdf.setFillColor(border_col)
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawString(tx + 10, ty + t_card_h - 15, f"MODEL: {tname}")
        pdf.setFillColor(c_slate_500)
        pdf.setFont("Helvetica", 6.5)
        pdf.drawRightString(tx + t_card_w - 10, ty + t_card_h - 15, tdesc)

        # Fields table
        fy = ty + t_card_h - 36
        for f_name, f_type, f_desc in fields:
            pdf.setFillColor(c_slate_900)
            pdf.setFont("Helvetica-Bold", 6.5)
            pdf.drawString(tx + 10, fy, f_name)

            pdf.setFillColor(c_brand if "Foreign" in f_type or "PK" in f_type else c_slate_500)
            pdf.setFont("Helvetica-Oblique", 6)
            pdf.drawString(tx + 80, fy, f_type)

            pdf.setFillColor(c_slate_700)
            pdf.setFont("Helvetica", 6)
            pdf.drawString(tx + 185, fy, f_desc[:44])
            fy -= 14

    # Support Models Strip (Category, Contact, Subscribe)
    sup_y = t_grid_y - (2 * t_card_h) - 34
    pdf.setFillColor(c_slate_900)
    pdf.setFont("Helvetica-Bold", 9.5)
    pdf.drawString(margin_x, sup_y, "2. Supporting Application Tables")

    sup_box_y = sup_y - 68
    pdf.setFillColor(c_white)
    pdf.setStrokeColor(c_slate_200)
    pdf.roundRect(margin_x, sup_box_y, content_w, 62, 5, fill=1, stroke=1)

    sups = [
        ("Category", "Event classification lookup (Music, Fashion, Tech, Business).", "id (PK), category_name"),
        ("Contact", "Customer inquiries and support messages submitted via portal.", "id (PK), name, email, subject, message, created_at"),
        ("Subscribe", "Newsletter email broadcast directory for event alerts.", "id (PK), email")
    ]
    sw = (content_w - 20) / 3
    for s_idx, (s_name, s_exp, s_cols) in enumerate(sups):
        sx = margin_x + 6 + (s_idx * (sw + 4))
        pdf.setFillColor(c_slate_100)
        pdf.roundRect(sx, sup_box_y + 6, sw, 50, 4, fill=1, stroke=0)
        pdf.setFillColor(c_slate_900)
        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(sx + 8, sup_box_y + 42, s_name)
        pdf.setFillColor(c_slate_700)
        pdf.setFont("Helvetica", 6)
        pdf.drawString(sx + 8, sup_box_y + 30, s_exp[:46])
        pdf.setFillColor(c_slate_500)
        pdf.setFont("Helvetica-Oblique", 5.5)
        pdf.drawString(sx + 8, sup_box_y + 16, f"Fields: {s_cols}")

    # Ticket Lifecycle State Machine
    state_y = sup_box_y - 20
    pdf.setFillColor(c_slate_900)
    pdf.setFont("Helvetica-Bold", 9.5)
    pdf.drawString(margin_x, state_y, "3. Ticket Booking Lifecycle State Machine")

    sm_y = state_y - 64
    pdf.setFillColor(c_white)
    pdf.setStrokeColor(c_slate_200)
    pdf.roundRect(margin_x, sm_y, content_w, 58, 5, fill=1, stroke=1)

    steps = [
        ("1. Selection", "Attendee selects event card & clicks 'Book Now'.", c_slate_900),
        ("2. Modal Review", "Displays price, date, attendee verification modal.", c_blue),
        ("3. POST Submission", "Direct POST to /book-event/<id>/ creates booking.", c_brand),
        ("4. Confirmed State", "Status set to 'Confirmed'; Ticket ID stored in session.", c_green),
        ("5. PDF Pass Issued", "Attendee downloads official ReportLab ticket pass.", c_green)
    ]
    step_w = (content_w - 24) / 5
    for st_i, (st_t, st_d, st_c) in enumerate(steps):
        stx = margin_x + 6 + (st_i * (step_w + 3))
        pdf.setFillColor(c_slate_100)
        pdf.roundRect(stx, sm_y + 6, step_w, 46, 4, fill=1, stroke=0)
        pdf.setFillColor(st_c)
        pdf.setFont("Helvetica-Bold", 7)
        pdf.drawString(stx + 6, sm_y + 38, st_t)
        pdf.setFillColor(c_slate_700)
        pdf.setFont("Helvetica", 5.5)
        wrapped_st = textwrap.wrap(st_d, width=22)
        wy = sm_y + 26
        for w in wrapped_st:
            pdf.drawString(stx + 6, wy, w)
            wy -= 8

    pdf.showPage()

    # =========================================================================
    # PAGE 3: CORE APPLICATION MODULES & USER WORKFLOWS
    # =========================================================================
    draw_page_frame(3, 4, "Application Modules & Technical Workflows")

    p3_top = page_h - 48 - 18
    pdf.setFillColor(c_slate_900)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(margin_x, p3_top, "1. Core Functional Modules")
    pdf.setFillColor(c_slate_500)
    pdf.setFont("Helvetica", 7.5)
    pdf.drawString(margin_x + 310, p3_top, "End-to-End User Experience & Back-Office Controls")

    modules = [
        ("Event Discovery & Spotlight Carousel", "events(), home() in views.py", [
            "Featured Event Spotlight: Prominently highlights top headlining events with rotating carousel controls.",
            "Live Booking Aggregations: Computes live bookings using annotate(total_bookings=Count('booking')).",
            "Instant Category Filter: Client-side category pills (events-filter.js) filter DOM nodes instantaneously without full page reload."
        ], c_brand),
        ("Customer Authentication & Session State", "user_login(), user_register(), user_logout()", [
            "Seamless Modal Experience: Unauthenticated users clicking 'Book Now' trigger the auth modal without losing event context.",
            "Session Key Persistence: Stores user_id and user_name in Django's session engine upon verification.",
            "My Bookings Navigation: Authenticated state reveals 'My Tickets' in the navigation bar and enables instant downloads."
        ], c_blue),
        ("Direct Booking Engine", "book_event(), confirm_booking(), user_cancel_booking()", [
            "Instant Event Confirmation: Clean confirmation modal reviews ticket amount, date, and venue before final POST.",
            "Atomic Booking Record Creation: Writes directly to Booking table with status='Confirmed'.",
            "Customer Ticket Management: my_bookings.html lets attendees review all active passes and cancel reservations if needed."
        ], c_green),
        ("Administrative Console & Analytics", "dashboard(), admin_login()", [
            "Executive Metrics Ribbon: Aggregates platform KPIs (Total Events, Active Bookings, Platform Revenue, Registered Attendees).",
            "Complete CRUD Management: Add, edit, or remove events with poster image uploads, manage categories, and audit bookings.",
            "Inquiry Management: Read and resolve customer support inquiries submitted through the contact portal."
        ], c_slate_900)
    ]

    m_y = p3_top - 20
    m_card_w = content_w
    m_card_h = 86

    for m_title, m_sub, m_bullets, m_acc in modules:
        m_y -= (m_card_h + 10)
        pdf.setFillColor(c_white)
        pdf.setStrokeColor(c_slate_200)
        pdf.roundRect(margin_x, m_y, m_card_w, m_card_h, 5, fill=1, stroke=1)

        # Left accent bar
        pdf.setFillColor(m_acc)
        pdf.roundRect(margin_x, m_y, 4, m_card_h, 2, fill=1, stroke=0)

        pdf.setFillColor(c_slate_900)
        pdf.setFont("Helvetica-Bold", 8.5)
        pdf.drawString(margin_x + 14, m_y + m_card_h - 15, m_title)

        pdf.setFillColor(c_slate_500)
        pdf.setFont("Helvetica-Bold", 6.5)
        pdf.drawRightString(margin_x + m_card_w - 14, m_y + m_card_h - 15, m_sub)

        pdf.setStrokeColor(c_slate_100)
        pdf.line(margin_x + 14, m_y + m_card_h - 22, margin_x + m_card_w - 14, m_y + m_card_h - 22)

        pdf.setFillColor(c_slate_700)
        pdf.setFont("Helvetica", 7)
        by = m_y + m_card_h - 35
        for b in m_bullets:
            pdf.drawString(margin_x + 14, by, f"•  {b}")
            by -= 14

    # PDF Generator Technical Architecture Section
    p3_s2_y = m_y - 20
    pdf.setFillColor(c_slate_900)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(margin_x, p3_s2_y, "2. Dynamic ReportLab PDF Ticket Architecture")

    pdf_box_y = p3_s2_y - 170
    pdf_box_h = 162
    pdf.setFillColor(c_white)
    pdf.setStrokeColor(c_slate_300)
    pdf.roundRect(margin_x, pdf_box_y, content_w, pdf_box_h, 6, fill=1, stroke=1)

    # Left visual representation of ticket
    t_demo_x = margin_x + 14
    t_demo_y = pdf_box_y + 12
    t_demo_w = 150
    t_demo_h = 138

    pdf.setFillColor(c_white)
    pdf.setStrokeColor(c_slate_300)
    pdf.roundRect(t_demo_x, t_demo_y, t_demo_w, t_demo_h, 5, fill=1, stroke=1)

    # Demo Ticket Accent Top
    pdf.setFillColor(c_brand)
    pdf.rect(t_demo_x, t_demo_y + t_demo_h - 3, t_demo_w, 3, fill=1, stroke=0)

    # Demo Ticket Header
    pdf.setFillColor(c_brand)
    pdf.rect(t_demo_x + 6, t_demo_y + t_demo_h - 14, 8, 8, fill=1, stroke=0)
    pdf.setFillColor(c_slate_900)
    pdf.setFont("Helvetica-Bold", 5.5)
    pdf.drawString(t_demo_x + 18, t_demo_y + t_demo_h - 12, "Kamnath Events Pass")

    # Demo Ticket Event Row
    pdf.setFillColor(c_slate_100)
    pdf.roundRect(t_demo_x + 6, t_demo_y + t_demo_h - 42, 28, 24, 2, fill=1, stroke=0)
    pdf.setFillColor(c_slate_900)
    pdf.setFont("Helvetica-Bold", 5.5)
    pdf.drawString(t_demo_x + 38, t_demo_y + t_demo_h - 26, "Gujarat Fashion Week")
    pdf.setFillColor(c_slate_500)
    pdf.setFont("Helvetica", 4.5)
    pdf.drawString(t_demo_x + 38, t_demo_y + t_demo_h - 33, "Wed, 02 Sep 2026")
    pdf.drawString(t_demo_x + 38, t_demo_y + t_demo_h - 40, "Grand Ballroom, Ahmedabad")

    # Demo Ticket Grid
    pdf.setFillColor(c_slate_50)
    pdf.roundRect(t_demo_x + 6, t_demo_y + t_demo_h - 76, t_demo_w - 12, 30, 3, fill=1, stroke=0)
    pdf.setFillColor(c_slate_900)
    pdf.setFont("Helvetica-Bold", 5)
    pdf.drawString(t_demo_x + 10, t_demo_y + t_demo_h - 56, "ATTENDEE: Samar Rathod")
    pdf.drawString(t_demo_x + 10, t_demo_y + t_demo_h - 66, "EMAIL: samar07@gmail.com")
    pdf.setFillColor(c_brand)
    pdf.setFont("Helvetica-Bold", 6)
    pdf.drawRightString(t_demo_x + t_demo_w - 10, t_demo_y + t_demo_h - 62, "Rs. 5,999.00")

    # Demo Ticket Tear Line
    pdf.setStrokeColor(c_slate_300)
    pdf.setLineWidth(0.8)
    pdf.setDash(2, 2)
    pdf.line(t_demo_x + 6, t_demo_y + 44, t_demo_x + t_demo_w - 6, t_demo_y + 44)
    pdf.setDash([])

    # Demo Barcode
    bx = t_demo_x + 8
    by = t_demo_y + 14
    for b_w in [2, 1, 3, 1, 1, 2, 4, 1, 2, 1, 3, 2, 1, 1, 2, 3]:
        pdf.setFillColor(c_slate_900)
        pdf.rect(bx, by, b_w, 16, fill=1, stroke=0)
        bx += b_w + 1.2
    pdf.setFillColor(c_slate_500)
    pdf.setFont("Helvetica", 4)
    pdf.drawString(t_demo_x + 8, by - 6, "* KMN-PASS-000035-SEC *")

    # Right side explanation of PDF engine features
    rx = margin_x + 180
    pdf.setFillColor(c_slate_900)
    pdf.setFont("Helvetica-Bold", 8.5)
    pdf.drawString(rx, pdf_box_y + pdf_box_h - 18, "How download_ticket(request, booking_id) Works:")

    pdf_features = [
        ("Direct Vector Canvas", "Uses reportlab.pdfgen.canvas.Canvas directly on standard A4 (595.27 x 841.89 pt)."),
        ("Embedded Event Thumbnails", "Dynamically locates uploaded posters in media/events/ or static category fallbacks."),
        ("Design System Alignment", "Applies exact website hex tokens (HexColor) for unified brand identity."),
        ("TextWrap Intelligence", "Uses Python's textwrap module to eliminate awkward mid-word breaks."),
        ("Scannable Barcode & Security", "Renders vector gate admission barcodes (* KMN-PASS-XXXXXX-SEC *) and entry rules."),
        ("MIME Stream Response", "Delivers binary application/pdf response directly via Django's HttpResponse.")
    ]

    fy = pdf_box_y + pdf_box_h - 34
    for ftitle, fdesc in pdf_features:
        pdf.setFillColor(c_brand)
        pdf.setFont("Helvetica-Bold", 7)
        pdf.drawString(rx, fy, f"•  {ftitle}:")
        pdf.setFillColor(c_slate_700)
        pdf.setFont("Helvetica", 7)
        pdf.drawString(rx + 115, fy, fdesc[:56])
        fy -= 19

    pdf.showPage()

    # =========================================================================
    # PAGE 4: VIVA VOCE EXAMINATION & PROFESSOR DEFENSE GUIDE
    # =========================================================================
    draw_page_frame(4, 4, "Academic Defense & Viva Voce Q&A")

    p4_top = page_h - 48 - 18
    pdf.setFillColor(c_slate_900)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(margin_x, p4_top, "Comprehensive Viva Voce Examination Guide")
    pdf.setFillColor(c_slate_500)
    pdf.setFont("Helvetica", 7.5)
    pdf.drawString(margin_x + 280, p4_top, "Concise, Technically Sound Explanations for Evaluation")

    qa_list = [
        ("Q1: Explain the architectural pattern of this project. Is it MVC or MTV?",
         "Django implements the Model-Template-View (MTV) design pattern. The Model (models.py) encapsulates the data schema and queries the MySQL database via Django ORM. The Template (HTML files) represents the presentation layer, dynamically rendering data via the Django Template Language (DTL). The View (views.py) serves as the controller and business logic layer, receiving HTTP requests, verifying credentials, and returning responses or PDF streams.",
         c_brand),
        ("Q2: How does the application generate PDF tickets without third-party converters?",
         "Instead of relying on heavy headless browser converters (like wkhtmltopdf or Weasyprint), this project generates tickets programmatically using Python's native ReportLab library. ReportLab draws vector shapes, text, barcodes, and embeds image files directly onto a PDF canvas. This ensures zero external binary dependencies, instant generation times (under 50 milliseconds), and precise layout fidelity.",
         c_blue),
        ("Q3: How are customer and administrator authorizations separated?",
         "Authentication state is maintained using Django's session framework. Customer logins store their user key in request.session['user_id'], whereas administrator logins store their credentials in request.session['admin_id']. Protected management functions in views.py check for admin_id explicitly, redirecting unauthorized users to the admin login portal and preventing privilege escalation.",
         c_green),
        ("Q4: What query optimizations are implemented in the Django ORM queries?",
         "To eliminate the N+1 query problem, the events view utilizes select_related('category') to perform an SQL JOIN between the Event and Category tables in a single query. Furthermore, annotate(total_bookings=Count('booking')) calculates active registration totals directly within the SQL engine, avoiding multiple redundant subqueries.",
         c_slate_900),
        ("Q5: Why is the front-end developed in Vanilla JS rather than React or Angular?",
         "Vanilla ES6 JavaScript provides maximum execution speed, zero bundling/compilation overhead, and zero node_modules vulnerabilities. By organizing scripts into modular files (auth.js, booking.js, events-filter.js, dashboard.js) and standardizing design tokens in design-system.css, the application delivers instant page loads and seamless UX while remaining simple to maintain and deploy.",
         c_brand_dark),
        ("Q6: What measures protect the web application against security vulnerabilities?",
         "1. SQL Injection: Completely prevented because Django ORM parameterizes all SQL queries automatically.\n2. CSRF Attacks: Protected using {% csrf_token %} on all state-changing POST requests.\n3. XSS (Cross-Site Scripting): Django Template Language escapes all dynamic variables by default.\n4. Sensitive Data: Session keys are cookie-encrypted and verified server-side."
         , c_blue)
    ]

    qy = p4_top - 20
    q_card_w = content_w
    q_card_h = 92

    for q_title, q_ans, q_col in qa_list:
        qy -= (q_card_h + 10)
        pdf.setFillColor(c_white)
        pdf.setStrokeColor(c_slate_200)
        pdf.roundRect(margin_x, qy, q_card_w, q_card_h, 5, fill=1, stroke=1)

        # Question header
        pdf.setFillColor(c_slate_100)
        pdf.roundRect(margin_x, qy + q_card_h - 22, q_card_w, 22, 4, fill=1, stroke=0)
        pdf.rect(margin_x, qy + q_card_h - 22, q_card_w, 6, fill=1, stroke=0)

        pdf.setFillColor(q_col)
        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(margin_x + 10, qy + q_card_h - 15, q_title)

        # Answer body
        pdf.setFillColor(c_slate_700)
        pdf.setFont("Helvetica", 6.8)
        ans_lines = textwrap.wrap(q_ans, width=128)
        ay = qy + q_card_h - 32
        for line in ans_lines[:5]:
            pdf.drawString(margin_x + 10, ay, line)
            ay -= 11

    pdf.save()
    print(f"Documentation PDF generated successfully at: {output_path}")

if __name__ == "__main__":
    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Kamnath_Events_Project_Documentation.pdf")
    build_pdf(out_file)
