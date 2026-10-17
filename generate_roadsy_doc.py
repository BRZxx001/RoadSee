import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_document():
    doc = Document()
    
    # Page Margins - 1 inch
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    # Color Palette Constants
    HEX_PRIMARY = "1E3A5F"      # Deep Navy
    HEX_ACCENT = "2563EB"       # Electric Blue
    HEX_WARNING = "D97706"      # Amber
    HEX_DANGER = "DC2626"       # Crimson Red
    HEX_SUCCESS = "16A34A"      # Forest Green
    HEX_MUTED = "64748B"        # Slate Gray
    HEX_LIGHT_BG = "F8FAFC"     # Soft light background
    HEX_BORDER = "E2E8F0"       # Border gray
    
    COLOR_PRIMARY = RGBColor(0x1E, 0x3A, 0x5F)
    COLOR_ACCENT = RGBColor(0x25, 0x63, 0xEB)
    COLOR_MUTED = RGBColor(0x64, 0x74, 0x8B)
    COLOR_TEXT = RGBColor(0x1E, 0x29, 0x3B)
    
    # Helper to set cell background color
    def set_cell_background(cell, hex_color):
        shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shading_elm)

    # Helper to set cell borders
    def set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'<w:tcBorders {nsdecls("w")}/>')
        for side, color in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
            if color:
                b_elm = parse_xml(f'<w:{side} {nsdecls("w")} w:val="single" w:sz="6" w:space="0" w:color="{color}"/>')
                borders.append(b_elm)
            else:
                b_elm = parse_xml(f'<w:{side} {nsdecls("w")} w:val="none"/>')
                borders.append(b_elm)
        tcPr.append(borders)

    # Helper to add styled callout box
    def add_callout(text, title=None, border_color=HEX_ACCENT, bg_color=HEX_LIGHT_BG):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, bg_color)
        
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'''
            <w:tcBorders {nsdecls("w")}>
                <w:top w:val="none"/>
                <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>
                <w:bottom w:val="none"/>
                <w:right w:val="none"/>
            </w:tcBorders>
        ''')
        tcPr.append(borders)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.left_indent = Inches(0.15)
        p.paragraph_format.right_indent = Inches(0.15)
        
        if title:
            r_title = p.add_run(f"★ {title}\n")
            r_title.bold = True
            r_title.font.size = Pt(11)
            r_title.font.name = "Arial"
            r_title.font.color.rgb = COLOR_PRIMARY
            
        r_text = p.add_run(text)
        r_text.font.size = Pt(10)
        r_text.font.name = "Arial"
        r_text.font.color.rgb = COLOR_TEXT
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Helper for Headings
    def add_slide_header(slide_no, title, subtitle=None):
        p_badge = doc.add_paragraph()
        p_badge.paragraph_format.space_before = Pt(18)
        p_badge.paragraph_format.space_after = Pt(2)
        r_badge = p_badge.add_run(f"SLIDE {slide_no} — PRESENTATION BLUEPRINT")
        r_badge.font.size = Pt(8.5)
        r_badge.font.name = "Arial"
        r_badge.font.bold = True
        r_badge.font.color.rgb = RGBColor(0x25, 0x63, 0xEB)
        
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(title)
        r.font.size = Pt(17)
        r.font.name = "Arial"
        r.font.bold = True
        r.font.color.rgb = COLOR_PRIMARY
        
        if subtitle:
            p_sub = doc.add_paragraph()
            p_sub.paragraph_format.space_before = Pt(0)
            p_sub.paragraph_format.space_after = Pt(10)
            r_sub = p_sub.add_run(subtitle)
            r_sub.font.size = Pt(10.5)
            r_sub.font.italic = True
            r_sub.font.name = "Arial"
            r_sub.font.color.rgb = COLOR_MUTED

    # Helper for Bullet Lists
    def add_bullet(p, lead, body):
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.left_indent = Inches(0.25)
        r_lead = p.add_run(f"•  {lead}: ")
        r_lead.bold = True
        r_lead.font.size = Pt(10)
        r_lead.font.name = "Arial"
        r_lead.font.color.rgb = COLOR_PRIMARY
        
        r_body = p.add_run(body)
        r_body.font.size = Pt(10)
        r_body.font.name = "Arial"
        r_body.font.color.rgb = COLOR_TEXT

    # -------------------------------------------------------------
    # TITLE COVER SECTION
    # -------------------------------------------------------------
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(24)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("ROADSY")
    r_title.bold = True
    r_title.font.size = Pt(36)
    r_title.font.name = "Arial"
    r_title.font.color.rgb = COLOR_PRIMARY
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(12)
    r_sub = p_sub.add_run("AI-Powered Urban Mobility, Multi-Modal Disruption Navigation & Disaster Resilience Engine")
    r_sub.font.size = Pt(13)
    r_sub.font.bold = True
    r_sub.font.name = "Arial"
    r_sub.font.color.rgb = COLOR_ACCENT

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_after = Pt(24)
    r_meta = p_meta.add_run("Complete Presentation Blueprint & Technical Pitch Masterfile | Ready for PPT Creation\nHackathon Submission — Smart Cities, Sustainable Infrastructure & AI Mobility Track")
    r_meta.font.size = Pt(9.5)
    r_meta.font.name = "Arial"
    r_meta.font.color.rgb = COLOR_MUTED

    # Executive Overview Box
    add_callout(
        "Roadsy is a unified smart city mobility platform solving the multi-billion dollar crisis of uncoordinated roadworks, undetected dangerous potholes, monsoon waterlogging, and sudden traffic gridlocks. Powered by C++ graph algorithms, computer vision severity scoring, and predictive flood depth modeling, Roadsy dynamically calculates the 'Best Route' that completely bypasses road hazards while saving commuter time and municipal repair budgets.",
        title="EXECUTIVE ELEVATOR PITCH",
        border_color=HEX_PRIMARY,
        bg_color="EFF6FF"
    )

    doc.add_page_break()

    # =============================================================
    # SLIDE 1: THE URBAN MOBILITY CRISIS (PROBLEM STATEMENT)
    # =============================================================
    add_slide_header(1, "The Urban Mobility Crisis & Problem Statement", "Why conventional navigation tools fail modern Indian & global cities")
    
    p = doc.add_paragraph()
    add_bullet(p, "The Disruption Blindspot", "Traditional navigation apps (like Google Maps or Apple Maps) excel at highway routing and macro traffic congestion, but are completely blind to hyper-local micro disruptions: unannounced municipal pipe digs, fresh dangerous potholes, waterlogged underpasses, and overlapping multi-department road cuts.")
    
    p = doc.add_paragraph()
    add_bullet(p, "Uncoordinated Municipal Digs", "Water boards (DJB/BWSSB), electricity utilities, telecom fiber providers, and municipal corporations dig up the same newly resurfaced road repeatedly without cross-department visibility, causing instant artificial gridlocks.")
    
    p = doc.add_paragraph()
    add_bullet(p, "Vehicle Damage & Fatalities", "Over 3,500+ fatal road accidents and ₹25,000+ Cr in vehicular suspension/tire damage occur annually in India alone due to undetected high-severity craters and deep potholes.")
    
    p = doc.add_paragraph()
    add_bullet(p, "Monsoon Paralysis & Underpass Flooding", "Citizens receive navigation instructions straight into submerged underpasses and waterlogged transit corridors with zero predictive foresight regarding rainfall intensity and drain blockage.")

    p = doc.add_paragraph()
    add_bullet(p, "Lack of Integrated Prioritization", "City authorities receive thousands of fragmented citizen complaints without algorithmic severity ranking, causing emergency repair funds to be misallocated to minor cracks while life-threatening road faults remain open for months.")

    # Problem metrics table
    tbl = doc.add_table(rows=4, cols=3)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Critical Pain Point", "Current Industry Flaw", "Roadsy Paradigm Shift"]
    for i, h in enumerate(headers):
        cell = tbl.cell(0, i)
        set_cell_background(cell, "1E3A5F")
        p_c = cell.paragraphs[0]
        r = p_c.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(9.5)
        r.font.name = "Arial"
        
    data = [
        ("Navigation Blindspots", "Routes commuters through flooded or cratered roads based solely on speed.", "Proactively penalizes dangerous nodes; guides drivers through verified safe streets."),
        ("Departmental Silos", "Utility digs occur without central scheduling or overlap detection.", "Automated conflict engine flags overlapping agency digs before road destruction."),
        ("Pothole Inspection", "Manual surveys by ground engineers take 3-6 weeks to prioritize.", "AI Computer Vision grades pothole dimensions and assigns instant Severity Scores.")
    ]
    for row_idx, (c1, c2, c3) in enumerate(data, start=1):
        for col_idx, text in enumerate([c1, c2, c3]):
            cell = tbl.cell(row_idx, col_idx)
            set_cell_background(cell, "F8FAFC" if row_idx % 2 == 1 else "FFFFFF")
            set_cell_borders(cell, top=HEX_BORDER, bottom=HEX_BORDER, left=HEX_BORDER, right=HEX_BORDER)
            p_c = cell.paragraphs[0]
            p_c.paragraph_format.space_before = Pt(3)
            p_c.paragraph_format.space_after = Pt(3)
            r = p_c.add_run(text)
            r.font.size = Pt(9)
            r.font.name = "Arial"
            r.font.color.rgb = COLOR_TEXT

    doc.add_page_break()

    # =============================================================
    # SLIDE 2: INTRODUCING ROADSY (THE UNIFIED SOLUTION)
    # =============================================================
    add_slide_header(2, "Introducing Roadsy: The Unified Urban Intelligence System", "Smart, Resilient, Multi-Stakeholder Infrastructure Management")
    
    add_callout(
        "Roadsy is not just a consumer map app; it is a bidirectional smart city operating system. It bridges daily daily commuters who need safe and predictable travel with municipal authorities who need actionable, prioritized intelligence to maintain city assets.",
        title="SYSTEM VISION & CORE ARCHITECTURE",
        border_color=HEX_PRIMARY,
        bg_color="F1F5F9"
    )

    p = doc.add_paragraph()
    add_bullet(p, "Multi-Disruption Ingestion", "Tracks 5 live vectors simultaneously: Road Construction Zones, Potholes & Surface Cracks, Waterlogged Pockets, Live Traffic Congestion Points, and Predictive Urban Flood Inundation.")
    
    p = doc.add_paragraph()
    add_bullet(p, "Dynamic 'Best Route' Engine", "Calculates optimal routes utilizing a high-performance C++ Dijkstra routing engine. Automatically assigns penalty weights to flooded roads, severe potholes, and active construction digs, guaranteeing maximum safety while displaying exact time saved: e.g., '60 min (saves 26 min)'.")
    
    p = doc.add_paragraph()
    add_bullet(p, "AI Pothole Severity Classifier", "Computer vision model trained to evaluate depth, surface diameter, water accumulation, and structural damage—classifying potholes into Minor, Moderate, Severe, or Dangerous in milliseconds.")
    
    p = doc.add_paragraph()
    add_bullet(p, "Predictive Flood Simulation", "Simulates street-level inundation depths (0-55 cm) across 4 live rainfall scenarios (Dry, Moderate, Heavy, Cloudburst) by calculating drainage capacity, land elevation, and sewer blockage factors.")

    p = doc.add_paragraph()
    add_bullet(p, "Civic Authority Command Console", "Provides a prioritized municipal repair dashboard ranking repair jobs via an automated composite severity formula, cutting response times from weeks to hours.")

    p = doc.add_paragraph()
    add_bullet(p, "Celestial Day/Night Experience", "Full light/dark theme switcher with real-world celestial sun ☀️ and moon 🌙 controls, complete with dark neon OpenStreetMap cartography requiring zero proprietary API keys.")

    doc.add_page_break()

    # =============================================================
    # SLIDE 3: DATA INGESTION & SENSING ARCHITECTURE
    # =============================================================
    add_slide_header(3, "Data Ingestion: How Does Roadsy Sense City Disruptions?", "Answering the critical question: 'Where does the data come from and how do we measure traffic time?'")

    p = doc.add_paragraph()
    add_bullet(p, "Traffic Jam & Congestion Detection", "Roadsy models live traffic using OpenStreetMap (OSM) road network segmenting paired with simulated and live probe telemetry (GPS velocity data from fleets, autorickshaws, and commuter smartphones). When segment velocity drops below 30% of free-flow speed, a dynamic Traffic Congestion Node is created with estimated delay minutes.")
    
    p = doc.add_paragraph()
    add_bullet(p, "Municipal Work Permits (Construction)", "Ingests scheduled road opening notices from municipal open-data portals and public works department (PWD) registries, recording GPS coordinates, issuing agency, project duration, and affected lane count.")

    p = doc.add_paragraph()
    add_bullet(p, "Crowdsourced Geotagged Citizen Reports", "Citizens upload photo evidence and geolocations of potholes and waterlogging. The frontend captures precise device GPS lat/long and EXIF timestamp.")

    p = doc.add_paragraph()
    add_bullet(p, "Meteorological & Drainage Telemetry", "Pulls live precipitation data from weather APIs and combines it with city topographical digital elevation models (DEM) and municipal stormwater drain sensors to calculate runoff accumulation.")

    tbl = doc.add_table(rows=6, cols=4)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    pipe_headers = ["Disruption Type", "Primary Ingestion Source", "Telemetry Metric", "Update Latency"]
    for i, h in enumerate(pipe_headers):
        cell = tbl.cell(0, i)
        set_cell_background(cell, "1E3A5F")
        p_c = cell.paragraphs[0]
        r = p_c.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(9)
        r.font.name = "Arial"

    pipe_data = [
        ("Traffic Congestion", "GPS Probe Fleet Telemetry & OSM Speed Profiles", "Velocity Delta & Delay (mins)", "Real-time (30s)"),
        ("Pothole Reports", "Crowdsourced Mobile Uploads & Dashcam Feeds", "Image RGB + Lat/Long + Depth cm", "Sub-second AI"),
        ("Waterlogging Spots", "Citizen Reports + IoT Ultrasonic Drain Level Sensors", "Water Depth (cm) & Spread (m)", "Real-time"),
        ("Construction Digs", "PWD / Utility API Portals + Ground Geo-tags", "Closure Radius & Barricade Type", "Daily / Shift"),
        ("Urban Flood Prediction", "Open-Meteo Weather API + Municipal Invert Elevation", "Rainfall Rate (mm/hr) & Runoff", "5-minute model")
    ]
    for row_idx, row_vals in enumerate(pipe_data, start=1):
        for col_idx, val in enumerate(row_vals):
            cell = tbl.cell(row_idx, col_idx)
            set_cell_background(cell, "F8FAFC" if row_idx % 2 == 1 else "FFFFFF")
            set_cell_borders(cell, top=HEX_BORDER, bottom=HEX_BORDER, left=HEX_BORDER, right=HEX_BORDER)
            p_c = cell.paragraphs[0]
            p_c.paragraph_format.space_before = Pt(3)
            p_c.paragraph_format.space_after = Pt(3)
            r = p_c.add_run(val)
            r.font.size = Pt(8.5)
            r.font.name = "Arial"
            r.font.color.rgb = COLOR_TEXT

    doc.add_page_break()

    # =============================================================
    # SLIDE 4: THE C++ BEST ROUTE ENGINE & ALGORITHM
    # =============================================================
    add_slide_header(4, "High-Performance C++ Dijkstra Routing Engine", "Dynamic weighted graph optimization balancing travel distance, time, and safety penalties")

    add_callout(
        "While standard routing algorithms optimize purely for Euclidean distance or road speed limits, Roadsy constructs a Multi-Penalty Dynamic Graph where every road segment's weight is adjusted in real-time based on risk severity scores.",
        title="MATHEMATICAL FORMULATION & GRAPH MODEL",
        border_color=HEX_PRIMARY,
        bg_color="F8FAFC"
    )

    p = doc.add_paragraph()
    add_bullet(p, "Dynamic Edge Weight Formula", "Edge Cost = Base_Travel_Time + Traffic_Delay_Penalty + Pothole_Penalty + Waterlog_Penalty + Construction_Penalty")
    
    p = doc.add_paragraph()
    add_bullet(p, "Node Penalty Quantifications", "• Traffic Delay: +15 to +40 mins based on congestion tier (Heavy/Severe)\n• Pothole Severity: Dangerous (+20 mins penalty / avoid edge), Severe (+12 mins), Moderate (+5 mins)\n• Waterlogging: Avoid/High Risk (+35 mins penalty / hard block if depth > 30cm)\n• Construction: Full Road Cut (+40 mins / node blocked), Single Lane (+15 mins)")

    p = doc.add_paragraph()
    add_bullet(p, "Native C++ Dijkstra Speed", "Engineered in raw C++ (router.cpp) compiled with -O3 optimizations. Evaluates road graph networks with thousands of intersections in under 1.8 milliseconds, providing instant responsiveness.")

    p = doc.add_paragraph()
    add_bullet(p, "Route Comparison Matrix", "Compares the 'Normal Route' (unaware of micro-hazards, takes congested or flooded arterial roads) with the 'Best Route' (diverts commuters through clear, hazard-free roads). Shows precise commuter savings: e.g., Best Route: 60 min (saves 26 min) vs Normal Route: 86 min with 7 high-risk disruptions.")

    doc.add_page_break()

    # =============================================================
    # SLIDE 5: AI POTHOLE VISION & SEVERITY CLASSIFICATION
    # =============================================================
    add_slide_header(5, "AI-Driven Pothole Severity Classification", "Automated damage assessment, priority scoring, and municipal dispatch")

    p = doc.add_paragraph()
    add_bullet(p, "Computer Vision Pipeline", "Ingests road surface imagery captured by smartphones, city survey vans, or dashcams. Extracts geometric edge contours, depth gradients, water accumulation reflection, and asphalt degradation.")

    p = doc.add_paragraph()
    add_bullet(p, "4-Tiered Severity Classification", "• Dangerous (Score 80-100): Depth >15 cm or diameter >60 cm, structural base failure, acute 2-wheeler accident risk.\n• Severe (Score 60-79): Depth 8-15 cm, high tire/rim damage probability.\n• Moderate (Score 40-59): Depth 4-8 cm, surface erosion requiring patching.\n• Minor (Score 0-39): Surface cracks & minor depressions (<4 cm).")

    p = doc.add_paragraph()
    add_bullet(p, "Automated Verification & De-duplication", "Prevents duplicate reports of the same pothole by clustering geocoordinates within a 15-meter buffer radius, increasing authority confidence scores with each independent citizen report.")

    p = doc.add_paragraph()
    add_bullet(p, "Direct Routing Feedback Loop", "When a pothole is classified as 'Dangerous' or 'Severe', its coordinates are instantly pushed to the C++ Dijkstra engine, immediately re-routing nearby commuters away from that road segment.")

    doc.add_page_break()

    # =============================================================
    # SLIDE 6: PREDICTIVE FLOOD SIMULATION & WATERLOGGING
    # =============================================================
    add_slide_header(6, "Predictive Urban Flood & Waterlogging Engine", "Real-time rainfall simulation and street inundation hazard modeling")

    p = doc.add_paragraph()
    add_bullet(p, "Rainfall Scenario Switcher", "Allows both commuters and city planners to simulate 4 distinct weather regimes in real-time:\n1. Dry (0 mm/h) — Normal clear city baseline\n2. Moderate (12 mm/h) — Standard monsoon showers, slight ponding\n3. Heavy (45 mm/h) — Flash runoff, low-lying underpasses risk\n4. Cloudburst (95 mm/h) — Severe inundation, catastrophic underpass flooding")

    p = doc.add_paragraph()
    add_bullet(p, "Topographical Runoff Calculation", "Computes predicted flood depth (cm) based on 3 factors:\nPredicted_Depth = (Rainfall_Intensity × Runoff_Coeff) - (Drain_Capacity × (1 - Drain_Blockage%)) + Elevation_Deficit")

    p = doc.add_paragraph()
    add_bullet(p, "Dynamic Road Categorization", "• Safe (<10 cm): Passable for all vehicles\n• Caution (10-25 cm): 2-wheelers and sedans risk stalling; low-speed transit only\n• Danger / Avoid (>25 cm): High risk of engine hydro-locking; completely closed in the Best Route planner")

    p = doc.add_paragraph()
    add_bullet(p, "Proactive Flash Flood Alerts", "Dispatches early evacuation and diversion alerts to commuters 15-30 minutes before heavy downpours inundate vulnerable choke points.")

    doc.add_page_break()

    # =============================================================
    # SLIDE 7: MUNICIPAL COMMAND CONSOLE & AGENCY HARMONY
    # =============================================================
    add_slide_header(7, "Municipal Command Console & Agency Harmony", "Transforming municipal chaos into synchronized, algorithmic governance")

    p = doc.add_paragraph()
    add_bullet(p, "Central Disruption Registry", "Single-pane-of-glass administrative dashboard for Municipal Corporations, PWD, Police, and Utility Boards.")

    p = doc.add_paragraph()
    add_bullet(p, "Priority Repair Algorithm", "Ranks repair tasks dynamically based on a composite urgency formula:\nPriority_Index = (Severity_Weight × 0.40) + (Traffic_Volume_Weight × 0.35) + (Citizen_Report_Count × 0.15) + (Days_Open × 0.10)\nEnsures high-impact arterial road craters are filled within 24 hours.")

    p = doc.add_paragraph()
    add_bullet(p, "Agency Conflict Detector", "Flags overlapping excavation permits in advance. For example: If Delhi Jal Board (DJB) and Airtel Fiber request to dig the same road stretch within 20 days of each other, Roadsy issues an overlap warning, mandating a single joint excavation.")

    p = doc.add_paragraph()
    add_bullet(p, "SLA & Transparency Tracking", "Tracks status from 'Reported' → 'Inspected' → 'Contractor Dispatched' → 'Repaired', creating complete civic accountability.")

    doc.add_page_break()

    # =============================================================
    # SLIDE 8: TECH STACK, ARCHITECTURE & PERFORMANCE
    # =============================================================
    add_slide_header(8, "Full Technology Stack & System Architecture", "High-performance, modern, decoupled engineering")

    # Tech Stack Table
    tbl_tech = doc.add_table(rows=7, cols=3)
    tbl_tech.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_headers = ["Layer", "Technologies Used", "Engineering Rationale"]
    for i, h in enumerate(t_headers):
        cell = tbl_tech.cell(0, i)
        set_cell_background(cell, "1E3A5F")
        p_c = cell.paragraphs[0]
        r = p_c.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(9.5)
        r.font.name = "Arial"

    tech_data = [
        ("Frontend UI", "React 18 + Vite + Tailwind/CSS Variables", "Sub-second hot reloading, responsive draggable split panels, ultra-smooth map pan/zoom."),
        ("Map & GIS Layer", "Leaflet.js + OpenStreetMap (OSM)", "100% open-source, zero API-key dependencies, zero billing quota limits, custom dark-mode CSS filter."),
        ("Theme Engine", "Celestial Toggle (Sun/Moon real image assets)", "Instant visual switching between Daylight cartography and High-Contrast Dark Neon Mode."),
        ("Backend Services", "FastAPI (Python 3.11) + Uvicorn ASGI", "Asynchronous endpoints, automatic OpenAPI schema generation, rapid ML inference handling."),
        ("Routing Engine", "C++17 (compiled binary with -O3)", "Ultra-fast Dijkstra shortest-path computation with dynamic penalty graphs (<2ms execution)."),
        ("AI / ML Module", "PyTorch / OpenCV Computer Vision Pipeline", "Edge-contour segmentation and texture analysis for real-time pothole severity classification.")
    ]
    for row_idx, (c1, c2, c3) in enumerate(tech_data, start=1):
        for col_idx, text in enumerate([c1, c2, c3]):
            cell = tbl_tech.cell(row_idx, col_idx)
            set_cell_background(cell, "F8FAFC" if row_idx % 2 == 1 else "FFFFFF")
            set_cell_borders(cell, top=HEX_BORDER, bottom=HEX_BORDER, left=HEX_BORDER, right=HEX_BORDER)
            p_c = cell.paragraphs[0]
            p_c.paragraph_format.space_before = Pt(3)
            p_c.paragraph_format.space_after = Pt(3)
            r = p_c.add_run(text)
            r.font.size = Pt(8.5)
            r.font.name = "Arial"
            r.font.color.rgb = COLOR_TEXT

    doc.add_page_break()

    # =============================================================
    # SLIDE 9: COMPETITIVE MATRIX & INNOVATION DIFFERENTIATORS
    # =============================================================
    add_slide_header(9, "Competitive Matrix: Why Roadsy Outperforms Existing Solutions", "Comparative feature benchmark across key industry players")

    tbl_comp = doc.add_table(rows=6, cols=5)
    tbl_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_headers = ["Core Capability", "Roadsy", "Google Maps", "Apple Maps", "Waze"]
    for i, h in enumerate(c_headers):
        cell = tbl_comp.cell(0, i)
        set_cell_background(cell, "1E3A5F" if i == 1 else "334155")
        p_c = cell.paragraphs[0]
        r = p_c.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.size = Pt(8.5)
        r.font.name = "Arial"

    comp_data = [
        ("Multi-Penalty Hazard Rerouting", "YES (Dijkstra + Penalties)", "NO (Speed only)", "NO (Speed only)", "Partial (Crowd warnings)"),
        ("Pothole Vision Severity Scoring", "YES (Automated 4-tier AI)", "NO", "NO", "NO (User alert only)"),
        ("Predictive Flood Simulation", "YES (Elevation + Drainage)", "NO", "NO", "NO"),
        ("Municipal Repair Priority Queue", "YES (Algorithmic Dispatch)", "NO", "NO", "NO"),
        ("Utility Overlap Coordination", "YES (Inter-agency conflict)", "NO", "NO", "NO")
    ]
    for row_idx, row_vals in enumerate(comp_data, start=1):
        for col_idx, val in enumerate(row_vals):
            cell = tbl_comp.cell(row_idx, col_idx)
            if col_idx == 1:
                set_cell_background(cell, "EFF6FF")
            else:
                set_cell_background(cell, "F8FAFC" if row_idx % 2 == 1 else "FFFFFF")
            set_cell_borders(cell, top=HEX_BORDER, bottom=HEX_BORDER, left=HEX_BORDER, right=HEX_BORDER)
            p_c = cell.paragraphs[0]
            p_c.paragraph_format.space_before = Pt(3)
            p_c.paragraph_format.space_after = Pt(3)
            r = p_c.add_run(val)
            r.font.size = Pt(8)
            r.font.name = "Arial"
            if col_idx == 1:
                r.bold = True
                r.font.color.rgb = COLOR_ACCENT
            else:
                r.font.color.rgb = COLOR_TEXT

    doc.add_page_break()

    # =============================================================
    # SLIDE 10: BUSINESS MODEL, SCALABILITY & SOCIAL IMPACT
    # =============================================================
    add_slide_header(10, "Business Model, Scalability & Civic ROI", "How Roadsy creates economic value and scales across megacities")

    p = doc.add_paragraph()
    add_bullet(p, "B2G Smart City SaaS Model", "Licensing tier for Municipal Corporations (NDMC, BBMP, BMC), Public Works Departments, and Traffic Police Command Centres (₹50L - ₹2.5 Cr annual license per metro).")

    p = doc.add_paragraph()
    add_bullet(p, "B2B Logistics & Fleet Telematics API", "Delivery fleets (Swiggy, Zomato, Amazon, Delhivery) and ride-hailing services (Ola, Uber) pay an API per-call fee to consume Roadsy's 'Best Route' hazard-free routing, saving millions in vehicle wear & tear and fuel wastage.")

    p = doc.add_paragraph()
    add_bullet(p, "Insurance Telematics Partnership", "Automotive insurers access hyper-local road risk heatmaps to calibrate underwriting models and incentivize policyholders using damage-free routes.")

    p = doc.add_paragraph()
    add_bullet(p, "Measurable Civic ROI", "• 30% reduction in vehicle maintenance costs for daily commuters\n• 40% faster municipal resolution of dangerous road hazards\n• Zero underpass flood fatalities via proactive predictive closures\n• Up to 26 minutes saved per peak-hour commute")

    doc.add_page_break()

    # =============================================================
    # SLIDE 11: LIVE DEMO SCRIPT & JUDGES Q&A CHEAT SHEET
    # =============================================================
    add_slide_header(11, "Live Hackathon Pitch Script & Judge Q&A Defense", "Step-by-step 3-minute pitch playbook and winning answers")

    add_callout(
        "Demonstrate the live product with high energy following this exact 3-minute chronology. Every feature demonstrated addresses a real-world judge evaluation criterion.",
        title="3-MINUTE WINNING PITCH WALKTHROUGH",
        border_color=HEX_PRIMARY,
        bg_color="F1F5F9"
    )

    p = doc.add_paragraph()
    add_bullet(p, "0:00 - 0:30 (The Hook)", "'Judges, imagine following Google Maps into what looks like a 10-minute shortcut, only to plunge your car into a flooded underpass or break your axle on an unannounced road dig. Traditional maps optimize for speed; Roadsy optimizes for survival and road resilience.'")

    p = doc.add_paragraph()
    add_bullet(p, "0:30 - 1:15 (Live Map & Routing Demo)", "'Here is Roadsy running live on our city road network. In the sidebar, you see 23 live disruptions: traffic jams, unannounced digs, and craters. Watch what happens when I plan a route from Connaught Place to Cyber City: The Normal Route takes 86 minutes straight through 3 waterlog spots and severe traffic. But with one click, our C++ Dijkstra engine computes the Best Route: 60 minutes — saving 26 minutes while completely avoiding every single hazard.'")

    p = doc.add_paragraph()
    add_bullet(p, "1:15 - 1:55 (AI Vision & Weather Simulation)", "'Next, see our AI Pothole Vision analyzer: an uploaded photo is instantly graded as Dangerous with structural rim failure warnings. And over in our Weather Panel, we can dial up a Cloudburst (95 mm/h), watching low-lying zones turn red with predicted 48 cm water depths in real-time.'")

    p = doc.add_paragraph()
    add_bullet(p, "1:55 - 2:30 (Command Console & Celestial Toggle)", "'For city authorities, our Dashboard ranks repairs by composite severity and flags overlapping utility digs before taxpayers' money is wasted. Finally, our celestial toggle seamlessly shifts commuters between day and night with custom zero-cost dark neon cartography.'")

    p = doc.add_paragraph()
    add_bullet(p, "2:30 - 3:00 (The Close)", "'Roadsy is the nervous system modern smart cities have been waiting for. Thank you, and we welcome your questions!'")

    # Q&A Cheat Sheet Box
    add_callout(
        "Q1: 'How is this different from Google Maps or Waze?'\n"
        "Ans: Google Maps only monitors aggregate vehicle speeds and misses road cuts, pothole depth, and flood levels. Waze relies entirely on manual user warnings without AI validation or municipal authority integration. Roadsy penalizes risk in routing and directly drives municipal repair queues.\n\n"
        "Q2: 'Where does the traffic and flood data come from?'\n"
        "Ans: Traffic is calculated from probe GPS telemetry and velocity drops across OSM road segments. Flood predictions combine live weather radar precipitation with digital elevation models (DEM) and stormwater drain capacity.\n\n"
        "Q3: 'Why did you use C++ for the routing engine?'\n"
        "Ans: In a city graph with 50,000+ nodes and dynamic penalty weights that update every 30 seconds, Python-based graph traversal causes noticeable latency. C++ Dijkstra executes in under 2 milliseconds with zero garbage collection pauses.",
        title="JUDGES Q&A CHEAT SHEET (BULLETPROOF DEFENSE)",
        border_color=HEX_WARNING,
        bg_color="FFFBEB"
    )

    # Save to Downloads
    target_path = r"c:\Users\Brahmjot Singh\Downloads\Roadsy_Complete_Project_Presentation_Masterfile.docx"
    doc.save(target_path)
    print(f"Document successfully created at: {target_path}")

if __name__ == "__main__":
    create_document()
