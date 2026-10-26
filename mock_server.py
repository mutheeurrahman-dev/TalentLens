import http.server
import socketserver
import json
import urllib.parse
import sys
import os

# Add backend to path so we use real skill_extractor
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from shared.skill_extractor import match_skills

CANDIDATES = [
    {
        "candidateId": "cand-001-alex",
        "candidateName": "Alex Rivera",
        "filename": "01_Full_Stack_Developer.pdf",
        "status": "COMPLETED",
        "createdAt": "2026-10-14T08:30:00Z",
        "processedAt": "2026-10-14T08:30:15Z",
        "resumeText": (
            "Alex Rivera\nSenior Full Stack Developer\nEmail: alex.rivera@example.com | Phone: +1 555-0192\n\n"
            "PROFESSIONAL SUMMARY\nExperienced Full Stack Engineer with 5+ years building scalable web applications "
            "using React, Node.js, TypeScript, and cloud technologies. Strong background in REST APIs, PostgreSQL, "
            "and microservices architectures.\n\n"
            "TECHNICAL SKILLS\n"
            "• Languages: TypeScript, JavaScript, Python, SQL, HTML, CSS\n"
            "• Frontend: React, Next.js, Tailwind CSS, Vite\n"
            "• Backend & APIs: Node.js, Express, FastAPI, REST API, GraphQL\n"
            "• Cloud & DevOps: Amazon Web Services (AWS), AWS S3, Docker, Kubernetes, Git, GitHub Actions, Linux\n"
            "• Databases: PostgreSQL, MongoDB, Redis, DynamoDB\n\n"
            "EXPERIENCE\nLead Full Stack Developer at CloudTech Solutions (2022 - Present)\n"
            "Designed and deployed serverless APIs using AWS Lambda, S3, and DynamoDB. Built high-performance React "
            "dashboards handling 50k+ daily users."
        )
    },
    {
        "candidateId": "cand-002-priya",
        "candidateName": "Priya Sharma",
        "filename": "02_Python_Backend_Developer.pdf",
        "status": "COMPLETED",
        "createdAt": "2026-10-14T09:15:00Z",
        "processedAt": "2026-10-14T09:15:12Z",
        "resumeText": (
            "Priya Sharma\nBackend Systems Architect\nEmail: priya.sharma@example.com | Chennai, India\n\n"
            "SUMMARY\nBackend specialist with extensive hands-on experience in Python, FastAPI, Django, and distributed systems. "
            "Expert in designing event-driven microservices on AWS with SQS, Lambda, and PostgreSQL.\n\n"
            "SKILLS\n"
            "• Programming: Python, SQL, Golang, Bash\n"
            "• Web Frameworks: FastAPI, Django, Flask, Node.js\n"
            "• Cloud & Serverless: AWS Lambda, AWS SQS, AWS S3, Amazon EC2, CloudFormation\n"
            "• Databases: PostgreSQL, MySQL, Redis, DynamoDB, MongoDB\n"
            "• DevOps & Tools: Docker, Git, CI/CD, Nginx, Linux, Postman\n\n"
            "EXPERIENCE\nSenior Backend Engineer at Apex Systems (2021 - Present)\n"
            "Engineered event-driven pipeline consuming 10M messages daily using SQS and Python workers."
        )
    },
    {
        "candidateId": "cand-003-marcus",
        "candidateName": "Marcus Chen",
        "filename": "03_Cloud_DevOps_Intern.pdf",
        "status": "COMPLETED",
        "createdAt": "2026-10-14T10:00:00Z",
        "processedAt": "2026-10-14T10:00:18Z",
        "resumeText": (
            "Marcus Chen\nCloud & DevOps Engineer\nEmail: mchen@example.com | San Francisco, CA\n\n"
            "SUMMARY\nInfrastructure automation engineer specialized in AWS cloud infrastructure, Kubernetes container orchestration, "
            "and CI/CD pipeline automation.\n\n"
            "TECHNICAL SKILLS\n"
            "• Cloud: Amazon Web Services (AWS), AWS Lambda, AWS S3, AWS SQS, EC2, Terraform\n"
            "• Containers & Orchestration: Kubernetes, Docker, Helm\n"
            "• CI/CD & Monitoring: Jenkins, GitHub Actions, Prometheus, Grafana, Ansible\n"
            "• Languages & Scripting: Python, Go, Bash, SQL\n"
            "• Operating Systems: Linux, Ubuntu, RHEL"
        )
    },
    {
        "candidateId": "cand-004-ananya",
        "candidateName": "Ananya Patel",
        "filename": "04_Data_Analyst.pdf",
        "status": "COMPLETED",
        "createdAt": "2026-10-14T10:45:00Z",
        "processedAt": "2026-10-14T10:45:14Z",
        "resumeText": (
            "Ananya Patel\nData Analyst & AI Specialist\nEmail: ananya.p@example.com\n\n"
            "SUMMARY\nData Analyst proficient in Python data ecosystems, SQL database extraction, statistical analysis, and machine learning models.\n\n"
            "TECHNICAL PROFICIENCIES\n"
            "• Machine Learning & AI: Machine Learning, Deep Learning, Scikit-learn, TensorFlow, PyTorch, NLP\n"
            "• Data Processing: Python, Pandas, NumPy, SQL, R\n"
            "• Visualization & Tools: Tableau, Power BI, Git, Jupyter, Matplotlib\n"
            "• Databases: PostgreSQL, MySQL, SQLite"
        )
    },
    {
        "candidateId": "cand-005-david",
        "candidateName": "David Kim",
        "filename": "05_Frontend_Developer.pdf",
        "status": "COMPLETED",
        "createdAt": "2026-10-14T11:20:00Z",
        "processedAt": "2026-10-14T11:20:10Z",
        "resumeText": (
            "David Kim\nSenior Frontend Engineer\nEmail: dkim@example.com\n\n"
            "SUMMARY\nUI/UX focused Frontend Engineer with mastery in React, TypeScript, Next.js, and modern CSS frameworks.\n\n"
            "SKILLS\n"
            "• Languages: TypeScript, JavaScript, HTML, CSS\n"
            "• Frameworks: React, Next.js, Vue, Tailwind CSS, Vite\n"
            "• Testing & State: Jest, React Testing Library, Redux, REST API\n"
            "• Tools: Git, Figma, Webpack, Postman"
        )
    },
    {
        "candidateId": "cand-006-samantha",
        "candidateName": "Samantha Brooks",
        "filename": "06_QA_Automation_Intern.pdf",
        "status": "COMPLETED",
        "createdAt": "2026-10-14T12:00:00Z",
        "processedAt": "2026-10-14T12:00:15Z",
        "resumeText": (
            "Samantha Brooks\nQA Automation & Test Engineer\nEmail: sbrooks@example.com\n\n"
            "SUMMARY\nQuality assurance engineer passionate about robust test automation suites, API testing, and continuous integration.\n\n"
            "SKILLS\n"
            "• Testing: PyTest, Selenium, Postman, Jest\n"
            "• Languages: Python, Java, JavaScript, SQL\n"
            "• DevOps & Tracking: Jenkins, Git, Jira, Agile, Scrum, Docker\n"
            "• Other: REST API, Linux"
        )
    },
    {
        "candidateId": "cand-007-kevin",
        "candidateName": "Kevin Vance",
        "filename": "resume_kevin_security.pdf",
        "status": "PROCESSING",
        "createdAt": "2026-10-14T12:35:00Z",
        "resumeText": ""
    },
    {
        "candidateId": "cand-008-emily",
        "candidateName": "Emily Zhang",
        "filename": "emily_zhang_intern.pdf",
        "status": "UPLOADING",
        "createdAt": "2026-10-14T12:38:00Z",
        "resumeText": ""
    }
]

class MockHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == '/api/candidates':
            self._set_headers(200)
            self.wfile.write(json.dumps(CANDIDATES).encode('utf-8'))
            return

        if path == '/api/upload':
            fn = query.get('filename', ['resume.pdf'])[0]
            self._set_headers(200)
            res = {
                "candidateId": f"cand-{len(CANDIDATES)+1:03d}",
                "uploadUrl": f"http://localhost:3001/mock-s3-upload?file={fn}",
                "s3Key": f"resumes/cand-{len(CANDIDATES)+1:03d}/{fn}"
            }
            self.wfile.write(json.dumps(res).encode('utf-8'))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            data = json.loads(body) if body else {}
        except Exception:
            data = {}

        if path == '/api/match':
            reqs = data.get('requirements', '')
            job_title = data.get('jobTitle', '')
            cid_list = data.get('candidateIds', [])

            results = []
            for c in CANDIDATES:
                if c.get("status") != "COMPLETED":
                    continue
                if cid_list and c.get("candidateId") not in cid_list:
                    continue

                r_text = c.get("resumeText", "")
                m_res = match_skills(r_text, reqs)
                rec = {
                    "candidateId": c["candidateId"],
                    "candidateName": c["candidateName"],
                    "filename": c["filename"],
                    "status": c["status"],
                    "createdAt": c["createdAt"],
                    "processedAt": c.get("processedAt"),
                    "jobTitle": job_title,
                    "matchResult": m_res
                }
                results.append(rec)

            results.sort(key=lambda x: x["matchResult"]["match_percentage"], reverse=True)
            self._set_headers(200)
            self.wfile.write(json.dumps(results).encode('utf-8'))
            return

        if path == '/api/upload':
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "acknowledged"}).encode('utf-8'))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

    def do_PUT(self):
        # Handle mock S3 direct upload
        self._set_headers(200)
        self.wfile.write(b'{"status": "uploaded"}')

if __name__ == '__main__':
    PORT = 3001
    print(f"Starting mock API server on http://localhost:{PORT}")
    with socketserver.ThreadingTCPServer(("", PORT), MockHandler) as httpd:
        httpd.serve_forever()
