import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs('generated_diagrams', exist_ok=True)
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'

def save_fig(fig, filename):
    path = os.path.join('generated_diagrams', filename)
    fig.savefig(path, dpi=300, bbox_inches='tight', pad_inches=0.15)
    plt.close(fig)
    print(f"Generated {filename}")

# ==========================================
# 1. Figure 3.1: Bull Diagram
# ==========================================
def draw_bull_diagram():
    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Styles
    box_blue = dict(boxstyle="round,pad=0.6,rounding_size=0.3", fc="#E3F2FD", ec="#1976D2", lw=1.5)
    box_green = dict(boxstyle="round,pad=0.6,rounding_size=0.3", fc="#E8F5E9", ec="#388E3C", lw=1.5)
    box_orange = dict(boxstyle="round,pad=0.6,rounding_size=0.3", fc="#FFF3E0", ec="#F57C00", lw=1.5)
    box_purple = dict(boxstyle="round,pad=0.6,rounding_size=0.3", fc="#F3E5F5", ec="#7B1FA2", lw=1.5)
    box_gray = dict(boxstyle="round,pad=0.6,rounding_size=0.3", fc="#ECEFF1", ec="#455A64", lw=1.5)

    # Nodes
    # Recruiter
    ax.text(25, 88, "Recruiter / HR User\n• Uploads PDF resumes\n• Inputs job description & criteria", ha='center', va='center', bbox=box_blue, fontsize=9.5)
    # Admin / System
    ax.text(75, 88, "AWS Infrastructure\n• Serverless Event Triggering\n• S3 Event -> SQS Queue", ha='center', va='center', bbox=box_green, fontsize=9.5)

    # Web Dashboard
    ax.text(25, 66, "React Web Dashboard\n• Direct S3 Upload (Presigned URL)\n• Dynamic Job Criteria Input\n• Real-time Polling & Candidate View", ha='center', va='center', bbox=box_purple, fontsize=9.5)
    # Storage / DB
    ax.text(75, 66, "Amazon S3 & DynamoDB\n• S3: Secure PDF Resume Storage\n• DynamoDB: Candidate Table\n(Status, Extracted Text, Timestamps)", ha='center', va='center', bbox=box_orange, fontsize=9.5)

    # Central Core: Processing & Matching
    ax.text(50, 42, "Textract OCR & Skill Extraction Engine\n• Amazon Textract: Multi-page Async Document Text Detection\n• Fallback Engine: pypdf & Raw Stream Extraction\n• Skill Engine: 80+ Canonical Skills, Aliases & Heuristic Parsing", ha='center', va='center', bbox=box_blue, fontsize=10, weight='bold')

    # Output decisions
    ax.text(18, 16, "Ranked Match Results\n• Match Percentage (0-100%)\n• Matched Skills (Green Tags)\n• Missing Skills (Red Tags)", ha='center', va='center', bbox=box_green, fontsize=9)
    ax.text(50, 16, "Candidate Profile View\n• Raw Resume Text Preview\n• Candidate Name Heuristic\n• Ingestion Timestamp & S3 Key", ha='center', va='center', bbox=box_purple, fontsize=9)
    ax.text(82, 16, "Pipeline Monitoring\n• SQS Queue Depth & DLQ\n• Upload Timeout Recovery (5m)\n• Status: UPLOADING/PROCESSING/DONE", ha='center', va='center', bbox=box_orange, fontsize=9)

    # Arrows
    arrow_kw = dict(arrowstyle="-|>", color="#37474F", lw=1.5, mutation_scale=14)
    ax.annotate("", xy=(25, 74), xytext=(25, 80), arrowprops=arrow_kw)
    ax.annotate("", xy=(75, 74), xytext=(75, 80), arrowprops=arrow_kw)
    ax.annotate("", xy=(40, 66), xytext=(60, 66), arrowprops=dict(arrowstyle="<|-|>", color="#37474F", lw=1.5, mutation_scale=14))
    
    ax.annotate("", xy=(42, 48), xytext=(25, 58), arrowprops=arrow_kw)
    ax.annotate("", xy=(58, 48), xytext=(75, 58), arrowprops=arrow_kw)

    ax.annotate("", xy=(20, 24), xytext=(40, 36), arrowprops=arrow_kw)
    ax.annotate("", xy=(50, 24), xytext=(50, 36), arrowprops=arrow_kw)
    ax.annotate("", xy=(80, 24), xytext=(60, 36), arrowprops=arrow_kw)

    save_fig(fig, "fig3_1_bull_diagram.png")

# ==========================================
# 2. Figure 3.2: Octopus Diagram
# ==========================================
def draw_octopus_diagram():
    fig, ax = plt.subplots(figsize=(10, 7.5))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    center_box = dict(boxstyle="circle,pad=0.8", fc="#E1F5FE", ec="#0288D1", lw=2)
    ax.text(50, 50, "TalentLens\nAI Resume\nScreening &\nSkill Matching\nPlatform", ha='center', va='center', bbox=center_box, fontsize=10, weight='bold', color="#01579B")

    # 8 tentacles
    tentacles = [
        ("Resume Ingestion & Upload\n• Presigned S3 PUT URLs\n• Client direct upload bypasses API limit\n• Fallback failure reporter", 18, 82, "#E8F5E9", "#2E7D32"),
        ("Amazon SQS & DLQ Pipeline\n• S3 ObjectCreated event trigger\n• Batch processing with retry\n• 14-day retention Dead Letter Queue", 50, 88, "#FFF3E0", "#E65100"),
        ("Amazon Textract OCR\n• Async document text detection\n• Handles multi-page complex PDFs\n• Built-in pypdf fallback extraction", 82, 82, "#F3E5F5", "#6A1B9A"),
        ("Amazon DynamoDB Database\n• Single-table serverless design\n• Pay-per-request auto-scaling\n• Candidate metadata & resume text", 88, 50, "#ECEFF1", "#37474F"),
        ("Skill Extraction Engine\n• 80+ canonical skills across 8 domains\n• Alias mapping (e.g., K8s, JS, AWS)\n• Boundary-aware regex tokenizer", 82, 18, "#E0F2F1", "#00695C"),
        ("Candidate Ranking Service\n• Dynamic match percentage (0-100%)\n• Set intersection for matched skills\n• Relative difference for missing skills", 50, 12, "#FFF8E1", "#F57F17"),
        ("React Interactive Dashboard\n• 4 dedicated section views\n• Dynamic tab navigation & modal view\n• 5-second automatic state polling", 18, 18, "#FCE4EC", "#C2185B"),
        ("AWS SAM Infrastructure\n• Infrastructure as Code (template.yaml)\n• Least-privilege IAM policies\n• HTTP API Gateway with CORS", 12, 50, "#EDE7F6", "#4527A0"),
    ]

    arrow_kw = dict(arrowstyle="<|-|>", color="#546E7A", lw=1.5, mutation_scale=12)

    for title, x, y, fc, ec in tentacles:
        box = dict(boxstyle="round,pad=0.5,rounding_size=0.3", fc=fc, ec=ec, lw=1.5)
        ax.text(x, y, title, ha='center', va='center', bbox=box, fontsize=8.5)
        # Draw connecting line to center
        dx = 50 - x
        dy = 50 - y
        dist = (dx**2 + dy**2)**0.5
        # Offset slightly from centers
        x_start = x + dx * 0.22
        y_start = y + dy * 0.22
        x_end = 50 - dx * 0.16
        y_end = 50 - dy * 0.16
        ax.annotate("", xy=(x_start, y_start), xytext=(x_end, y_end), arrowprops=arrow_kw)

    save_fig(fig, "fig3_2_octopus_diagram.png")

# ==========================================
# 3. Figure 4.1: System Architecture Diagram
# ==========================================
def draw_architecture_diagram():
    fig, ax = plt.subplots(figsize=(10.5, 7.5))
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Subgraph boxes (dashed)
    subgraph_style = dict(boxstyle="round,pad=0.5,rounding_size=0.2", fc="#FAFAFA", ec="#90A4AE", lw=1.2, ls="--")
    
    # 1. Frontend
    ax.add_patch(patches.Rectangle((3, 58), 24, 38, fill=True, fc="#F8F9FA", ec="#B0BEC5", lw=1.2, ls="--"))
    ax.text(15, 93, "Presentation Tier (Frontend)", ha='center', va='center', fontsize=9.5, weight='bold', color="#37474F")
    ax.text(15, 83, "React 18 SPA (Vite)\n• DashboardOverview\n• CandidateList & Cards\n• JobRequirements Form\n• ResumeUploader Form", ha='center', va='center', bbox=dict(boxstyle="round,pad=0.4", fc="#E1F5FE", ec="#0288D1", lw=1.2), fontsize=8.5)
    ax.text(15, 66, "API Client & Matcher\n• api.js (Fetch + camelCase)\n• skillMatcher.js (Client engine)\n• 5s Polling Controller", ha='center', va='center', bbox=dict(boxstyle="round,pad=0.4", fc="#E1F5FE", ec="#0288D1", lw=1.2), fontsize=8.5)

    # 2. API Gateway
    ax.add_patch(patches.Rectangle((31, 58), 18, 38, fill=True, fc="#F8F9FA", ec="#B0BEC5", lw=1.2, ls="--"))
    ax.text(40, 93, "API Gateway Tier", ha='center', va='center', fontsize=9.5, weight='bold', color="#37474F")
    ax.text(40, 83, "GET /api/upload\nPOST /api/upload", ha='center', va='center', bbox=dict(boxstyle="round,pad=0.4", fc="#EDE7F6", ec="#512DA8", lw=1.2), fontsize=8)
    ax.text(40, 72, "GET /api/candidates", ha='center', va='center', bbox=dict(boxstyle="round,pad=0.4", fc="#EDE7F6", ec="#512DA8", lw=1.2), fontsize=8)
    ax.text(40, 63, "POST /api/match", ha='center', va='center', bbox=dict(boxstyle="round,pad=0.4", fc="#EDE7F6", ec="#512DA8", lw=1.2), fontsize=8)

    # 3. Compute (Lambda)
    ax.add_patch(patches.Rectangle((53, 38), 24, 58, fill=True, fc="#F8F9FA", ec="#B0BEC5", lw=1.2, ls="--"))
    ax.text(65, 93, "Compute Tier (AWS Lambda)", ha='center', va='center', fontsize=9.5, weight='bold', color="#37474F")
    ax.text(65, 83, "Upload Lambda\n(handlers/upload.py)\nGenerates Presigned S3 URL", ha='center', va='center', bbox=dict(boxstyle="round,pad=0.4", fc="#FFF3E0", ec="#E65100", lw=1.2), fontsize=8)
    ax.text(65, 70, "Candidates Lambda\n(handlers/candidates.py)\nScans DDB, 5m Timeout Check", ha='center', va='center', bbox=dict(boxstyle="round,pad=0.4", fc="#FFF3E0", ec="#E65100", lw=1.2), fontsize=8)
    ax.text(65, 57, "Match Lambda\n(handlers/match.py)\nExtracts & Ranks Skills", ha='center', va='center', bbox=dict(boxstyle="round,pad=0.4", fc="#FFF3E0", ec="#E65100", lw=1.2), fontsize=8)
    ax.text(65, 44, "Process Resume Lambda\n(handlers/process_resume.py)\nAsync Textract & Fallback", ha='center', va='center', bbox=dict(boxstyle="round,pad=0.4", fc="#FFF3E0", ec="#E65100", lw=1.2), fontsize=8)

    # 4. Storage & AI Tier
    ax.add_patch(patches.Rectangle((81, 10), 22, 86, fill=True, fc="#F8F9FA", ec="#B0BEC5", lw=1.2, ls="--"))
    ax.text(92, 93, "Data & AI Services", ha='center', va='center', fontsize=9.5, weight='bold', color="#37474F")
    ax.text(92, 80, "Amazon S3\nResume Bucket\n(Private Storage)", ha='center', va='center', bbox=dict(boxstyle="round,pad=0.4", fc="#E8F5E9", ec="#2E7D32", lw=1.2), fontsize=8.5)
    ax.text(92, 63, "Amazon SQS\nProcessing Queue\n& 14-day DLQ", ha='center', va='center', bbox=dict(boxstyle="round,pad=0.4", fc="#E8F5E9", ec="#2E7D32", lw=1.2), fontsize=8.5)
    ax.text(92, 44, "Amazon Textract\nAsync Document\nText Detection", ha='center', va='center', bbox=dict(boxstyle="round,pad=0.4", fc="#FCE4EC", ec="#C2185B", lw=1.2), fontsize=8.5)
    ax.text(92, 22, "Amazon DynamoDB\nTalentLensCandidates\n(NoSQL Metadata)", ha='center', va='center', bbox=dict(boxstyle="round,pad=0.4", fc="#ECEFF1", ec="#37474F", lw=1.2), fontsize=8.5)

    # Direct S3 Upload Arrow from UI
    ax.annotate("Direct S3 PUT\n(Bypasses API Gateway)", xy=(81, 80), xytext=(27, 80),
                arrowprops=dict(arrowstyle="-|>", color="#1565C0", lw=1.8, mutation_scale=14, ls="-"),
                fontsize=8, ha='center', va='bottom', color="#0D47A1", weight='bold')

    # Connecting Arrows
    arrow_kw = dict(arrowstyle="-|>", color="#455A64", lw=1.2, mutation_scale=12)
    ax.annotate("", xy=(31, 83), xytext=(27, 83), arrowprops=arrow_kw)
    ax.annotate("", xy=(31, 72), xytext=(27, 72), arrowprops=arrow_kw)
    ax.annotate("", xy=(31, 63), xytext=(27, 63), arrowprops=arrow_kw)

    ax.annotate("", xy=(53, 83), xytext=(49, 83), arrowprops=arrow_kw)
    ax.annotate("", xy=(53, 70), xytext=(49, 72), arrowprops=arrow_kw)
    ax.annotate("", xy=(53, 57), xytext=(49, 63), arrowprops=arrow_kw)

    ax.annotate("Event Trigger", xy=(92, 69), xytext=(92, 74), arrowprops=arrow_kw, fontsize=7.5, ha='center')
    ax.annotate("Queue Batch", xy=(77, 46), xytext=(81, 59), arrowprops=arrow_kw, fontsize=7.5)
    ax.annotate("Start / Get OCR", xy=(81, 44), xytext=(77, 44), arrowprops=arrow_kw, fontsize=7.5)
    ax.annotate("Save Item", xy=(81, 25), xytext=(77, 42), arrowprops=arrow_kw, fontsize=7.5)
    ax.annotate("Scan / Read", xy=(81, 22), xytext=(77, 67), arrowprops=arrow_kw, fontsize=7.5)

    save_fig(fig, "fig4_1_architecture_diagram.png")

# ==========================================
# 4. Figure 4.2: DFD Level 0 (Context Diagram)
# ==========================================
def draw_dfd_level_0():
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # External Entity Left: Recruiter
    box_entity = dict(boxstyle="square,pad=0.6", fc="#ECEFF1", ec="#37474F", lw=1.8)
    ax.text(18, 50, "Recruiter /\nHR Specialist", ha='center', va='center', bbox=box_entity, fontsize=10, weight='bold')

    # Central Process: TalentLens
    circle_process = dict(boxstyle="circle,pad=0.7", fc="#E1F5FE", ec="#0288D1", lw=2)
    ax.text(52, 50, "0\n\nTalentLens\nResume Screening &\nSkill Matching\nSystem", ha='center', va='center', bbox=circle_process, fontsize=9.5, weight='bold')

    # External Entity Right: Cloud Services / Textract
    ax.text(86, 50, "AWS Cloud\nAI & Storage\nServices", ha='center', va='center', bbox=box_entity, fontsize=10, weight='bold')

    # Inflow / Outflow arrows between Recruiter & System
    arrow_kw = dict(arrowstyle="-|>", color="#1E88E5", lw=1.4, mutation_scale=12)
    arrow_back = dict(arrowstyle="-|>", color="#43A047", lw=1.4, mutation_scale=12)

    # Recruiter -> System
    ax.annotate("1. Resume PDF & Upload Request", xy=(42, 60), xytext=(28, 60), arrowprops=arrow_kw, fontsize=8, ha='center', va='bottom')
    ax.annotate("3. Job Criteria & Keyword Queries", xy=(42, 53), xytext=(28, 53), arrowprops=arrow_kw, fontsize=8, ha='center', va='bottom')

    # System -> Recruiter
    ax.annotate("2. S3 Presigned URL & Status", xy=(28, 44), xytext=(42, 44), arrowprops=arrow_back, fontsize=8, ha='center', va='top')
    ax.annotate("4. Ranked Match % & Skill Breakdown", xy=(28, 37), xytext=(42, 37), arrowprops=arrow_back, fontsize=8, ha='center', va='top')

    # System <-> AWS Cloud Services
    ax.annotate("PDF bytes, OCR Request", xy=(76, 56), xytext=(62, 56), arrowprops=arrow_kw, fontsize=8, ha='center', va='bottom')
    ax.annotate("Extracted Text & Event Signals", xy=(62, 44), xytext=(76, 44), arrowprops=arrow_back, fontsize=8, ha='center', va='top')

    save_fig(fig, "fig4_2_dfd_level_0.png")

# ==========================================
# 5. Figure 4.3: DFD Level 1
# ==========================================
def draw_dfd_level_1():
    fig, ax = plt.subplots(figsize=(10.5, 7.5))
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Styles
    p_box = dict(boxstyle="circle,pad=0.5", fc="#E3F2FD", ec="#1565C0", lw=1.5)
    ds_box = dict(boxstyle="square,pad=0.4", fc="#FFF9C4", ec="#FBC02D", lw=1.5)
    ent_box = dict(boxstyle="square,pad=0.5", fc="#ECEFF1", ec="#37474F", lw=1.5)
    arrow_kw = dict(arrowstyle="-|>", color="#37474F", lw=1.3, mutation_scale=11)

    # Entity: Recruiter
    ax.text(10, 52, "Recruiter", ha='center', va='center', bbox=ent_box, fontsize=10, weight='bold')

    # Processes
    ax.text(32, 85, "1.0\nRequest\nUpload URL", ha='center', va='center', bbox=p_box, fontsize=8)
    ax.text(32, 60, "2.0\nDirect S3\nUpload", ha='center', va='center', bbox=p_box, fontsize=8)
    ax.text(54, 60, "3.0\nQueue Event\nDispatch", ha='center', va='center', bbox=p_box, fontsize=8)
    ax.text(76, 60, "4.0\nTextract OCR &\nExtraction", ha='center', va='center', bbox=p_box, fontsize=8)
    ax.text(32, 35, "5.0\nFetch Candidates\n& Poll Status", ha='center', va='center', bbox=p_box, fontsize=8)
    ax.text(54, 18, "6.0\nMatch Skills &\nRank Pool", ha='center', va='center', bbox=p_box, fontsize=8)

    # Data Stores
    ax.text(54, 85, "D1: DynamoDB Candidates", ha='center', va='center', bbox=ds_box, fontsize=8.5, weight='bold')
    ax.text(32, 10, "D2: Amazon S3 Resumes", ha='center', va='center', bbox=ds_box, fontsize=8.5, weight='bold')
    ax.text(66, 38, "D3: SQS Processing Queue", ha='center', va='center', bbox=ds_box, fontsize=8.5, weight='bold')

    # Flow lines
    # Recruiter -> 1.0 -> D1 & back to Recruiter
    ax.annotate("filename", xy=(26, 85), xytext=(15, 60), arrowprops=arrow_kw, fontsize=7.5)
    ax.annotate("init record", xy=(46, 85), xytext=(38, 85), arrowprops=arrow_kw, fontsize=7.5)
    ax.annotate("presigned URL", xy=(15, 56), xytext=(26, 80), arrowprops=arrow_kw, fontsize=7.5)

    # Recruiter -> 2.0 -> D2
    ax.annotate("upload PDF", xy=(26, 60), xytext=(16, 54), arrowprops=arrow_kw, fontsize=7.5)
    ax.annotate("store PDF", xy=(32, 16), xytext=(32, 53), arrowprops=arrow_kw, fontsize=7.5)

    # 2.0 -> 3.0 via S3 notification -> D3
    ax.annotate("ObjectCreated", xy=(48, 60), xytext=(38, 60), arrowprops=arrow_kw, fontsize=7.5)
    ax.annotate("enqueue", xy=(62, 44), xytext=(57, 54), arrowprops=arrow_kw, fontsize=7.5)

    # D3 -> 4.0
    ax.annotate("batch trigger", xy=(73, 54), xytext=(68, 44), arrowprops=arrow_kw, fontsize=7.5)
    ax.annotate("update text & COMPLETED", xy=(60, 80), xytext=(74, 67), arrowprops=arrow_kw, fontsize=7.5)

    # Recruiter -> 5.0 -> read D1
    ax.annotate("poll / view", xy=(26, 37), xytext=(15, 48), arrowprops=arrow_kw, fontsize=7.5)
    ax.annotate("scan candidates", xy=(48, 80), xytext=(34, 42), arrowprops=arrow_kw, fontsize=7.5)

    # Recruiter -> 6.0 -> read D1 -> return ranked
    ax.annotate("job criteria", xy=(48, 20), xytext=(15, 44), arrowprops=arrow_kw, fontsize=7.5)
    ax.annotate("batch get / scan", xy=(54, 79), xytext=(54, 25), arrowprops=arrow_kw, fontsize=7.5)
    ax.annotate("ranked list", xy=(15, 40), xytext=(48, 16), arrowprops=arrow_kw, fontsize=7.5)

    save_fig(fig, "fig4_3_dfd_level_1.png")

# ==========================================
# 6. Figure 4.4: Use Case Diagram
# ==========================================
def draw_use_case_diagram():
    fig, ax = plt.subplots(figsize=(9.5, 7))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Boundary box
    system_box = patches.Rectangle((30, 5), 65, 90, fill=True, fc="#FAFAFA", ec="#78909C", lw=1.5, ls="-")
    ax.add_patch(system_box)
    ax.text(62, 92, "TalentLens System Boundary", ha='center', va='center', fontsize=11, weight='bold', color="#37474F")

    # Actor: Recruiter stick figure representation / box
    actor_box = dict(boxstyle="round,pad=0.5", fc="#E8EAF6", ec="#3F51B5", lw=1.8)
    ax.text(12, 50, "Recruiter /\nHR Specialist\n(Actor)", ha='center', va='center', bbox=actor_box, fontsize=10, weight='bold')

    use_cases = [
        ("UC1: Request S3 Presigned Upload URL", 62, 82),
        ("UC2: Direct Upload Resume PDF to S3", 62, 73),
        ("UC3: Monitor Asynchronous Processing Status", 62, 64),
        ("UC4: Browse Candidate Pool & View Resume Text", 62, 55),
        ("UC5: Input Job Requirements & Target Skills", 62, 46),
        ("UC6: Match Candidates Against Job Description", 62, 37),
        ("UC7: View Ranked Match Percentage & Skill Tags", 62, 28),
        ("UC8: Inspect Candidate Details & Missing Skills", 62, 19),
        ("UC9: Inspect Cloud Architecture & AWS Diagnostics", 62, 10),
    ]

    uc_style = dict(boxstyle="round,pad=0.4,rounding_size=0.3", fc="#E0F7FA", ec="#00838F", lw=1.2)
    line_kw = dict(color="#37474F", lw=1.2)

    for uc_title, x, y in use_cases:
        ax.text(x, y, uc_title, ha='center', va='center', bbox=uc_style, fontsize=8.5)
        ax.plot([19, 44], [50, y], **line_kw)

    save_fig(fig, "fig4_4_use_case_diagram.png")

# ==========================================
# 7. Figure 4.5: Sequence Diagram
# ==========================================
def draw_sequence_diagram():
    fig, ax = plt.subplots(figsize=(10.5, 7.5))
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 100)
    ax.axis('off')

    lifelines = [
        ("React UI", 10),
        ("API Gateway", 25),
        ("Upload Lambda", 40),
        ("Amazon S3", 55),
        ("Amazon SQS", 70),
        ("Process Lambda", 85),
        ("DynamoDB", 98),
    ]

    # Draw header boxes & vertical dashed lines
    for name, x in lifelines:
        ax.text(x, 95, name, ha='center', va='center', bbox=dict(boxstyle="round,pad=0.4", fc="#E1F5FE", ec="#0288D1", lw=1.2), fontsize=8, weight='bold')
        ax.plot([x, x], [8, 91], color="#B0BEC5", lw=1.2, ls="--")

    seq_arrow = dict(arrowstyle="-|>", color="#37474F", lw=1.2, mutation_scale=10)
    dash_arrow = dict(arrowstyle="-|>", color="#546E7A", lw=1.2, mutation_scale=10, ls=":")

    steps = [
        (1, 10, 25, 85, "1. GET /api/upload?filename=cv.pdf", seq_arrow),
        (2, 25, 40, 80, "2. Invoke handler", seq_arrow),
        (3, 40, 98, 75, "3. put_item(status='UPLOADING')", seq_arrow),
        (4, 40, 10, 70, "4. Return {uploadUrl, candidateId}", dash_arrow),
        (5, 10, 55, 65, "5. PUT PDF to Presigned S3 URL", seq_arrow),
        (6, 55, 70, 58, "6. ObjectCreated Event Notification", seq_arrow),
        (7, 70, 85, 51, "7. SQS Batch Event Trigger", seq_arrow),
        (8, 85, 98, 44, "8. update_item(status='PROCESSING')", seq_arrow),
        (9, 85, 85, 37, "9. Start Textract & Polling", None), # Self-call
        (10, 85, 98, 30, "10. update_item(status='COMPLETED', text)", seq_arrow),
        (11, 10, 25, 23, "11. Polling GET /api/candidates", seq_arrow),
        (12, 25, 10, 16, "12. Return updated candidate list", dash_arrow),
    ]

    for num, x1, x2, y, label, arr in steps:
        if arr is None:
            # Self-loop
            ax.plot([x1, x1+5, x1+5, x1], [y, y, y-3, y-3], color="#E65100", lw=1.3)
            ax.text(x1+6, y-1.5, label, ha='left', va='center', fontsize=7.5, color="#E65100", weight='bold')
        else:
            ax.annotate("", xy=(x2, y), xytext=(x1, y), arrowprops=arr)
            mid_x = (x1 + x2) / 2
            ax.text(mid_x, y + 1.5, label, ha='center', va='bottom', fontsize=7.5)

    save_fig(fig, "fig4_5_sequence_diagram.png")

# ==========================================
# 8. Figure 4.6: Database Design (ER Diagram)
# ==========================================
def draw_er_diagram():
    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Main DynamoDB Entity
    ddb_box = dict(boxstyle="square,pad=0.6", fc="#FFFDE7", ec="#FBC02D", lw=1.8)
    ddb_content = (
        "TABLE: TalentLensCandidates (Amazon DynamoDB)\n"
        "----------------------------------------------------\n"
        "PK: candidateId [String, UUID v4] (Partition Key)\n"
        "• filename          : String (Original uploaded file name)\n"
        "• s3Key             : String (resumes/{candidateId}/{filename})\n"
        "• status            : String (UPLOADING | PROCESSING | COMPLETED | FAILED)\n"
        "• createdAt         : String (ISO 8601 UTC timestamp)\n"
        "• processedAt       : String (ISO 8601 UTC completion timestamp)\n"
        "• candidateName     : String (Heuristically extracted full name)\n"
        "• resumeText        : String (Extracted OCR resume plain text)\n"
        "• errorMessage      : String (Optional failure diagnostic details)\n"
        "• jobTitle          : String (Title of job criteria evaluated against)\n"
        "• matchResult       : Map / Dict (Nested skill match payload)"
    )
    ax.text(48, 50, ddb_content, ha='center', va='center', bbox=ddb_box, fontsize=8.5, family='monospace')

    # Nested Map Entity
    map_box = dict(boxstyle="round,pad=0.5", fc="#E8F5E9", ec="#388E3C", lw=1.5)
    map_content = (
        "NESTED MAP: matchResult\n"
        "---------------------------------\n"
        "• match_percentage : Number (0-100)\n"
        "• matched_skills   : List[String]\n"
        "• missing_skills   : List[String]\n"
        "• resume_skills    : List[String]\n"
        "• required_skills  : List[String]"
    )
    ax.text(88, 50, map_content, ha='center', va='center', bbox=map_box, fontsize=8, family='monospace')

    # S3 Object Storage Reference
    s3_box = dict(boxstyle="round,pad=0.5", fc="#E1F5FE", ec="#0288D1", lw=1.5)
    s3_content = (
        "OBJECT STORE: Amazon S3\n"
        "---------------------------------\n"
        "Bucket: talentlens-resumes-*\n"
        "Prefix: resumes/{candidateId}/*\n"
        "Content-Type: application/pdf"
    )
    ax.text(12, 50, s3_content, ha='center', va='center', bbox=s3_box, fontsize=8, family='monospace')

    # Connections
    arrow_kw = dict(arrowstyle="<|-|>", color="#37474F", lw=1.5, mutation_scale=12)
    ax.annotate("1 : 1 S3 Object Pointer", xy=(26, 50), xytext=(21, 50), arrowprops=arrow_kw, fontsize=8, ha='center')
    ax.annotate("Embedded 1:1 Map", xy=(76, 50), xytext=(70, 50), arrowprops=arrow_kw, fontsize=8, ha='center')

    save_fig(fig, "fig4_6_er_diagram.png")

if __name__ == '__main__':
    print("Generating diagrams...")
    draw_bull_diagram()
    draw_octopus_diagram()
    draw_architecture_diagram()
    draw_dfd_level_0()
    draw_dfd_level_1()
    draw_use_case_diagram()
    draw_sequence_diagram()
    draw_er_diagram()
    print("All diagrams generated successfully!")
