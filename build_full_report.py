import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import win32com.client
import pypdf

def set_cell_margins(cell, top=20, bottom=20, left=50, right=50):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_shading(cell, color_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)

def set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}/>')
    borders = {'w:top': top, 'w:bottom': bottom, 'w:left': left, 'w:right': right}
    for b_name, b_val in borders.items():
        if b_val:
            node = parse_xml(f'<{b_name} {nsdecls("w")} w:val="{b_val.get("val", "single")}" w:sz="{b_val.get("sz", "4")}" w:space="0" w:color="{b_val.get("color", "CCCCCC")}"/>')
            tcBorders.append(node)
        else:
            node = parse_xml(f'<{b_name} {nsdecls("w")} w:val="none"/>')
            tcBorders.append(node)
    tcPr.append(tcBorders)

def prevent_row_split(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

def set_repeat_table_header(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

def generate_document(docx_path, page_map=None):
    doc = Document()
    p_map = page_map or {}

    normal_style = doc.styles['Normal']
    normal_font = normal_style.font
    normal_font.name = 'Times New Roman'
    normal_font.size = Pt(12)
    normal_font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = 1.5
    normal_style.paragraph_format.space_after = Pt(6)
    normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for sec in doc.sections:
        sec.page_width = Inches(8.27)
        sec.page_height = Inches(11.69)
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.25)
        sec.right_margin = Inches(1.0)

    def add_p(text, bold_prefix="", italic_prefix="", space_after=6, line_spacing=1.5):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = line_spacing
        p.paragraph_format.space_after = Pt(space_after)
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.bold = True
            r_pre.font.name = 'Times New Roman'
            r_pre.font.size = Pt(12)
        if italic_prefix:
            r_it = p.add_run(italic_prefix)
            r_it.italic = True
            r_it.font.name = 'Times New Roman'
            r_it.font.size = Pt(12)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        return p

    def add_bullet(text, bold_prefix=""):
        p = doc.add_paragraph(style='List Bullet')
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.35
        p.paragraph_format.space_after = Pt(3)
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.bold = True
            r_pre.font.name = 'Times New Roman'
            r_pre.font.size = Pt(12)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        return p

    def add_heading2(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.2
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        return p

    def add_caption(text, is_table=False):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4 if is_table else 4)
        p.paragraph_format.space_after = Pt(6 if is_table else 8)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.keep_with_next = True if is_table else False
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
        return p

    def add_highlight_run(p, text, is_bold=True):
        r = p.add_run(text)
        r.bold = is_bold
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        rPr = r._r.get_or_add_rPr()
        highlight = OxmlElement('w:highlight')
        highlight.set(qn('w:val'), 'yellow')
        rPr.append(highlight)
        return r

    # =========================================================================
    # SECTION 0: COVER PAGE, BONAFIDE CERTIFICATE, ACKNOWLEDGEMENT (NO NUMBERS)
    # =========================================================================
    sec0 = doc.sections[0]
    sec0.footer.is_linked_to_previous = False
    for p in sec0.footer.paragraphs: p.text = ""
    for elem in sec0._sectPr.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}footerReference'):
        sec0._sectPr.remove(elem)

    # 1. COVER PAGE
    t_logo = doc.add_table(rows=1, cols=2)
    t_logo.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_logo.autofit = False
    row_logo = t_logo.rows[0]
    prevent_row_split(row_logo)
    
    # Left logo: Anna Univ
    c_left = row_logo.cells[0]
    c_left.width = Inches(3.0)
    p_l = c_left.paragraphs[0]
    p_l.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_l.paragraph_format.space_after = Pt(0)
    if os.path.exists('assets/anna_univ_logo.png'):
        r_l = p_l.add_run()
        r_l.add_picture('assets/anna_univ_logo.png', height=Inches(1.0))
    set_cell_borders(c_left)

    # Right logo: LICET
    c_right = row_logo.cells[1]
    c_right.width = Inches(3.0)
    p_r = c_right.paragraphs[0]
    p_r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_r.paragraph_format.space_after = Pt(0)
    if os.path.exists('assets/licet_logo.png'):
        r_r = p_r.add_run()
        r_r.add_picture('assets/licet_logo.png', height=Inches(1.0))
    set_cell_borders(c_right)

    p_proj = doc.add_paragraph()
    p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj.paragraph_format.space_before = Pt(32)
    p_proj.paragraph_format.space_after = Pt(16)
    p_proj.paragraph_format.line_spacing = 1.3
    r = p_proj.add_run("DESIGN AND IMPLEMENTATION OF AN AI-POWERED RESUME SCREENING AND SKILL MATCHING SYSTEM (TALENTLENS) USING AWS SERVERLESS, AMAZON TEXTRACT AND REACT")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(14)
    p_sub.paragraph_format.space_after = Pt(14)
    r = p_sub.add_run("A MINI PROJECT REPORT")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)

    p_by = doc.add_paragraph()
    p_by.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_by.paragraph_format.space_after = Pt(14)
    r = p_by.add_run("Submitted by")
    r.italic = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)

    p_team = doc.add_paragraph()
    p_team.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_team.paragraph_format.space_after = Pt(4)
    add_highlight_run(p_team, "TEAM-[NO.]")

    for i in range(1, 4):
        p_stu = doc.add_paragraph()
        p_stu.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_stu.paragraph_format.space_after = Pt(4)
        add_highlight_run(p_stu, f"[STUDENT NAME {i}] – [REGISTER NUMBER]")

    p_deg = doc.add_paragraph()
    p_deg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_deg.paragraph_format.space_before = Pt(36)
    p_deg.paragraph_format.space_after = Pt(4)
    r = p_deg.add_run("BACHELOR OF TECHNOLOGY\nIN\nINFORMATION TECHNOLOGY")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)

    p_col = doc.add_paragraph()
    p_col.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_col.paragraph_format.space_before = Pt(40)
    p_col.paragraph_format.space_after = Pt(4)
    r = p_col.add_run("LOYOLA-ICAM COLLEGE OF ENGINEERING AND TECHNOLOGY\nANNA UNIVERSITY: CHENNAI 600 025\nNOV 2026")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)

    # 2. BONAFIDE CERTIFICATE (PAGE BREAK)
    doc.add_page_break()

    p_cert = doc.add_paragraph()
    p_cert.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert.paragraph_format.space_before = Pt(32)
    p_cert.paragraph_format.space_after = Pt(28)
    r = p_cert.add_run("BONAFIDE CERTIFICATE")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)

    p_cbody = doc.add_paragraph()
    p_cbody.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_cbody.paragraph_format.line_spacing = 1.5
    p_cbody.paragraph_format.space_after = Pt(48)
    r1 = p_cbody.add_run("Certified that the Mini project report on ")
    r1.font.name = 'Times New Roman'
    r2 = p_cbody.add_run("“DESIGN AND IMPLEMENTATION OF AN AI-POWERED RESUME SCREENING AND SKILL MATCHING SYSTEM (TALENTLENS) USING AWS SERVERLESS, AMAZON TEXTRACT AND REACT”")
    r2.bold = True
    r2.font.name = 'Times New Roman'
    r3 = p_cbody.add_run(" is the bonafide work of ")
    r3.font.name = 'Times New Roman'
    add_highlight_run(p_cbody, "[STUDENT NAME 1]([REGISTER NUMBER]), [STUDENT NAME 2]([REGISTER NUMBER]), [STUDENT NAME 3]([REGISTER NUMBER])", is_bold=True)
    r4 = p_cbody.add_run(" who carried out the project work under my supervision.")
    r4.font.name = 'Times New Roman'

    t_sig = doc.add_table(rows=1, cols=2)
    t_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_sig.autofit = False
    r_sig = t_sig.rows[0]
    prevent_row_split(r_sig)

    c_sig1 = r_sig.cells[0]
    c_sig1.width = Inches(3.0)
    p_s1 = c_sig1.paragraphs[0]
    p_s1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_s1.paragraph_format.line_spacing = 1.3
    r = p_s1.add_run("SIGNATURE\n\n\n\nDr. G. Shobana\nProject Coordinator\nDepartment of Information Technology\nLoyola-ICAM College of Engineering and\nTechnology\nLoyola Campus,\nNungambakkam, Chennai-34")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    set_cell_borders(c_sig1)

    c_sig2 = r_sig.cells[1]
    c_sig2.width = Inches(3.0)
    p_s2 = c_sig2.paragraphs[0]
    p_s2.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_s2.paragraph_format.line_spacing = 1.3
    r = p_s2.add_run("SIGNATURE\n\n\n\nMs. Sherril Sophie Maria Vincent\nHead of the Department\nDepartment of Information Technology\nLoyola-ICAM College of Engineering and\nTechnology\nLoyola Campus,\nNungambakkam, Chennai-34")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    set_cell_borders(c_sig2)

    # 3. ACKNOWLEDGEMENT (PAGE BREAK)
    doc.add_page_break()

    p_ack = doc.add_paragraph()
    p_ack.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ack.paragraph_format.space_before = Pt(32)
    p_ack.paragraph_format.space_after = Pt(20)
    r = p_ack.add_run("ACKNOWLEDGEMENT")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)

    add_p("First of all, we thank The Lord Almighty for showering His blessings on us, which enabled us to complete this project successfully.")
    add_p("We express our sincere gratitude to our beloved and respected Director, Rev. Dr. Justine SJ. We wish to acknowledge with thanks to our college, Dean of Students, Rev. Dr. Albert William SJ for his support and encouragement.")
    add_p("We extend our sincere gratitude to Dr. Baskar A., Principal, for his motivation and support towards this project.")
    add_p("We express our sincere gratitude to the Head of the Department of Information Technology, Ms Sherril Sophie Maria Vincent for her constant support, motivation, encouragement and being a source of inspiration throughout this project and during the course of this semester.")
    add_p("Our sincere thanks to our Project Coordinator Dr. G. Shobana for their valuable guidance in shaping this project.")
    add_p("We also take this opportunity to thank all the Faculty and Non-teaching staff members of the Department of Information Technology for their constant support. Finally, we thank each and every one who helped us to complete this project.")

    p_stusig = doc.add_paragraph()
    p_stusig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_stusig.paragraph_format.space_before = Pt(32)
    p_stusig.paragraph_format.line_spacing = 1.3
    add_highlight_run(p_stusig, "[STUDENT NAME 1]\n[STUDENT NAME 2]\n[STUDENT NAME 3]")

    # =========================================================================
    # SECTION 1: FRONT MATTER (ROMAN NUMERALS i, ii, iii, iv, v)
    # =========================================================================
    sec1 = doc.add_section()
    sec1.top_margin = Inches(1.0)
    sec1.bottom_margin = Inches(1.0)
    sec1.left_margin = Inches(1.25)
    sec1.right_margin = Inches(1.0)
    sec1.footer.is_linked_to_previous = False

    sectPr1 = sec1._sectPr
    for elem in sectPr1.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pgNumType'):
        sectPr1.remove(elem)
    sectPr1.append(parse_xml(f'<w:pgNumType {nsdecls("w")} w:start="1" w:fmt="lowerRoman"/>'))

    p_f1 = sec1.footer.paragraphs[0]
    p_f1.text = ""
    p_f1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_f1._p.append(parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w')))

    # ABSTRACT (Page i)
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abs.paragraph_format.space_before = Pt(26)
    p_abs.paragraph_format.space_after = Pt(14)
    r = p_abs.add_run("ABSTRACT")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)

    add_p(
        "TalentLens is a production-grade, cloud-native automated resume screening and candidate ranking system built using an "
        "event-driven AWS Serverless architecture and Amazon Textract machine learning document intelligence. In modern technical "
        "recruitment workflows, human talent acquisition specialists spend dozens of hours manually reviewing unstructured multi-page "
        "PDF resumes against specific job descriptions—an inefficient process prone to cognitive bias, missed qualifications, and human error. "
        "TalentLens eliminates these bottlenecks by enabling recruiters to seamlessly upload PDF resumes, define target job descriptions "
        "or keyword criteria, and immediately view ranked candidate leaderboards with quantitative match scores and explicit visual tags "
        "highlighting matched versus missing skills. The presentation tier is built as an interactive Single-Page Application (SPA) using React 18 "
        "and Vite, incorporating modular components for dashboard analytics, direct drag-and-drop resume ingestion, job requirement scoring, "
        "candidate inspection modals, and an integrated cloud architecture health visualizer. To completely bypass API Gateway payload limits "
        "(6 MB synchronous ceiling), the client requests secure presigned URLs from a serverless endpoint (GET /api/upload) and streams PDF binaries "
        "directly to an encrypted Amazon S3 private storage bucket with strict virtual-host addressing.",
        line_spacing=1.35, space_after=8
    )
    add_p(
        "Upon successful file ingestion, Amazon S3 publishes an ObjectCreated event notification directly into Amazon Simple Queue Service (SQS) "
        "with an associated Dead-Letter Queue (DLQ) configured for 14-day message retention across 3 retry cycles. An asynchronous AWS Lambda worker "
        "(Python 3.12) consumes queue batches, coordinates multi-page document text detection using Amazon Textract's asynchronous StartDocumentTextDetection "
        "API with exponential backoff polling, and applies a resilient local stream fallback parser (pypdf) to ensure 100% operational uptime. "
        "Extracted text and candidate metadata are indexed in Amazon DynamoDB under a single-table serverless model configured with pay-per-request "
        "billing. A comprehensive skill extraction engine evaluates candidates against an 80+ canonical skill dictionary spanning 8 engineering categories, "
        "expanding shorthand aliases (e.g., 'K8s' to Kubernetes, 'JS' to JavaScript, 'AWS' to Amazon Web Services) using word-boundary regular expressions. "
        "The complete system is formally defined using the AWS Serverless Application Model (SAM) with least-privilege IAM policies, achieving "
        "sub-second ranking latency, zero idle server cost, and 100% automated test coverage across 56 test cases.",
        line_spacing=1.35, space_after=4
    )

    # LIST OF FIGURES (Page ii)
    doc.add_page_break()
    p_lof = doc.add_paragraph()
    p_lof.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lof.paragraph_format.space_before = Pt(26)
    p_lof.paragraph_format.space_after = Pt(14)
    r = p_lof.add_run("LIST OF FIGURES")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)

    figs_data = [
        ("3.1", "Bull Diagram", p_map.get("fig_3_1", "6")),
        ("3.2", "Octopus Diagram", p_map.get("fig_3_2", "7")),
        ("4.1", "System Architecture Diagram", p_map.get("fig_4_1", "8")),
        ("4.2", "Data Flow Diagram - Level 0 (Context Diagram)", p_map.get("fig_4_2", "9")),
        ("4.3", "Data Flow Diagram - Level 1", p_map.get("fig_4_3", "9")),
        ("4.4", "Use Case Diagram", p_map.get("fig_4_4", "10")),
        ("4.5", "Sequence Diagram - Resume Upload & Text Extraction Flow", p_map.get("fig_4_5", "11")),
        ("4.6", "Entity-Relationship Diagram (DynamoDB Data Model)", p_map.get("fig_4_6", "12")),
        ("8.1", "Dashboard Overview & Pipeline Health", p_map.get("fig_8_1", "34")),
        ("8.2", "Cloud Architecture Interactive View", p_map.get("fig_8_2", "34")),
        ("8.3", "Candidate Pool & Pipeline Status Badges", p_map.get("fig_8_3", "35")),
        ("8.4", "Job Requirements & Criteria Configuration", p_map.get("fig_8_4", "35")),
        ("8.5", "Ranked Candidates & Dynamic Skill Match Scores", p_map.get("fig_8_5", "36")),
        ("8.6", "Candidate Inspection Modal & Extracted Resume Text", p_map.get("fig_8_6", "36")),
        ("8.7", "Resume Upload Interface & S3 Ingestion History", p_map.get("fig_8_7", "37")),
        ("8.8", "Candidate Tabular View with Status Badges", p_map.get("fig_8_8", "37")),
    ]

    t_lof = doc.add_table(rows=len(figs_data)+1, cols=3)
    t_lof.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_lof.autofit = False
    h_row = t_lof.rows[0]
    set_repeat_table_header(h_row)
    prevent_row_split(h_row)
    widths = [Inches(1.5), Inches(3.8), Inches(1.2)]
    aligns = [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER]

    for cell, title, w, al in zip(h_row.cells, ["FIGURE NO", "TITLE", "PAGE NO"], widths, aligns):
        cell.width = w
        set_cell_margins(cell, 18, 18, 50, 50)
        p = cell.paragraphs[0]
        p.alignment = al
        r = p.add_run(title)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)

    for ri, (f_num, f_title, f_pg) in enumerate(figs_data, start=1):
        row = t_lof.rows[ri]
        prevent_row_split(row)
        for ci, (val, w, al) in enumerate(zip([f_num, f_title, f_pg], widths, aligns)):
            cell = row.cells[ci]
            cell.width = w
            set_cell_margins(cell, 12, 12, 50, 50)
            p = cell.paragraphs[0]
            p.alignment = al
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)

    # LIST OF TABLES (Page iii)
    doc.add_page_break()
    p_lot = doc.add_paragraph()
    p_lot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lot.paragraph_format.space_before = Pt(26)
    p_lot.paragraph_format.space_after = Pt(14)
    r = p_lot.add_run("LIST OF TABLES")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)

    tables_data = [
        ("2.1", "Hardware Requirements", p_map.get("tbl_2_1", "4")),
        ("2.2", "Software Requirements", p_map.get("tbl_2_2", "5")),
        ("4.1", "DynamoDB Table Schema & Key Specifications", p_map.get("tbl_4_1", "12")),
        ("5.1", "REST API Endpoints Specification", p_map.get("tbl_5_1", "13")),
        ("5.2", "Resume Processing Validation & Status Transitions", p_map.get("tbl_5_2", "15")),
        ("5.3", "Canonical Skill Taxonomy & Aliases Mapping", p_map.get("tbl_5_3", "16")),
        ("5.4", "Frontend Views & Navigation Architecture", p_map.get("tbl_5_4", "17")),
        ("8.1", "Core Source Code Modules & File Catalog", p_map.get("tbl_8_1", "21")),
    ]

    t_lot = doc.add_table(rows=len(tables_data)+1, cols=3)
    t_lot.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_lot.autofit = False
    h_row = t_lot.rows[0]
    set_repeat_table_header(h_row)
    prevent_row_split(h_row)
    for cell, title, w, al in zip(h_row.cells, ["TABLE NO", "TITLE", "PAGE NO"], widths, aligns):
        cell.width = w
        set_cell_margins(cell, 25, 25, 50, 50)
        p = cell.paragraphs[0]
        p.alignment = al
        r = p.add_run(title)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)

    for ri, (t_num, t_title, t_pg) in enumerate(tables_data, start=1):
        row = t_lot.rows[ri]
        prevent_row_split(row)
        for ci, (val, w, al) in enumerate(zip([t_num, t_title, t_pg], widths, aligns)):
            cell = row.cells[ci]
            cell.width = w
            set_cell_margins(cell, 16, 16, 50, 50)
            p = cell.paragraphs[0]
            p.alignment = al
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)

    # LIST OF ABBREVIATIONS (Page iv - 20 items, exactly 1 page)
    doc.add_page_break()
    p_loa = doc.add_paragraph()
    p_loa.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loa.paragraph_format.space_before = Pt(26)
    p_loa.paragraph_format.space_after = Pt(14)
    r = p_loa.add_run("LIST OF ABBREVIATIONS")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)

    abbrevs = [
        ("AI", "Artificial Intelligence"),
        ("API", "Application Programming Interface"),
        ("ARN", "Amazon Resource Name"),
        ("AWS", "Amazon Web Services"),
        ("CORS", "Cross-Origin Resource Sharing"),
        ("DFD", "Data Flow Diagram"),
        ("DLQ", "Dead-Letter Queue"),
        ("DDB", "DynamoDB (Amazon NoSQL Database)"),
        ("ER", "Entity-Relationship"),
        ("HTTP", "HyperText Transfer Protocol"),
        ("IaC", "Infrastructure as Code"),
        ("IAM", "Identity and Access Management"),
        ("JSON", "JavaScript Object Notation"),
        ("KPI", "Key Performance Indicator"),
        ("OCR", "Optical Character Recognition"),
        ("PDF", "Portable Document Format"),
        ("REST", "Representational State Transfer"),
        ("S3", "Simple Storage Service (Amazon S3)"),
        ("SAM", "Serverless Application Model (AWS SAM)"),
        ("SPA", "Single Page Application"),
        ("SQS", "Simple Queue Service (Amazon SQS)"),
        ("UI", "User Interface"),
        ("UML", "Unified Modeling Language"),
        ("UUID", "Universally Unique Identifier"),
    ]

    t_loa = doc.add_table(rows=len(abbrevs)+1, cols=2)
    t_loa.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_loa.autofit = False
    h_row = t_loa.rows[0]
    set_repeat_table_header(h_row)
    prevent_row_split(h_row)
    ab_widths = [Inches(1.8), Inches(4.7)]
    for cell, title, w in zip(h_row.cells, ["ABBREVIATION", "EXPANSION"], ab_widths):
        cell.width = w
        set_cell_margins(cell, 18, 18, 50, 50)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(title)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)

    for ri, (abbr, exp) in enumerate(abbrevs, start=1):
        row = t_loa.rows[ri]
        prevent_row_split(row)
        for ci, (val, w) in enumerate(zip([abbr, exp], ab_widths)):
            cell = row.cells[ci]
            cell.width = w
            set_cell_margins(cell, 10, 10, 50, 50)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.0)

    # TABLE OF CONTENTS (Page v - Exactly 1 page)
    doc.add_page_break()
    p_toc = doc.add_paragraph()
    p_toc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc.paragraph_format.space_before = Pt(26)
    p_toc.paragraph_format.space_after = Pt(12)
    r = p_toc.add_run("TABLE OF CONTENTS")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)

    toc_entries = [
        ("", "ABSTRACT", "i"),
        ("", "LIST OF FIGURES", "ii"),
        ("", "LIST OF TABLES", "iii"),
        ("", "LIST OF ABBREVIATIONS", "iv"),
        ("1.", "INTRODUCTION", p_map.get("ch1", "1")),
        ("", "1.1 Problem Statement", p_map.get("ch1_1", "1")),
        ("", "1.2 Objectives", p_map.get("ch1_2", "1")),
        ("", "1.3 Software Engineering Concepts Demonstrated", p_map.get("ch1_3", "2")),
        ("2.", "REQUIREMENTS", p_map.get("ch2", "3")),
        ("", "2.1 Functional Requirements", p_map.get("ch2_1", "3")),
        ("", "2.2 Non-Functional Requirements", p_map.get("ch2_2", "4")),
        ("", "2.3 Hardware and Software Requirements", p_map.get("ch2_3", "4")),
        ("3.", "ANALYSIS", p_map.get("ch3", "6")),
        ("", "3.1 Presentation of Bull Diagram", p_map.get("ch3_1", "6")),
        ("", "3.2 Presentation of Octopus Diagram", p_map.get("ch3_2", "7")),
        ("4.", "SYSTEM DESIGN – UML MODELING", p_map.get("ch4", "8")),
        ("", "4.1 System Architecture Diagram", p_map.get("ch4_1", "8")),
        ("", "4.2 Data Flow Diagram", p_map.get("ch4_2", "9")),
        ("", "4.3 Use Case Diagram", p_map.get("ch4_3", "10")),
        ("", "4.4 Sequence Diagram", p_map.get("ch4_4", "11")),
        ("", "4.5 Database Design (ER Diagram)", p_map.get("ch4_5", "12")),
        ("5.", "MODULE DESCRIPTION", p_map.get("ch5", "13")),
        ("", "5.1 Resume Upload & Presigned URL Module", p_map.get("ch5_1", "13")),
        ("", "5.2 Asynchronous Document Ingestion & SQS Queue Module", p_map.get("ch5_2", "14")),
        ("", "5.3 Text Extraction & Amazon Textract OCR Module", p_map.get("ch5_3", "14")),
        ("", "5.4 Candidate Data Access & DynamoDB Storage Module", p_map.get("ch5_4", "15")),
        ("", "5.5 Keyword-Based Skill Extraction & Matching Engine Module", p_map.get("ch5_5", "15")),
        ("", "5.6 Candidate Retrieval & Ranking API Module", p_map.get("ch5_6", "16")),
        ("", "5.7 Frontend Routing, Dashboard & Real-Time Polling Module", p_map.get("ch5_7", "16")),
        ("", "5.8 Serverless Infrastructure & SAM Deployment Module", p_map.get("ch5_8", "17")),
        ("6.", "CONCLUSION", p_map.get("ch6", "18")),
        ("7.", "REFERENCES", p_map.get("ch7", "20")),
        ("8.", "APPENDICES", p_map.get("ch8", "21")),
        ("", "8.1 Code", p_map.get("ch8_1", "21")),
        ("", "8.2 Screenshots", p_map.get("ch8_2", "32")),
    ]

    t_toc = doc.add_table(rows=len(toc_entries)+1, cols=3)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_toc.autofit = False

    h_row = t_toc.rows[0]
    set_repeat_table_header(h_row)
    prevent_row_split(h_row)
    toc_widths = [Inches(1.2), Inches(4.3), Inches(1.0)]
    for cell, title, w, al in zip(h_row.cells, ["CHAPTER NO.", "TITLE", "PAGE NO."], toc_widths, aligns):
        cell.width = w
        set_cell_margins(cell, 15, 15, 50, 50)
        p = cell.paragraphs[0]
        p.alignment = al
        r = p.add_run(title)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9.5)

    for ri, (ch_num, ch_title, ch_pg) in enumerate(toc_entries, start=1):
        row = t_toc.rows[ri]
        prevent_row_split(row)
        for ci, (val, w, al) in enumerate(zip([ch_num, ch_title, ch_pg], toc_widths, aligns)):
            cell = row.cells[ci]
            cell.width = w
            set_cell_margins(cell, 8, 8, 50, 50)
            p = cell.paragraphs[0]
            p.alignment = al
            r = p.add_run(val)
            if ch_num or val in ["ABSTRACT", "LIST OF FIGURES", "LIST OF TABLES", "LIST OF ABBREVIATIONS", "CONCLUSION", "REFERENCES", "APPENDICES"]:
                r.bold = True
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.0)

    # =========================================================================
    # SECTION 2: BODY (ARABIC NUMERALS 1, 2, 3... STARTING AT CHAPTER 1)
    # =========================================================================
    sec2 = doc.add_section()
    sec2.top_margin = Inches(1.0)
    sec2.bottom_margin = Inches(1.0)
    sec2.left_margin = Inches(1.25)
    sec2.right_margin = Inches(1.0)
    sec2.footer.is_linked_to_previous = False

    sectPr2 = sec2._sectPr
    for elem in sectPr2.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pgNumType'):
        sectPr2.remove(elem)
    sectPr2.append(parse_xml(f'<w:pgNumType {nsdecls("w")} w:start="1" w:fmt="decimal"/>'))

    p_f2 = sec2.footer.paragraphs[0]
    p_f2.text = ""
    p_f2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_f2._p.append(parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w')))

    # -------------------------------------------------------------------------
    # CHAPTER 1: INTRODUCTION
    # -------------------------------------------------------------------------
    p_ch1 = doc.add_paragraph()
    p_ch1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ch1.paragraph_format.space_before = Pt(30)
    p_ch1.paragraph_format.space_after = Pt(18)
    r = p_ch1.add_run("CHAPTER 1\nINTRODUCTION")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)

    add_heading2("1.1 Problem Statement")
    add_p("Cloud Computing, Artificial Intelligence and Full-Stack Serverless Web Development.", bold_prefix="Domain: ")
    add_p(
        "In modern technical talent acquisition and recruitment operations, organizations routinely receive hundreds or thousands "
        "of candidate applications for open engineering positions. Each candidate submits a resume in Portable Document Format (PDF), "
        "featuring completely distinct document layouts, multi-column typography, graphics, varying fonts, and diverse phrasing. "
        "Recruiters and human resource specialists are tasked with manually inspecting every document, extracting relevant candidate "
        "skill sets, comparing individual qualifications against extensive job descriptions, and synthesizing candidate shortlists."
    )
    add_p(
        "This traditional manual screening methodology suffers from severe systemic limitations: it is exceedingly slow and labor-intensive, "
        "requires 15 to 30 minutes of manual review per resume, is highly susceptible to human fatigue and unconscious cognitive bias, and "
        "frequently overlooks qualified talent due to terminology mismatches (such as a recruiter failing to equate 'K8s' with 'Kubernetes' "
        "or 'React.js' with 'React'). Furthermore, traditional server-based recruitment web applications struggle with operational scaling, "
        "as uploading dozens of multi-megabyte PDF documents simultaneously chokes synchronous web servers, exhausts server memory, and violates "
        "standard API Gateway request payload size limits."
    )
    add_p(
        "This project implements TalentLens, a production-ready, fully serverless resume screening and automated skill matching platform. "
        "TalentLens allows recruiters to upload candidate resumes directly to an encrypted cloud repository using secure presigned URLs, "
        "automatically triggers an asynchronous machine-learning optical character recognition (OCR) pipeline powered by Amazon Textract and "
        "Amazon Simple Queue Service (SQS), indexes candidate data in Amazon DynamoDB, and dynamically evaluates candidate competency profiles "
        "against customizable job requirements through an intelligent keyword extraction engine. Recruiters are presented with a real-time, "
        "ranked candidate leaderboard displaying precise match percentages, matched skills (tagged in green), and missing qualification gaps "
        "(tagged in red), transforming hours of manual document inspection into an instantaneous, objective, and auditable screening workflow."
    )

    add_heading2("1.2 Objectives")
    add_bullet("To architect and implement an event-driven, fully serverless cloud backend on Amazon Web Services (AWS) utilizing AWS Lambda (Python 3.12), Amazon API Gateway, Amazon S3, Amazon SQS, and Amazon DynamoDB.")
    add_bullet("To eliminate synchronous web server bottlenecks and API payload limits by engineering a direct-to-S3 upload workflow leveraging time-bounded presigned URLs.")
    add_bullet("To achieve resilient, asynchronous document text extraction by coupling S3 ObjectCreated events with SQS processing queues, Dead-Letter Queues (DLQ), and Amazon Textract multi-page document text detection.")
    add_bullet("To provide an offline-capable, high-reliability fallback text extraction engine utilizing pypdf and byte-stream decompression in scenarios where cloud OCR services experience network latency or service quotas.")
    add_bullet("To design and implement a domain-specific skill extraction engine supporting an 80+ canonical skill taxonomy across 8 technology sectors with extensive alias and acronym normalization.")
    add_bullet("To calculate deterministic, objective candidate ranking metrics using mathematical set intersection and relative difference algorithms, providing transparent match percentage scores and skill gap analysis.")
    add_bullet("To deliver a responsive, component-based user interface using React 18 and Vite, incorporating executive KPI overview cards, interactive cloud architecture health visualizers, and automatic 5-second polling state synchronization.")
    add_bullet("To define the entire infrastructure as code using the AWS Serverless Application Model (SAM) with least-privilege IAM policies, ensuring reproducible, secure deployments across cloud environments.")
    add_bullet("To validate system correctness, security boundaries, and algorithm accuracy through a comprehensive automated testing suite encompassing 56 unit and integration test cases across Python (PyTest) and JavaScript (Vitest).")

    add_heading2("1.3 Software Engineering Concepts Demonstrated")
    add_p("The TalentLens engineering implementation rigorously applies established software engineering principles and modern cloud patterns:")
    add_bullet("Event-Driven Architecture (EDA): Decoupling file ingestion from document processing using Amazon SQS queues, eliminating tight server coupling and preventing request dropouts during sudden bursts in resume submission traffic.")
    add_bullet("Direct-to-Cloud Upload Pattern: Utilizing presigned S3 PUT URLs with strict content-type constraints, shifting heavy binary payload transport away from API Gateway and compute layers directly to object storage.")
    add_bullet("Serverless Microservices & Least-Privilege IAM: Isolating compute tasks into specialized, single-purpose AWS Lambda handlers (upload, candidates, match, process_resume), each governed by tightly scoped IAM policies (e.g., S3CrudPolicy, DynamoDBCrudPolicy).")
    add_bullet("Resilient Asynchronous Processing & Dead-Letter Queues (DLQ): Implementing automated redrive policies (maxReceiveCount = 3) and dedicated DLQ retention (14 days) to isolate malformed or unprocessable files without blocking active queues.")
    add_bullet("Graceful Degradation & Fallback Design: Incorporating redundant document extraction mechanisms in process_resume.py, automatically falling back to pypdf byte-level decompression if Textract service limits or network timeouts occur.")
    add_bullet("Canonical Taxonomy & Alias Normalization: Employing boundary-aware regular expressions and token normalization to map disparate candidate terminology (e.g., 'TS', 'K8s', 'Postgres') to standardized canonical skills.")
    add_bullet("Component-Based Single-Page UI Design: Developing a modular React 18 architecture with centralized API communication (api.js), responsive CSS styling, and optimistic UI state updates.")
    add_bullet("Infrastructure as Code (IaC): Encapsulating cloud resources, queues, permissions, and REST routes within a version-controlled AWS SAM template (template.yaml) for deterministic multi-environment provisioning.")
    add_bullet("Comprehensive Automated Test Verification: Implementing isolated unit and integration test suites using PyTest (backend mocks with boto3) and Vitest (React Testing Library), achieving 100% test pass rates.")

    # -------------------------------------------------------------------------
    # CHAPTER 2: REQUIREMENTS
    # -------------------------------------------------------------------------
    doc.add_page_break()
    p_ch2 = doc.add_paragraph()
    p_ch2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ch2.paragraph_format.space_before = Pt(30)
    p_ch2.paragraph_format.space_after = Pt(18)
    r = p_ch2.add_run("CHAPTER 2\nREQUIREMENTS")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)

    add_heading2("2.1 Functional Requirements")
    add_p("The functional requirements specify the software capabilities and operational workflows implemented within the TalentLens platform:")
    add_bullet("The system shall generate a secure, regional Amazon S3 presigned PUT URL upon receiving a valid GET /api/upload request specifying a resume filename.")
    add_bullet("The system shall validate that uploaded resume filenames possess a valid '.pdf' extension and reject non-PDF file submissions with HTTP status code 400.")
    add_bullet("The system shall initialize a new candidate record in Amazon DynamoDB upon presigned URL generation with candidateId (UUID v4), filename, S3 key, and initial status 'UPLOADING'.")
    add_bullet("The system shall allow the React web frontend to upload PDF binaries directly to the designated Amazon S3 bucket via the presigned URL, completely bypassing API Gateway.")
    add_bullet("The system shall trigger an automated S3 ObjectCreated event notification to an Amazon SQS queue whenever a PDF is successfully stored under the 'resumes/' S3 key prefix.")
    add_bullet("The system shall invoke an asynchronous worker Lambda (talentlens-process-resume) upon SQS message arrival with batch size 1 and individual batch item failure reporting.")
    add_bullet("The system shall update the candidate status in DynamoDB to 'PROCESSING' immediately upon initiating document analysis.")
    add_bullet("The system shall submit the resume PDF to Amazon Textract using StartDocumentTextDetection and poll GetDocumentTextDetection with exponential backoff until OCR completion.")
    add_bullet("The system shall fall back to local pypdf byte-stream extraction to extract text content if Amazon Textract is unreachable or returns a non-success status code.")
    add_bullet("The system shall heuristically parse the first 10 extracted text lines to extract the candidate's human name, falling back to a sanitized filename format if no valid name pattern is detected.")
    add_bullet("The system shall store the complete extracted resume text, candidate name, completion timestamp, and status 'COMPLETED' in Amazon DynamoDB.")
    add_bullet("The system shall provide a candidates listing endpoint (GET /api/candidates) returning all candidate records sorted by creation timestamp descending, with resumeText truncated to 200 characters for lightweight payload transfer.")
    add_bullet("The system shall automatically detect and transition stale candidate records stranded in 'UPLOADING' status for over 300 seconds (5 minutes) to 'FAILED' with an explanatory timeout error message.")
    add_bullet("The system shall accept a POST /api/match request containing job description criteria, execute canonical skill extraction against all completed candidates, and compute deterministic match percentages.")
    add_bullet("The system shall return candidates ranked in strictly descending order of match percentage, returning explicit lists of matched skills, missing skills, resume skills, and required skills.")
    add_bullet("The system shall provide a React single-page dashboard with dedicated tabbed views for Dashboard Overview, Candidate Pool, Job Requirements, and Resume Upload, automatically polling for candidate status updates every 5 seconds.")

    add_heading2("2.2 Non-Functional Requirements")
    add_p("The non-functional requirements define the architectural qualities, security constraints, and operational standards of the platform:")
    add_bullet("Security & Encryption: All uploaded resumes stored in Amazon S3 shall enforce server-side encryption and Block Public Access policies. Access to S3 objects shall occur exclusively through short-lived (300-second) presigned URLs.")
    add_bullet("Least-Privilege Access Control: All AWS Lambda functions shall execute under dedicated IAM roles with least-privilege resource policies (e.g., S3CrudPolicy, DynamoDBCrudPolicy), prohibiting wildcard administrative permissions.")
    add_bullet("Fault Tolerance & Dead-Letter Redrive: The SQS processing queue shall route unprocessable or failing messages to a dedicated Dead-Letter Queue (DLQ) after 3 failed attempts, retaining messages for 14 days (1,209,600 seconds) for diagnostic inspection.")
    add_bullet("Low Latency & High Performance: The skill matching engine shall execute in-memory tokenization and set algebra, processing and ranking candidate batches in under 50 milliseconds per candidate.")
    add_bullet("Elastic Scalability: The system shall employ fully serverless components (API Gateway, Lambda, SQS, DynamoDB On-Demand) that scale automatically from zero to thousands of concurrent requests without manual capacity provisioning.")
    add_bullet("Usability & Accessibility: The user interface shall provide an intuitive, dark-themed responsive design compatible with desktop displays, featuring color-coded visual skill tags (green for matched, red for missing) and clear progress indicators.")
    add_bullet("Cross-Origin Resource Sharing (CORS): The API Gateway HTTP API and S3 bucket shall return standardized CORS headers, allowing seamless cross-origin requests from modern web browsers.")
    add_bullet("Maintainability & Clean Architecture: The backend codebase shall be strictly modularized into event handlers (upload, candidates, match, process_resume) and shared domain libraries (skill_extractor, response).")
    add_bullet("Reliability & Graceful Degradation: The text extraction pipeline shall implement multi-tier fallback parsing, ensuring document ingestion succeeds even during external cloud service degradation.")
    add_bullet("Cost Efficiency: All infrastructure shall leverage AWS pay-per-request pricing, incurring zero operational cost during periods of recruitment inactivity.")

    add_heading2("2.3 Hardware and Software Requirements")
    add_p("The hardware and software specifications required for local development, automated testing, and cloud production deployment are detailed in Tables 2.1 and 2.2.")

    add_caption("Table 2.1: Hardware Requirements", is_table=True)
    hw_rows = [
        ("Processor", "Dual-Core x86_64 or Apple Silicon (2.0 GHz or higher)", "Executes local Python testing, Vite build server, and mock API services"),
        ("System Memory (RAM)", "4 GB minimum (8 GB recommended)", "Accommodates Node.js runtime, Python processes, browser instances, and Playwright"),
        ("Available Disk Space", "2 GB free storage space", "Stores node_modules, Python virtual environment, build artifacts, and test resumes"),
        ("Network Connectivity", "Broadband Internet (1 Mbps or higher)", "Required for downloading dependencies and deploying AWS SAM infrastructure"),
        ("Display Resolution", "1366 × 768 or higher", "Optimal rendering of the React recruitment dashboard and analytics modal views"),
    ]
    t_hw = doc.add_table(rows=len(hw_rows)+1, cols=3)
    t_hw.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_hw.autofit = False
    h_row = t_hw.rows[0]
    set_repeat_table_header(h_row)
    prevent_row_split(h_row)
    hw_widths = [Inches(1.8), Inches(2.7), Inches(2.2)]
    for cell, title, w, al in zip(h_row.cells, ["Component", "Minimum Specification", "Operational Purpose"], hw_widths, aligns):
        cell.width = w
        set_cell_shading(cell, "EAECEE")
        set_cell_margins(cell, 25, 25, 50, 50)
        p = cell.paragraphs[0]
        p.alignment = al
        r = p.add_run(title)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)

    for ri, (comp, spec, purp) in enumerate(hw_rows, start=1):
        row = t_hw.rows[ri]
        prevent_row_split(row)
        for ci, (val, w, al) in enumerate(zip([comp, spec, purp], hw_widths, aligns)):
            cell = row.cells[ci]
            cell.width = w
            set_cell_margins(cell, 16, 16, 50, 50)
            p = cell.paragraphs[0]
            p.alignment = al
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)

    add_caption("Table 2.2: Software Requirements", is_table=True)
    sw_rows = [
        ("Python 3.12", "Primary programming language for all backend AWS Lambda microservices"),
        ("Boto3 1.35+", "Official AWS SDK for Python, managing S3, SQS, DynamoDB, and Textract operations"),
        ("PyPDF 6.20+", "Pure-Python PDF parser providing local byte-stream extraction fallback"),
        ("PyTest 8.3+", "Automated testing framework for executing backend unit and mock test suites"),
        ("Node.js 18+ & npm", "JavaScript runtime environment for frontend development and dependency management"),
        ("React 18 & Vite 6", "Modern frontend component library and rapid module bundler powering the web dashboard"),
        ("Vitest 2.1+", "Fast Vite-native unit testing framework with React Testing Library integration"),
        ("AWS SAM CLI", "Serverless Application Model CLI for local build emulation and AWS CloudFormation deployment"),
        ("Amazon DynamoDB", "Serverless NoSQL database managing candidate records, statuses, and resume metadata"),
        ("Amazon S3", "Scalable cloud object storage for secure, private PDF resume file persistence"),
        ("Amazon Textract", "Cloud AI document service for multi-page asynchronous optical character recognition"),
        ("Amazon SQS", "Fully managed distributed message queuing service decoupling ingestion from processing"),
        ("Web Browser", "Current versions of Google Chrome, Microsoft Edge, Mozilla Firefox, or Apple Safari"),
    ]
    t_sw = doc.add_table(rows=len(sw_rows)+1, cols=2)
    t_sw.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_sw.autofit = False
    h_row = t_sw.rows[0]
    set_repeat_table_header(h_row)
    prevent_row_split(h_row)
    sw_widths = [Inches(2.4), Inches(4.3)]
    for cell, title, w in zip(h_row.cells, ["Software Package / Service", "Role in System Architecture"], sw_widths):
        cell.width = w
        set_cell_shading(cell, "EAECEE")
        set_cell_margins(cell, 25, 25, 50, 50)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(title)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)

    for ri, (sw_pkg, sw_role) in enumerate(sw_rows, start=1):
        row = t_sw.rows[ri]
        prevent_row_split(row)
        for ci, (val, w) in enumerate(zip([sw_pkg, sw_role], sw_widths)):
            cell = row.cells[ci]
            cell.width = w
            set_cell_margins(cell, 16, 16, 50, 50)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)

    # -------------------------------------------------------------------------
    # CHAPTER 3: ANALYSIS
    # -------------------------------------------------------------------------
    doc.add_page_break()
    p_ch3 = doc.add_paragraph()
    p_ch3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ch3.paragraph_format.space_before = Pt(30)
    p_ch3.paragraph_format.space_after = Pt(18)
    r = p_ch3.add_run("CHAPTER 3\nANALYSIS")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)

    add_heading2("3.1 Presentation of Bull Diagram")
    add_p(
        "The bull diagram (Figure 3.1) illustrates the comprehensive end-to-end operational flow and data transformation cycles of "
        "TalentLens. The interaction begins when an HR recruiter accesses the web dashboard to upload PDF resumes or input job criteria. "
        "Rather than forcing large binary PDF documents through API Gateway, the application requests an ephemeral S3 presigned URL from "
        "the upload handler and streams the PDF directly into an encrypted S3 bucket. Upon upload completion, S3 emits an ObjectCreated event "
        "to Amazon SQS, which buffers the task and activates the asynchronous text extraction engine. The Lambda worker initiates Amazon Textract "
        "for multi-page document text detection while maintaining a local pypdf fallback in case of cloud throttling. Extracted resume text "
        "is indexed in Amazon DynamoDB with metadata, timestamps, and candidate status. When the recruiter enters job requirements, the skill "
        "matching engine normalizes the criteria, matches skills against an 80+ canonical taxonomy with alias resolution, and returns ranked "
        "candidate profiles with quantitative match scores and explicit visual tags for matched and missing qualifications."
    )

    if os.path.exists('generated_diagrams/fig3_1_bull_diagram.png'):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        r = p_img.add_run()
        r.add_picture('generated_diagrams/fig3_1_bull_diagram.png', width=Inches(5.4))
        add_caption("Figure 3.1: Bull Diagram")

    add_heading2("3.2 Presentation of Octopus Diagram")
    add_p(
        "The octopus diagram (Figure 3.2) models the primary functional modules and architectural subsystems radiating from the central "
        "TalentLens platform core. The Resume Ingestion module coordinates presigned S3 URLs, client-side streaming, and failure reporting. "
        "The Amazon SQS & DLQ subsystem manages asynchronous queue buffering, retries, and dead-letter isolation. The Amazon Textract OCR module "
        "performs multi-page text detection with local pypdf fallback parsing. The Amazon DynamoDB data layer provides scalable single-table NoSQL "
        "storage for candidate profiles. The Keyword Skill Extraction Engine maintains an 80+ canonical skill dictionary and alias mapping. "
        "The Candidate Ranking Service executes set algebra to calculate match percentages and skill tag breakdowns. The React Interactive "
        "Dashboard delivers four dedicated viewports with automated 5-second polling. Finally, the AWS SAM Infrastructure module governs "
        "declarative infrastructure as code, least-privilege IAM policies, and HTTP API Gateway routing."
    )

    if os.path.exists('generated_diagrams/fig3_2_octopus_diagram.png'):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        r = p_img.add_run()
        r.add_picture('generated_diagrams/fig3_2_octopus_diagram.png', width=Inches(5.4))
        add_caption("Figure 3.2: Octopus Diagram")

    # -------------------------------------------------------------------------
    # CHAPTER 4: SYSTEM DESIGN – UML MODELING
    # -------------------------------------------------------------------------
    doc.add_page_break()
    p_ch4 = doc.add_paragraph()
    p_ch4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ch4.paragraph_format.space_before = Pt(30)
    p_ch4.paragraph_format.space_after = Pt(18)
    r = p_ch4.add_run("CHAPTER 4\nSYSTEM DESIGN – UML MODELING")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)

    add_heading2("4.1 System Architecture Diagram")
    add_p(
        "TalentLens follows a cloud-native, three-tier serverless architecture structured across presentation, application routing, "
        "serverless compute, and managed storage/AI tiers (Figure 4.1). The presentation tier is a React 18 single-page application "
        "executing in the recruiter's web browser, featuring components for dashboard metrics, candidate ranking, resume uploading, "
        "and job criteria configuration. The API tier is governed by Amazon API Gateway (HTTP API v2) configured with permissive CORS headers "
        "routing requests to dedicated AWS Lambda microservices (talentlens-upload, talentlens-candidates, and talentlens-match). "
        "The compute tier runs Python 3.12 in isolated execution environments with least-privilege IAM permissions. The storage and AI tier "
        "consists of an encrypted Amazon S3 private bucket, an Amazon SQS processing queue with a 14-day DLQ, Amazon Textract for OCR, "
        "and Amazon DynamoDB for candidate metadata indexing."
    )

    if os.path.exists('generated_diagrams/fig4_1_architecture_diagram.png'):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        r = p_img.add_run()
        r.add_picture('generated_diagrams/fig4_1_architecture_diagram.png', width=Inches(5.4))
        add_caption("Figure 4.1: System Architecture Diagram")

    add_heading2("4.2 Data Flow Diagram")
    add_p(
        "Figure 4.2 presents the Level 0 Context Diagram of TalentLens. The external entity is the HR Recruiter or Talent Acquisition Specialist. "
        "The recruiter sends resume PDF files, upload requests, and job criteria queries into the TalentLens system core, and receives secure S3 "
        "presigned URLs, ingestion status updates, candidate profile previews, and ranked candidate match scores with skill gap breakdowns. "
        "In parallel, the system exchanges document binaries, OCR requests, event signals, and extracted text blocks with AWS cloud services."
    )

    if os.path.exists('generated_diagrams/fig4_2_dfd_level_0.png'):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        r = p_img.add_run()
        r.add_picture('generated_diagrams/fig4_2_dfd_level_0.png', width=Inches(5.0))
        add_caption("Figure 4.2: Data Flow Diagram - Level 0 (Context Diagram)")

    add_p(
        "Figure 4.3 illustrates the Level 1 Data Flow Diagram, detailing internal process interactions across data stores. In Process 1.0 "
        "(Request Upload URL), the recruiter submits a filename; the handler validates the '.pdf' extension, initializes an 'UPLOADING' record "
        "in D1 (DynamoDB Candidates Store), and returns a presigned S3 URL. In Process 2.0 (Direct S3 Upload), the browser streams the PDF directly "
        "to D2 (S3 Resume Bucket). S3 generates an ObjectCreated event, routed by Process 3.0 (Queue Ingestion) into D3 (SQS Queue). "
        "Process 4.0 (Textract OCR & Extraction) consumes queue messages, updates D1 to 'PROCESSING', invokes Amazon Textract or fallback pypdf, "
        "parses the candidate name, and saves extracted text with status 'COMPLETED' in D1. In Process 5.0 (Fetch Candidates), the recruiter "
        "retrieves all candidate records. In Process 6.0 (Match Skills & Rank Pool), the recruiter provides job requirements; the engine "
        "scans completed candidates from D1, executes skill set intersection, and returns ranked match percentages."
    )

    if os.path.exists('generated_diagrams/fig4_3_dfd_level_1.png'):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        r = p_img.add_run()
        r.add_picture('generated_diagrams/fig4_3_dfd_level_1.png', width=Inches(5.4))
        add_caption("Figure 4.3: Data Flow Diagram - Level 1")

    add_heading2("4.3 Use Case Diagram")
    add_p(
        "Figure 4.4 illustrates the Use Case Diagram modeling the interactions between the HR Recruiter actor and the TalentLens platform. "
        "The primary use cases comprise: UC1 (Request S3 Presigned Upload URL), UC2 (Direct Upload Resume PDF to S3), UC3 (Monitor Asynchronous "
        "Processing Status), UC4 (Browse Candidate Pool & View Resume Text), UC5 (Input Job Requirements & Target Skills), UC6 (Match Candidates "
        "Against Job Description), UC7 (View Ranked Match Percentage & Skill Tags), UC8 (Inspect Candidate Details & Missing Skills), and "
        "UC9 (Inspect Cloud Architecture & AWS Diagnostics)."
    )

    if os.path.exists('generated_diagrams/fig4_4_use_case_diagram.png'):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        r = p_img.add_run()
        r.add_picture('generated_diagrams/fig4_4_use_case_diagram.png', width=Inches(5.0))
        add_caption("Figure 4.4: Use Case Diagram")

    add_heading2("4.4 Sequence Diagram")
    add_p(
        "Figure 4.5 depicts the Sequence Diagram detailing the chronological message flow during resume upload, asynchronous text extraction, "
        "and candidate listing. The React UI issues GET /api/upload?filename=cv.pdf to API Gateway, which forwards the request to the Upload Lambda. "
        "The Lambda generates a UUID v4 candidateId, creates a DynamoDB record with status 'UPLOADING', generates a 300-second presigned S3 PUT URL, "
        "and returns the payload. The React client streams the PDF directly to Amazon S3. Upon arrival, S3 emits an ObjectCreated event to SQS. "
        "The Process Resume Lambda receives the SQS trigger, updates DynamoDB status to 'PROCESSING', invokes Amazon Textract async document text "
        "detection, polls for completion, parses candidate name, and updates DynamoDB to 'COMPLETED'. The React client polls GET /api/candidates "
        "every 5 seconds, dynamically updating the candidate list upon processing completion."
    )

    if os.path.exists('generated_diagrams/fig4_5_sequence_diagram.png'):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        r = p_img.add_run()
        r.add_picture('generated_diagrams/fig4_5_sequence_diagram.png', width=Inches(5.4))
        add_caption("Figure 4.5: Sequence Diagram - Resume Upload & Text Extraction Flow")

    add_heading2("4.5 Database Design (ER Diagram)")
    add_p(
        "TalentLens implements a single-table serverless NoSQL data architecture hosted on Amazon DynamoDB (Table: TalentLensCandidates), "
        "supplemented by Amazon S3 object storage for binary files (Figure 4.6). The partition key candidateId (String, UUID v4) guarantees "
        "uniform hash partition distribution across DynamoDB storage partitions. The schema employs flexible attributes allowing sparse and "
        "nested map storage without requiring table restructuring. Table 4.1 enumerates the complete schema attributes, data types, and constraints."
    )

    add_caption("Table 4.1: DynamoDB Table Schema & Key Specifications", is_table=True)
    ddb_rows = [
        ("candidateId", "String (UUID v4)", "Partition Key (HASH)", "Primary identifier uniquely indexing candidate records"),
        ("filename", "String", "Attribute", "Original name of the uploaded PDF resume file"),
        ("s3Key", "String", "Attribute", "Object storage URI path (resumes/{candidateId}/{filename})"),
        ("status", "String", "Attribute", "Lifecycle status: UPLOADING | PROCESSING | COMPLETED | FAILED"),
        ("createdAt", "String (ISO 8601 UTC)", "Attribute", "Timestamp of initial presigned upload URL creation"),
        ("processedAt", "String (ISO 8601 UTC)", "Attribute", "Timestamp when OCR text extraction completed"),
        ("candidateName", "String", "Attribute", "Heuristically extracted candidate full name or sanitized filename"),
        ("resumeText", "String", "Attribute", "Complete OCR-extracted plain text body of the resume"),
        ("errorMessage", "String", "Attribute (Optional)", "Diagnostic error message if upload or processing failed"),
        ("jobTitle", "String", "Attribute (Optional)", "Job role title evaluated during skill matching execution"),
        ("matchResult", "Map / JSON Object", "Attribute (Optional)", "Nested structure: match_percentage, matched_skills, missing_skills"),
    ]
    t_ddb = doc.add_table(rows=len(ddb_rows)+1, cols=4)
    t_ddb.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_ddb.autofit = False
    h_row = t_ddb.rows[0]
    set_repeat_table_header(h_row)
    prevent_row_split(h_row)
    ddb_widths = [Inches(1.5), Inches(1.5), Inches(1.5), Inches(2.2)]
    for cell, title, w in zip(h_row.cells, ["Field Name", "Data Type", "Constraint", "Functional Description"], ddb_widths):
        cell.width = w
        set_cell_shading(cell, "EAECEE")
        set_cell_margins(cell, 25, 25, 50, 50)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(title)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)

    for ri, (fn, dt, con, desc) in enumerate(ddb_rows, start=1):
        row = t_ddb.rows[ri]
        prevent_row_split(row)
        for ci, (val, w) in enumerate(zip([fn, dt, con, desc], ddb_widths)):
            cell = row.cells[ci]
            cell.width = w
            set_cell_margins(cell, 16, 16, 50, 50)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)

    if os.path.exists('generated_diagrams/fig4_6_er_diagram.png'):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        r = p_img.add_run()
        r.add_picture('generated_diagrams/fig4_6_er_diagram.png', width=Inches(5.4))
        add_caption("Figure 4.6: Entity-Relationship Diagram (DynamoDB Data Model)")

    # -------------------------------------------------------------------------
    # CHAPTER 5: MODULE DESCRIPTION
    # -------------------------------------------------------------------------
    doc.add_page_break()
    p_ch5 = doc.add_paragraph()
    p_ch5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ch5.paragraph_format.space_before = Pt(30)
    p_ch5.paragraph_format.space_after = Pt(18)
    r = p_ch5.add_run("CHAPTER 5\nMODULE DESCRIPTION")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)

    add_heading2("5.1 Resume Upload & Presigned URL Module")
    add_p(
        "Implemented in backend/handlers/upload.py, this module handles presigned URL generation and client-side upload failure reporting. "
        "When an HTTP GET /api/upload request arrives with a filename query parameter, the handler validates that the filename terminates "
        "in '.pdf' (case-insensitive). It generates a random UUID v4 candidateId and formats an S3 storage key as 'resumes/{candidateId}/{filename}'. "
        "The handler uses boto3's S3 client configured with regional endpoint addressing (e.g., ap-south-1) and 's3v4' signature version to generate "
        "a presigned PUT URL with an expiration window of 300 seconds (5 minutes). Simultaneously, an initial candidate item is written to "
        "Amazon DynamoDB with status 'UPLOADING', creation timestamp, and empty resumeText. If a network disruption interrupts client-side upload, "
        "the frontend invokes POST /api/upload with candidateId and status 'FAILED', prompting the handler to record the failure reason."
    )

    add_caption("Table 5.1: REST API Endpoints Specification", is_table=True)
    api_rows = [
        ("/api/upload", "GET", "Public", "Generates S3 presigned PUT URL and creates candidate record with status 'UPLOADING'"),
        ("/api/upload", "POST", "Public", "Updates candidate record to 'FAILED' upon client-side upload interruption"),
        ("/api/candidates", "GET", "Public", "Scans and returns all candidate records sorted by createdAt desc, truncating resumeText to 200 chars"),
        ("/api/match", "POST", "Public", "Evaluates completed candidates against job requirements and returns ranked match percentages"),
    ]
    t_api = doc.add_table(rows=len(api_rows)+1, cols=4)
    t_api.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_api.autofit = False
    h_row = t_api.rows[0]
    set_repeat_table_header(h_row)
    prevent_row_split(h_row)
    api_widths = [Inches(1.5), Inches(0.9), Inches(1.0), Inches(3.3)]
    for cell, title, w in zip(h_row.cells, ["Endpoint", "Method", "Access", "Operational Purpose"], api_widths):
        cell.width = w
        set_cell_shading(cell, "EAECEE")
        set_cell_margins(cell, 25, 25, 50, 50)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(title)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)

    for ri, (ep, meth, acc, purp) in enumerate(api_rows, start=1):
        row = t_api.rows[ri]
        prevent_row_split(row)
        for ci, (val, w) in enumerate(zip([ep, meth, acc, purp], api_widths)):
            cell = row.cells[ci]
            cell.width = w
            set_cell_margins(cell, 16, 16, 50, 50)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)

    add_heading2("5.2 Asynchronous Document Ingestion & SQS Queue Module")
    add_p(
        "Defined in template.yaml, the ingestion subsystem decouples file arrival from processing execution. The Amazon S3 bucket is configured "
        "with an event notification rule triggering on 's3:ObjectCreated:*' restricted to prefix 'resumes/'. This notification publishes directly "
        "to 'talentlens-processing-queue'. A dedicated Dead-Letter Queue ('talentlens-processing-dlq') is attached with a redrive policy specifying "
        "maxReceiveCount = 3 and message retention period of 1,209,600 seconds (14 days). The processing queue enforces a VisibilityTimeout of "
        "300 seconds, guaranteeing adequate execution headroom for the downstream Lambda function (configured timeout 180 seconds, memory 512 MB)."
    )

    add_heading2("5.3 Text Extraction & Amazon Textract OCR Module")
    add_p(
        "Implemented in backend/handlers/process_resume.py, this module processes SQS messages containing S3 event notifications. It parses the S3 key "
        "to extract candidateId and filename, transitions candidate status to 'PROCESSING' in DynamoDB, and submits the PDF to Amazon Textract via "
        "StartDocumentTextDetection. It polls GetDocumentTextDetection using exponential backoff starting at 2.0s up to 10.0s until JobStatus reaches "
        "'SUCCEEDED' or 'FAILED'. For multi-page outputs, it traverses NextToken pagination, collecting text blocks of BlockType 'LINE'. "
        "Crucially, if Textract encounters service unavailability or timeout, the handler activates _extract_text_from_pdf_s3(), which downloads "
        "the raw PDF from S3 into memory and parses text lines using pypdf and stream decompression. It applies _extract_name_heuristic() across "
        "the initial 10 text lines to extract the candidate's name, updates DynamoDB status to 'COMPLETED', and stores the full extracted text."
    )

    add_caption("Table 5.2: Resume Processing Validation & Status Transitions", is_table=True)
    val_rows = [
        ("1", "File Extension Check", "Filename must end with '.pdf'", "HTTP 400 'Invalid file type. Only .pdf files are supported.'"),
        ("2", "Candidate Record Init", "UUID v4 generated, S3 key assigned", "DynamoDB Item created with status='UPLOADING'"),
        ("3", "Presigned URL Expiry", "URL valid for 300 seconds (5m)", "S3 returns HTTP 403 Access Denied if expired"),
        ("4", "Queue Ingestion Trigger", "S3 key must match resumes/*", "S3 event dropped if outside resumes/ prefix"),
        ("5", "SQS Processing Delivery", "Worker Lambda polls SQS batch", "Status transitioned to 'PROCESSING' in DynamoDB"),
        ("6", "Textract OCR Extraction", "Async StartDocumentTextDetection", "Falls back to pypdf byte-stream extraction if Textract fails"),
        ("7", "Name Heuristic Parsing", "Scans first 10 non-header lines", "Falls back to sanitized filename if no name matches"),
        ("8", "Completion Finalization", "Full text & metadata written to DDB", "Status transitioned to 'COMPLETED' in DynamoDB"),
    ]
    t_val = doc.add_table(rows=len(val_rows)+1, cols=4)
    t_val.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_val.autofit = False
    h_row = t_val.rows[0]
    set_repeat_table_header(h_row)
    prevent_row_split(h_row)
    val_widths = [Inches(0.6), Inches(1.8), Inches(2.2), Inches(2.1)]
    for cell, title, w in zip(h_row.cells, ["Step", "Validation / Check", "Operational Rule", "System Response / Action"], val_widths):
        cell.width = w
        set_cell_shading(cell, "EAECEE")
        set_cell_margins(cell, 25, 25, 50, 50)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(title)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)

    for ri, (st, chk, rule, act) in enumerate(val_rows, start=1):
        row = t_val.rows[ri]
        prevent_row_split(row)
        for ci, (val, w) in enumerate(zip([st, chk, rule, act], val_widths)):
            cell = row.cells[ci]
            cell.width = w
            set_cell_margins(cell, 16, 16, 50, 50)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)

    add_heading2("5.4 Candidate Data Access & DynamoDB Storage Module")
    add_p(
        "The data layer manages high-throughput candidate metadata storage using Amazon DynamoDB's on-demand capacity mode. In handlers/candidates.py, "
        "the listing service executes paginated table scans using ExclusiveStartKey to retrieve all candidates. For each item, it truncates resumeText "
        "to 200 characters to optimize network transfer sizes. Furthermore, it incorporates an automatic timeout detector: if any candidate remains in "
        "'UPLOADING' status for greater than 300 seconds without an S3 ObjectCreated event arriving, it automatically updates the item status to 'FAILED' "
        "with an error message 'Upload timed out or was interrupted.', ensuring stale records never freeze the user interface."
    )

    add_heading2("5.5 Keyword-Based Skill Extraction & Matching Engine Module")
    add_p(
        "Implemented in backend/shared/skill_extractor.py, this engine performs tokenization, skill detection, and match percentage scoring. "
        "It defines SKILLS_DATABASE containing over 80 canonical skill identifiers categorized into 8 domains: Programming Languages, "
        "Web Frameworks, Databases, Cloud Services, DevOps Tools, Data Science & AI, Soft Skills, and Other Tools. The ALIASES dictionary "
        "maps variations, abbreviations, and informal acronyms to their canonical counterparts (e.g., 'K8s' -> 'kubernetes', 'JS' -> 'javascript', "
        "'py' -> 'python', 'FastAPI' -> 'fastapi', 'AWS' -> 'amazon web services'). The normalize_text() function converts text to lowercase, "
        "preserves critical programming symbols (+, #, ., - for C++, C#, .NET, Node.js), and consolidates whitespace. In match_skills(), "
        "it calculates the mathematical set intersection between resume skills and required skills, computing: "
        "Match Percentage = (|Matched Skills| / |Required Skills|) * 100."
    )

    add_caption("Table 5.3: Canonical Skill Taxonomy & Aliases Mapping", is_table=True)
    tax_rows = [
        ("Programming Languages", "Python, JavaScript, TypeScript, Java, C++, C#, Golang, Rust, SQL", "py->python, js->javascript, ts->typescript, cpp->c++, csharp->c#"),
        ("Web Frameworks", "React, Angular, Vue, Next.js, Node.js, Express, Django, Flask, FastAPI", "reactjs->react, nextjs->next.js, nodejs->node.js, expressjs->express"),
        ("Databases", "PostgreSQL, MySQL, MongoDB, DynamoDB, Redis, Elasticsearch, Cassandra", "postgres->postgresql, mongo->mongodb, elastic search->elasticsearch"),
        ("Cloud Services", "Amazon Web Services, AWS Lambda, AWS S3, AWS DynamoDB, AWS SQS, AWS Textract", "aws->amazon web services, lambda->aws lambda, s3->aws s3, sqs->aws sqs"),
        ("DevOps & Containers", "Docker, Kubernetes, Jenkins, Git, GitHub Actions, GitLab CI, Ansible, Nginx", "k8s->kubernetes, actions->github actions, compose->docker compose"),
        ("Data Science & AI", "Machine Learning, Deep Learning, Artificial Intelligence, TensorFlow, PyTorch", "ml->machine learning, dl->deep learning, ai->artificial intelligence"),
        ("Soft Skills", "Communication, Leadership, Teamwork, Problem Solving, Agile, Scrum", "collaboration->teamwork, critical thinking->problem solving"),
        ("Tools & Protocols", "REST API, GraphQL, gRPC, Microservices, Linux, Jira, Postman, Vite, Tailwind CSS", "restful api->rest api, tailwind->tailwind css"),
    ]
    t_tax = doc.add_table(rows=len(tax_rows)+1, cols=3)
    t_tax.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_tax.autofit = False
    h_row = t_tax.rows[0]
    set_repeat_table_header(h_row)
    prevent_row_split(h_row)
    tax_widths = [Inches(1.8), Inches(2.5), Inches(2.4)]
    for cell, title, w in zip(h_row.cells, ["Skill Category", "Canonical Skill Keywords", "Supported Shorthand Aliases"], tax_widths):
        cell.width = w
        set_cell_shading(cell, "EAECEE")
        set_cell_margins(cell, 25, 25, 50, 50)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(title)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)

    for ri, (cat, can, ali) in enumerate(tax_rows, start=1):
        row = t_tax.rows[ri]
        prevent_row_split(row)
        for ci, (val, w) in enumerate(zip([cat, can, ali], tax_widths)):
            cell = row.cells[ci]
            cell.width = w
            set_cell_margins(cell, 16, 16, 50, 50)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)

    add_heading2("5.6 Candidate Retrieval & Ranking API Module")
    add_p(
        "Implemented in backend/handlers/match.py, this module handles POST /api/match requests. It parses requirements and optional candidateIds "
        "from the JSON payload. If specific candidate IDs are provided, it performs a batched lookup using DynamoDB batch_get_item (chunked into "
        "groups of 100); otherwise, it scans the table for all candidates with status 'COMPLETED'. It executes match_skills() for each candidate's "
        "full resumeText, attaches the resulting matchResult, and sorts the returned candidate array descending by match_percentage."
    )

    add_heading2("5.7 Frontend Routing, Dashboard & Real-Time Polling Module")
    add_p(
        "The React 18 single-page application (frontend/src/App.jsx) organizes candidate evaluation into four tabbed views (Table 5.4). "
        "The central App component maintains candidate state, active job match parameters, and an automatic 5-second polling interval (via setInterval) "
        "that remains active as long as any candidate holds status 'UPLOADING' or 'PROCESSING'. In frontend/src/api/api.js, fetch requests communicate "
        "with backend endpoints and transform backend snake_case keys (match_percentage, matched_skills) into camelCase properties used by React components. "
        "The UI incorporates modal inspection (CandidateDetailModal.jsx) and cloud architecture diagnostics (CloudArchitecture.jsx)."
    )

    add_caption("Table 5.4: Frontend Views & Navigation Architecture", is_table=True)
    view_rows = [
        ("Dashboard Overview", "tab-overview", "Executive KPI cards, pipeline summary, cloud architecture banner, recent uploads"),
        ("Candidate Pool", "tab-candidates", "Full candidate leaderboard, status badges, match % rankings, matched/missing skill tags"),
        ("Job Requirements", "tab-requirements", "Interactive form for entering job title, criteria, and executing skill matching"),
        ("Resume Upload", "tab-upload", "Drag-and-drop PDF dropzone, presigned S3 upload execution, and ingestion history table"),
        ("Candidate Detail Modal", "Modal Overlay", "Full extracted resume text viewer, candidate metadata, and complete skill breakdown"),
    ]
    t_vw = doc.add_table(rows=len(view_rows)+1, cols=3)
    t_vw.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_vw.autofit = False
    h_row = t_vw.rows[0]
    set_repeat_table_header(h_row)
    prevent_row_split(h_row)
    vw_widths = [Inches(1.8), Inches(1.5), Inches(3.4)]
    for cell, title, w in zip(h_row.cells, ["View Component", "Tab Identifier", "Functional Description & Rendered Elements"], vw_widths):
        cell.width = w
        set_cell_shading(cell, "EAECEE")
        set_cell_margins(cell, 25, 25, 50, 50)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(title)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)

    for ri, (v_name, v_id, v_desc) in enumerate(view_rows, start=1):
        row = t_vw.rows[ri]
        prevent_row_split(row)
        for ci, (val, w) in enumerate(zip([v_name, v_id, v_desc], vw_widths)):
            cell = row.cells[ci]
            cell.width = w
            set_cell_margins(cell, 16, 16, 50, 50)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)

    add_heading2("5.8 Serverless Infrastructure & SAM Deployment Module")
    add_p(
        "The entire cloud infrastructure is defined declaratively in backend/template.yaml using the AWS Serverless Application Model (SAM). "
        "Global function settings specify Python 3.12 runtime, x86_64 architecture, 256 MB base memory, and 30-second timeouts. The template "
        "defines four Lambda functions, an HTTP API Gateway with CORS configuration, an S3 bucket with CORS and notification rules, "
        "two SQS queues, and the DynamoDB table with PAY_PER_REQUEST billing. Deployment is executed deterministically with 'sam build' and 'sam deploy'."
    )

    # -------------------------------------------------------------------------
    # CHAPTER 6: CONCLUSION
    # -------------------------------------------------------------------------
    doc.add_page_break()
    p_ch6 = doc.add_paragraph()
    p_ch6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ch6.paragraph_format.space_before = Pt(30)
    p_ch6.paragraph_format.space_after = Pt(18)
    r = p_ch6.add_run("CHAPTER 6\nCONCLUSION")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)

    add_p(
        "The TalentLens AI-powered resume screening and skill matching platform was successfully engineered, tested, and demonstrated. "
        "The project demonstrates how modern cloud-native serverless primitives (AWS Lambda, Amazon S3, SQS, DynamoDB, and Amazon Textract) "
        "can be synthesized into an ultra-scalable, zero-maintenance recruitment automation engine. By utilizing presigned S3 URLs, the system "
        "completely eliminates API Gateway binary payload bottlenecks, while SQS decoupling ensures that sudden surges in resume submissions "
        "never compromise server stability. The multi-tier OCR pipeline extracts high-fidelity text across diverse document layouts, and the "
        "keyword-based skill extraction engine delivers objective, bias-free candidate rankings with sub-second execution speeds."
    )
    add_p(
        "Rigorous automated testing was conducted across both backend and frontend layers to verify functional compliance, edge case handling, "
        "and algorithmic precision. The backend test suite (Python 3.12 with PyTest 8.3.4) executed 39 unit and integration test cases across "
        "tests/test_skill_extractor.py (19 tests), tests/test_match.py (8 tests), and tests/test_upload.py (12 tests) using mocked AWS services. "
        "All 39 backend tests passed with 100% success in 1.11 seconds. The frontend test suite (Node.js with Vitest 2.1.9 and React Testing Library) "
        "executed 17 unit and component test cases across __tests__/skillMatcher.test.js (10 tests), __tests__/CloudArchitecture.test.jsx (3 tests), "
        "and __tests__/App.test.jsx (4 tests). All 17 frontend tests passed with 100% success. In total, the project achieved 56 automated test passes "
        "with zero failures, verifying complete software integrity."
    )
    add_p(
        "Verification Note on Project Documentation Mismatches: During verification of the codebase against the project's documentation, "
        "three minor mismatches were identified: (1) The README file lists 38 backend tests (19+6+13), whereas the actual test suite executes 39 tests; "
        "(2) The README lists 12 frontend tests, whereas the actual test suite executes 17 tests; and (3) README documentation examples mention "
        "us-east-1, whereas the active code defaults to ap-south-1 (Mumbai). The report reflects the verified source code behavior."
    )

    add_heading2("Limitations")
    add_bullet("Cold Start Latency: Infrequently invoked Lambda functions and Amazon Textract asynchronous jobs can experience initial cold start delays of 3 to 8 seconds during the first document ingestion.")
    add_bullet("Exact Keyword Matching versus Semantic Context: The skill matching engine relies on dictionary tokenization and alias resolution; it does not evaluate semantic seniority or deep contextual nuance.")
    add_bullet("Language Restriction: The skill extraction taxonomy and Textract document detection models are currently optimized for English-language resumes and standard Latin character sets.")
    add_bullet("File Format Constraint: Ingestion is currently restricted to PDF documents; other common formats like Microsoft Word (.docx) or OpenDocument (.odt) require pre-conversion.")

    add_heading2("Future Enhancements")
    add_bullet("Vector Embeddings & Semantic Search: Integrating Amazon Bedrock (Titan or Claude models) and Amazon OpenSearch Serverless to generate dense vector embeddings of resumes, enabling semantic matching beyond keyword boundaries.")
    add_bullet("Multi-Format Document Ingestion: Adding native support for Word (.docx), plain text (.txt), and scanned image formats (.png, .tiff) using Textract AnalyzeDocument features.")
    add_bullet("Recruiter Role-Based Authentication: Implementing Amazon Cognito user pools to provide role-based authentication, multi-tenant recruiter isolation, and candidate confidentiality controls.")
    add_bullet("Automated Candidate Communication: Integrating Amazon SES (Simple Email Service) to automatically transmit personalized status updates, interview invitations, or feedback to evaluated candidates.")
    add_bullet("Exportable Candidate Dossiers: Generating downloadable PDF or CSV candidate evaluation summaries for talent acquisition review meetings.")

    # -------------------------------------------------------------------------
    # CHAPTER 7: REFERENCES
    # -------------------------------------------------------------------------
    doc.add_page_break()
    p_ch7 = doc.add_paragraph()
    p_ch7.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ch7.paragraph_format.space_before = Pt(30)
    p_ch7.paragraph_format.space_after = Pt(18)
    r = p_ch7.add_run("CHAPTER 7\nREFERENCES")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)

    refs = [
        "Roger S. Pressman and Bruce R. Maxim, Software Engineering: A Practitioner’s Approach, 9th Edition, McGraw-Hill Education, 2020.",
        "Ian Sommerville, Software Engineering, 10th Edition, Pearson Education, 2016.",
        "Roy T. Fielding, Architectural Styles and the Design of Network-based Software Architectures (Doctoral dissertation, REST), University of California, Irvine, 2000.",
        "Julian Wood, James Beswick, and Eric Johnson, Serverless Architectures on AWS, 2nd Edition, Manning Publications, 2022.",
        "Amazon Web Services, AWS Serverless Application Model (SAM) Developer Guide. https://docs.aws.amazon.com/serverless-application-model/",
        "Amazon Web Services, Amazon Textract Developer Guide and API Reference. https://docs.aws.amazon.com/textract/",
        "Amazon Web Services, Amazon DynamoDB Developer Guide. https://docs.aws.amazon.com/amazondynamodb/",
        "Amazon Web Services, Amazon Simple Queue Service (SQS) Documentation. https://docs.aws.amazon.com/sqs/",
        "Amazon Web Services, Amazon Simple Storage Service (S3) Documentation. https://docs.aws.amazon.com/s3/",
        "React Official Documentation – React 18 Architecture and Hooks. https://react.dev/",
        "Vite Official Documentation – Next Generation Frontend Tooling. https://vite.dev/",
        "R. Fielding, M. Nottingham, and J. Reschke, RFC 9110 – HTTP Semantics. https://www.rfc-editor.org/rfc/rfc9110",
        "P. Leach, M. Mealling, and R. Salz, RFC 4122 – A Universally Unique IDentifier (UUID) URN Namespace. https://www.rfc-editor.org/rfc/rfc4122",
        "MDN Web Docs – Web APIs, Fetch API, and Asynchronous JavaScript. https://developer.mozilla.org/",
    ]

    for idx, ref_text in enumerate(refs, start=1):
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.space_after = Pt(6)
        p_ref.paragraph_format.line_spacing = 1.3
        p_ref.paragraph_format.left_indent = Inches(0.4)
        p_ref.paragraph_format.first_line_indent = Inches(-0.4)
        r_num = p_ref.add_run(f"{idx}.  ")
        r_num.bold = True
        r_num.font.name = 'Times New Roman'
        r_num.font.size = Pt(11)
        r_txt = p_ref.add_run(ref_text)
        r_txt.font.name = 'Times New Roman'
        r_txt.font.size = Pt(11)

    # -------------------------------------------------------------------------
    # CHAPTER 8: APPENDICES
    # -------------------------------------------------------------------------
    doc.add_page_break()
    p_ch8 = doc.add_paragraph()
    p_ch8.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ch8.paragraph_format.space_before = Pt(30)
    p_ch8.paragraph_format.space_after = Pt(18)
    r = p_ch8.add_run("CHAPTER 8\nAPPENDICES")
    r.bold = True
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)

    add_heading2("8.1 Code")
    add_p(
        "The source code of TalentLens is organized across serverless AWS Lambda microservices, shared domain libraries, "
        "declarative infrastructure-as-code definitions, and a modular React frontend single-page application. The core files "
        "implementing the presigned upload generation, asynchronous SQS ingestion, Textract OCR parsing, candidate matching engine, "
        "and client dashboard are detailed in Table 8.1 and printed in the subsequent subsections; additional development scripts, "
        "test suites, and CSS stylesheets are located in the submitted project directory."
    )

    add_caption("Table 8.1: Core Source Code Modules & File Catalog", is_table=True)
    code_files_catalog = [
        ("8.1.1", "backend/template.yaml", "AWS SAM template defining S3, SQS, DLQ, DynamoDB, API Gateway, and Lambda functions"),
        ("8.1.2", "backend/handlers/upload.py", "Lambda handler generating S3 presigned PUT URLs and tracking candidate upload statuses"),
        ("8.1.3", "backend/handlers/process_resume.py", "SQS worker Lambda executing Amazon Textract OCR with local pypdf fallback"),
        ("8.1.4", "backend/handlers/match.py", "Lambda handler matching candidate resumes against job criteria and ranking candidates"),
        ("8.1.5", "backend/handlers/candidates.py", "Lambda handler scanning DynamoDB, paginating candidates, and handling upload timeouts"),
        ("8.1.6", "backend/shared/skill_extractor.py", "Canonical skill database (80+ skills), alias dictionary, normalizer, and matcher"),
        ("8.1.7", "backend/shared/response.py", "Standardized API Gateway proxy response helpers with CORS headers and Decimal encoder"),
        ("8.1.8", "frontend/src/App.jsx", "Root React component managing view tabs, candidate states, polling, and modal overlays"),
        ("8.1.9", "frontend/src/api/api.js", "Frontend API client interfacing with backend endpoints and transforming data schemas"),
        ("8.1.10", "frontend/src/utils/skillMatcher.js", "Client-side skill matching and text extraction utility for offline previewing"),
    ]

    t_cat = doc.add_table(rows=len(code_files_catalog)+1, cols=3)
    t_cat.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_cat.autofit = False
    h_row = t_cat.rows[0]
    set_repeat_table_header(h_row)
    prevent_row_split(h_row)
    cat_widths = [Inches(1.0), Inches(2.5), Inches(3.2)]
    for cell, title, w in zip(h_row.cells, ["No.", "File Path", "Functional Architectural Purpose"], cat_widths):
        cell.width = w
        set_cell_shading(cell, "EAECEE")
        set_cell_margins(cell, 25, 25, 50, 50)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(title)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)

    for ri, (c_no, c_fp, c_purp) in enumerate(code_files_catalog, start=1):
        row = t_cat.rows[ri]
        prevent_row_split(row)
        for ci, (val, w) in enumerate(zip([c_no, c_fp, c_purp], cat_widths)):
            cell = row.cells[ci]
            cell.width = w
            set_cell_margins(cell, 16, 16, 50, 50)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)

    def print_code_box(sub_no, title, filepath, desc, code_content):
        p_head = doc.add_paragraph()
        p_head.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_head.paragraph_format.space_before = Pt(8)
        p_head.paragraph_format.space_after = Pt(2)
        p_head.paragraph_format.keep_with_next = True
        r1 = p_head.add_run(f"{sub_no} {title} ")
        r1.bold = True
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(10.5)
        r2 = p_head.add_run(f"({filepath})")
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(10)

        p_desc = doc.add_paragraph()
        p_desc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_desc.paragraph_format.space_after = Pt(3)
        p_desc.paragraph_format.keep_with_next = True
        r = p_desc.add_run(desc)
        r.italic = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9.5)

        t_code = doc.add_table(rows=1, cols=1)
        t_code.alignment = WD_TABLE_ALIGNMENT.CENTER
        t_code.autofit = False
        row = t_code.rows[0]
        prevent_row_split(row)
        cell = row.cells[0]
        cell.width = Inches(6.7)
        set_cell_shading(cell, "F8F9FA")
        set_cell_borders(cell,
                         top={'val': 'single', 'sz': '4', 'color': 'D0D3D4'},
                         bottom={'val': 'single', 'sz': '4', 'color': 'D0D3D4'},
                         left={'val': 'single', 'sz': '4', 'color': 'D0D3D4'},
                         right={'val': 'single', 'sz': '4', 'color': 'D0D3D4'})
        set_cell_margins(cell, 35, 35, 50, 50)
        p_c = cell.paragraphs[0]
        p_c.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_c.paragraph_format.line_spacing = 1.0
        p_c.paragraph_format.space_after = Pt(0)
        r_c = p_c.add_run(code_content.strip())
        r_c.font.name = 'Consolas'
        r_c.font.size = Pt(7.5)
        r_c.font.color.rgb = RGBColor(30, 30, 30)

    def get_file_content(path, max_lines=46):
        if not os.path.exists(path): return "# File not found"
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        if len(lines) <= max_lines:
            return "".join(lines)
        return "".join(lines[:max_lines]) + f"\n# ... [Remaining {len(lines)-max_lines} lines omitted for brevity; see project repository] ..."

    print_code_box("8.1.1", "template.yaml", "backend/template.yaml",
                   "AWS SAM infrastructure template defining resources, S3 events, SQS redrive policies, and IAM permissions.",
                   get_file_content("backend/template.yaml", 46))
    print_code_box("8.1.2", "upload.py", "backend/handlers/upload.py",
                   "AWS Lambda upload handler managing S3 presigned PUT URLs, validation, and DynamoDB initialization.",
                   get_file_content("backend/handlers/upload.py", 46))
    print_code_box("8.1.3", "process_resume.py", "backend/handlers/process_resume.py",
                   "SQS-triggered Lambda function executing Amazon Textract multi-page OCR and local pypdf fallback extraction.",
                   get_file_content("backend/handlers/process_resume.py", 48))
    print_code_box("8.1.4", "match.py", "backend/handlers/match.py",
                   "AWS Lambda matching handler ranking candidates against job criteria using set intersection.",
                   get_file_content("backend/handlers/match.py", 46))
    print_code_box("8.1.5", "candidates.py", "backend/handlers/candidates.py",
                   "AWS Lambda listing handler scanning DynamoDB, paginating candidates, and handling upload timeouts.",
                   get_file_content("backend/handlers/candidates.py", 46))
    print_code_box("8.1.6", "skill_extractor.py", "backend/shared/skill_extractor.py",
                   "Domain skill extraction engine with 80+ canonical skills, alias normalization, and match percentage scoring.",
                   get_file_content("backend/shared/skill_extractor.py", 48))
    print_code_box("8.1.7", "response.py", "backend/shared/response.py",
                   "API Gateway proxy response utilities incorporating CORS headers and custom Decimal JSON serialization.",
                   get_file_content("backend/shared/response.py", 46))
    print_code_box("8.1.8", "App.jsx", "frontend/src/App.jsx",
                   "Root React 18 component orchestrating view navigation, candidate pipeline state, and 5-second automatic polling.",
                   get_file_content("frontend/src/App.jsx", 46))
    print_code_box("8.1.9", "api.js", "frontend/src/api/api.js",
                   "Frontend API client managing HTTP requests, presigned URL retrieval, and schema key transformation.",
                   get_file_content("frontend/src/api/api.js", 46))
    print_code_box("8.1.10", "skillMatcher.js", "frontend/src/utils/skillMatcher.js",
                   "Client-side skill matching utility providing synchronous offline skill extraction in the browser.",
                   get_file_content("frontend/src/utils/skillMatcher.js", 46))

    # -------------------------------------------------------------------------
    # 8.2 SCREENSHOTS
    # -------------------------------------------------------------------------
    doc.add_page_break()
    add_heading2("8.2 Screenshots")
    add_p(
        "The following screenshots were captured directly from the live, running TalentLens application operating locally with "
        "the mock backend API server and Vite development frontend. Each figure is accompanied by a formal caption and a detailed "
        "one-line operational description explaining the system behavior, rendered UI components, and recruiter workflows."
    )

    screenshots_catalog = [
        ("8.1", "Dashboard Overview & Pipeline Health", "screenshots/fig8_1_dashboard_overview.png",
         "Figure 8.1 shows the executive dashboard overview with KPI metric cards (Total Resumes: 8, Ready for Match: 6, Ready Rate: 75%), "
         "the active AWS pipeline indicator, quick navigation shortcuts, and the recent candidate activity stream."),
        ("8.2", "Cloud Architecture Interactive View", "screenshots/fig8_2_cloud_architecture.png",
         "Figure 8.2 shows the integrated cloud architecture view detailing the serverless event flow from S3 direct upload through SQS queues, "
         "Amazon Textract document text detection, DynamoDB indexing, and candidate ranking."),
        ("8.3", "Candidate Pool & Pipeline Status Badges", "screenshots/fig8_3_candidate_pool.png",
         "Figure 8.3 shows the candidate pool view displaying candidate cards with color-coded status badges (COMPLETED in green, "
         "PROCESSING in amber, and UPLOADING in blue), extracted candidate names, and action buttons."),
        ("8.4", "Job Requirements & Criteria Configuration", "screenshots/fig8_4_job_requirements.png",
         "Figure 8.4 shows the job requirements configuration interface where the recruiter inputs target job titles, pastes job descriptions, "
         "selects criteria presets, and triggers the automated skill matching engine."),
        ("8.5", "Ranked Candidates & Dynamic Skill Match Scores", "screenshots/fig8_5_ranked_results.png",
         "Figure 8.5 shows the candidate leaderboard ranked by match percentage descending following job requirements matching, "
         "featuring visual skill tags highlighting matched competencies in green and missing skill gaps in red."),
        ("8.6", "Candidate Inspection Modal & Extracted Resume Text", "screenshots/fig8_6_candidate_modal.png",
         "Figure 8.6 shows the candidate inspection modal displaying the full OCR-extracted resume text body, candidate metadata, "
         "ingestion timestamps, and categorized skill qualifications."),
        ("8.7", "Resume Upload Interface & S3 Ingestion History", "screenshots/fig8_7_resume_upload.png",
         "Figure 8.7 shows the resume upload dropzone supporting PDF drag-and-drop, direct-to-S3 binary streaming via presigned URLs, "
         "and the candidate ingestion history table."),
        ("8.8", "Candidate Tabular View with Status Badges", "screenshots/fig8_8_candidate_table.png",
         "Figure 8.8 shows the candidate pool in structured tabular view with sortable columns for candidate ID, full name, filename, "
         "status badge, creation date, and inspection action triggers."),
    ]

    for f_num, f_title, f_path, f_desc in screenshots_catalog:
        if os.path.exists(f_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(6)
            p_img.paragraph_format.space_after = Pt(2)
            p_img.paragraph_format.keep_with_next = True
            r = p_img.add_run()
            r.add_picture(f_path, width=Inches(4.6))

            add_caption(f"Figure {f_num}: {f_title}")
            add_p(f_desc, space_after=6, line_spacing=1.2)

    doc.save(docx_path)
    print(f"Generated {docx_path}")

def run_two_pass_build():
    docx_file = "TalentLens_Mini_Project_Report.docx"
    pdf_file = "TalentLens_Mini_Project_Report.pdf"

    print("=== PASS 1: Building initial DOCX ===")
    generate_document(docx_file)

    print("=== PASS 1: Converting to PDF via Word COM ===")
    abs_docx = os.path.abspath(docx_file)
    abs_pdf = os.path.abspath(pdf_file)
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(abs_docx)
        doc.SaveAs(abs_pdf, FileFormat=17)
        doc.Close()
    finally:
        word.Quit()

    print("=== PASS 1: Inspecting PDF page numbers ===")
    reader = pypdf.PdfReader(pdf_file)
    total_pages = len(reader.pages)
    print(f"Total pages in Pass 1 PDF: {total_pages}")

    arabic_start_idx = None
    for i in range(total_pages):
        text = reader.pages[i].extract_text() or ""
        if "CHAPTER 1" in text and "INTRODUCTION" in text:
            arabic_start_idx = i
            print(f"Chapter 1 detected at PDF physical page {i+1} (Arabic page 1)")
            break

    if arabic_start_idx is None:
        arabic_start_idx = 8

    page_map = {}
    for i in range(arabic_start_idx, total_pages):
        page_num = i - arabic_start_idx + 1
        text = reader.pages[i].extract_text() or ""

        if "CHAPTER 1" in text and "INTRODUCTION" in text and "ch1" not in page_map:
            page_map["ch1"] = str(page_num)
        if "1.1 Problem Statement" in text and "ch1_1" not in page_map:
            page_map["ch1_1"] = str(page_num)
        if "1.2 Objectives" in text and "ch1_2" not in page_map:
            page_map["ch1_2"] = str(page_num)
        if "1.3 Software Engineering" in text and "ch1_3" not in page_map:
            page_map["ch1_3"] = str(page_num)

        if "CHAPTER 2" in text and "REQUIREMENTS" in text and "ch2" not in page_map:
            page_map["ch2"] = str(page_num)
        if "2.1 Functional Requirements" in text and "ch2_1" not in page_map:
            page_map["ch2_1"] = str(page_num)
        if "2.2 Non-Functional Requirements" in text and "ch2_2" not in page_map:
            page_map["ch2_2"] = str(page_num)
        if "2.3 Hardware and Software" in text and "ch2_3" not in page_map:
            page_map["ch2_3"] = str(page_num)
        if "Table 2.1" in text and "tbl_2_1" not in page_map:
            page_map["tbl_2_1"] = str(page_num)
        if "Table 2.2" in text and "tbl_2_2" not in page_map:
            page_map["tbl_2_2"] = str(page_num)

        if "CHAPTER 3" in text and "ANALYSIS" in text and "ch3" not in page_map:
            page_map["ch3"] = str(page_num)
        if "3.1 Presentation of Bull" in text and "ch3_1" not in page_map:
            page_map["ch3_1"] = str(page_num)
        if "Figure 3.1" in text and "fig_3_1" not in page_map:
            page_map["fig_3_1"] = str(page_num)
        if "3.2 Presentation of Octopus" in text and "ch3_2" not in page_map:
            page_map["ch3_2"] = str(page_num)
        if "Figure 3.2" in text and "fig_3_2" not in page_map:
            page_map["fig_3_2"] = str(page_num)

        if "CHAPTER 4" in text and "SYSTEM DESIGN" in text and "ch4" not in page_map:
            page_map["ch4"] = str(page_num)
        if "4.1 System Architecture" in text and "ch4_1" not in page_map:
            page_map["ch4_1"] = str(page_num)
        if "Figure 4.1" in text and "fig_4_1" not in page_map:
            page_map["fig_4_1"] = str(page_num)
        if "4.2 Data Flow Diagram" in text and "ch4_2" not in page_map:
            page_map["ch4_2"] = str(page_num)
        if "Figure 4.2" in text and "fig_4_2" not in page_map:
            page_map["fig_4_2"] = str(page_num)
        if "Figure 4.3" in text and "fig_4_3" not in page_map:
            page_map["fig_4_3"] = str(page_num)
        if "4.3 Use Case Diagram" in text and "ch4_3" not in page_map:
            page_map["ch4_3"] = str(page_num)
        if "Figure 4.4" in text and "fig_4_4" not in page_map:
            page_map["fig_4_4"] = str(page_num)
        if "4.4 Sequence Diagram" in text and "ch4_4" not in page_map:
            page_map["ch4_4"] = str(page_num)
        if "Figure 4.5" in text and "fig_4_5" not in page_map:
            page_map["fig_4_5"] = str(page_num)
        if "4.5 Database Design" in text and "ch4_5" not in page_map:
            page_map["ch4_5"] = str(page_num)
        if "Table 4.1" in text and "tbl_4_1" not in page_map:
            page_map["tbl_4_1"] = str(page_num)
        if "Figure 4.6" in text and "fig_4_6" not in page_map:
            page_map["fig_4_6"] = str(page_num)

        if "CHAPTER 5" in text and "MODULE DESCRIPTION" in text and "ch5" not in page_map:
            page_map["ch5"] = str(page_num)
        if "5.1 Resume Upload" in text and "ch5_1" not in page_map:
            page_map["ch5_1"] = str(page_num)
        if "Table 5.1" in text and "tbl_5_1" not in page_map:
            page_map["tbl_5_1"] = str(page_num)
        if "5.2 Asynchronous Document Ingestion" in text and "ch5_2" not in page_map:
            page_map["ch5_2"] = str(page_num)
        if "5.3 Text Extraction" in text and "ch5_3" not in page_map:
            page_map["ch5_3"] = str(page_num)
        if "Table 5.2" in text and "tbl_5_2" not in page_map:
            page_map["tbl_5_2"] = str(page_num)
        if "5.4 Candidate Data Access" in text and "ch5_4" not in page_map:
            page_map["ch5_4"] = str(page_num)
        if "5.5 Keyword-Based Skill Extraction" in text and "ch5_5" not in page_map:
            page_map["ch5_5"] = str(page_num)
        if "Table 5.3" in text and "tbl_5_3" not in page_map:
            page_map["tbl_5_3"] = str(page_num)
        if "5.6 Candidate Retrieval" in text and "ch5_6" not in page_map:
            page_map["ch5_6"] = str(page_num)
        if "5.7 Frontend Routing" in text and "ch5_7" not in page_map:
            page_map["ch5_7"] = str(page_num)
        if "Table 5.4" in text and "tbl_5_4" not in page_map:
            page_map["tbl_5_4"] = str(page_num)
        if "5.8 Serverless Infrastructure" in text and "ch5_8" not in page_map:
            page_map["ch5_8"] = str(page_num)

        if "CHAPTER 6" in text and "CONCLUSION" in text and "ch6" not in page_map:
            page_map["ch6"] = str(page_num)

        if "CHAPTER 7" in text and "REFERENCES" in text and "ch7" not in page_map:
            page_map["ch7"] = str(page_num)

        if "CHAPTER 8" in text and "APPENDICES" in text and "ch8" not in page_map:
            page_map["ch8"] = str(page_num)
        if "8.1 Code" in text and "ch8_1" not in page_map:
            page_map["ch8_1"] = str(page_num)
        if "Table 8.1" in text and "tbl_8_1" not in page_map:
            page_map["tbl_8_1"] = str(page_num)

        if "8.2 Screenshots" in text and "ch8_2" not in page_map:
            page_map["ch8_2"] = str(page_num)
        if "Figure 8.1" in text and "fig_8_1" not in page_map:
            page_map["fig_8_1"] = str(page_num)
        if "Figure 8.2" in text and "fig_8_2" not in page_map:
            page_map["fig_8_2"] = str(page_num)
        if "Figure 8.3" in text and "fig_8_3" not in page_map:
            page_map["fig_8_3"] = str(page_num)
        if "Figure 8.4" in text and "fig_8_4" not in page_map:
            page_map["fig_8_4"] = str(page_num)
        if "Figure 8.5" in text and "fig_8_5" not in page_map:
            page_map["fig_8_5"] = str(page_num)
        if "Figure 8.6" in text and "fig_8_6" not in page_map:
            page_map["fig_8_6"] = str(page_num)
        if "Figure 8.7" in text and "fig_8_7" not in page_map:
            page_map["fig_8_7"] = str(page_num)
        if "Figure 8.8" in text and "fig_8_8" not in page_map:
            page_map["fig_8_8"] = str(page_num)

    print("=== PASS 2: Rebuilding DOCX with exact page numbers ===")
    generate_document(docx_file, page_map)

    print("=== PASS 2: Final PDF Conversion ===")
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(abs_docx)
        doc.SaveAs(abs_pdf, FileFormat=17)
        doc.Close()
    finally:
        word.Quit()

    reader_final = pypdf.PdfReader(pdf_file)
    print(f"\n==========================================")
    print(f"FINAL REPORT READY!")
    print(f"DOCX: {abs_docx} ({os.path.getsize(abs_docx)} bytes)")
    print(f"PDF:  {abs_pdf} ({os.path.getsize(abs_pdf)} bytes)")
    print(f"Total Pages: {len(reader_final.pages)}")
    print(f"==========================================")

if __name__ == '__main__':
    run_two_pass_build()
