"""Build the LabPulse capstone presentation from checked-in evidence."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "evidence"
OUTPUT = Path(__file__).with_name("slides.pdf")
WIDTH, HEIGHT = 960, 540

BG = colors.HexColor("#101a20")
INK = colors.HexColor("#f3f7f8")
MUTED = colors.HexColor("#a9b8bd")
ACCENT = colors.HexColor("#58d6c2")
LINE = colors.HexColor("#37515a")

REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
pdfmetrics.registerFont(TTFont("Arial", REGULAR))
pdfmetrics.registerFont(TTFont("Arial-Bold", BOLD))

pdf = canvas.Canvas(str(OUTPUT), pagesize=(WIDTH, HEIGHT))
pdf.setTitle("LabPulse | DevOps capstone presentation")
pdf.setAuthor("Arka Ghosh")
pdf.setCreator("Arka Ghosh")
pdf.setSubject("Application, delivery pipeline, infrastructure, Kubernetes, and monitoring")


def text(x, y, content, size=17, color=INK, bold=False):
    pdf.setFillColor(color)
    pdf.setFont("Arial-Bold" if bold else "Arial", size)
    pdf.drawString(x, y, content)


def lines(x, y, items, size=17, leading=27, color=INK):
    for item in items:
        text(x, y, item, size=size, color=color)
        y -= leading


def base(number, title, subtitle=None):
    pdf.setFillColor(BG)
    pdf.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    text(55, 483, title, 32, bold=True)
    if subtitle:
        text(55, 450, subtitle, 15, MUTED)
    pdf.setStrokeColor(LINE)
    pdf.setLineWidth(0.8)
    pdf.line(55, 49, WIDTH - 55, 49)
    text(55, 28, "LabPulse  /  Arka Ghosh", 11, MUTED)
    text(WIDTH - 79, 28, f"{number:02d}", 11, MUTED)


def shot(name, x, y, width, height):
    image = ImageReader(str(EVIDENCE / name))
    iw, ih = image.getSize()
    scale = min(width / iw, height / ih)
    w, h = iw * scale, ih * scale
    left = x + (width - w) / 2
    bottom = y + (height - h) / 2
    pdf.drawImage(image, left, bottom, width=w, height=h)
    pdf.setStrokeColor(LINE)
    pdf.rect(left, bottom, w, h, fill=0, stroke=1)


def finish():
    pdf.showPage()


# 1: Project overview
pdf.setFillColor(BG)
pdf.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
text(58, 405, "LabPulse", 60, bold=True)
text(60, 353, "A lab equipment and incident tracker", 25, ACCENT)
lines(60, 267, [
    "Arka Ghosh  |  Group A  |  Roll 10110",
    "DevOps final capstone",
], size=17, leading=34, color=MUTED)
text(60, 65, "github.com/Godatcode/labpulse-devops-capstone", 14, INK)
finish()

# 2: Application
base(2, "The application", "A shared view of equipment condition and repair work")
shot("labpulse-compose.jpg", 430, 110, 470, 305)
lines(58, 366, [
    "Technicians register equipment",
    "and report faults against it.",
    "Repair status moves from open",
    "to in progress to resolved.",
], size=17, leading=31)
text(58, 202, "Stack", 18, ACCENT, bold=True)
lines(58, 170, ["React frontend", "FastAPI backend", "PostgreSQL + Alembic"],
      size=16, leading=27, color=MUTED)
finish()

# 3: Architecture
base(3, "Architecture", "One app, two services, and one database")
text(72, 365, "Browser", 23, ACCENT, bold=True)
text(248, 365, "Nginx frontend", 23, INK, bold=True)
text(505, 365, "FastAPI", 23, INK, bold=True)
text(704, 365, "PostgreSQL", 23, INK, bold=True)
text(197, 367, ">", 24, MUTED)
text(458, 367, ">", 24, MUTED)
text(661, 367, ">", 24, MUTED)
pdf.setStrokeColor(LINE)
pdf.line(72, 320, 884, 320)
text(72, 271, "HTTP paths", 20, ACCENT, bold=True)
lines(72, 236, ["/ serves React", "/api routes to FastAPI", "/health and /ready support checks"],
      size=17, leading=31)
text(505, 271, "Metrics", 20, ACCENT, bold=True)
lines(505, 236, ["Prometheus scrapes /metrics", "Grafana queries Prometheus", "Requests and latency are visible"],
      size=17, leading=31)
finish()

# 4: CI/CD
base(4, "CI/CD pipeline", "A main-branch push tests, scans, and publishes a traceable build")
shot("github-actions.jpg", 438, 106, 460, 310)
lines(58, 375, [
    "1  Pytest and Ruff check the API",
    "2  Vite builds the frontend",
    "3  Docker builds both images",
    "4  Trivy scans both images",
    "5  GHCR receives SHA-tagged images",
], size=17, leading=43)
text(58, 127, "Successful run recorded in the repository evidence.", 13, MUTED)
finish()

# 5: Infrastructure
base(5, "AWS infrastructure", "Terraform provisioned the stack in ap-southeast-2")
shot("aws-vpc-active.jpg", 54, 192, 412, 230)
shot("aws-eks-active.jpg", 494, 192, 412, 230)
text(56, 166, "VPC: 2 public + 2 private subnets", 15, INK)
text(496, 166, "EKS: cluster + managed node group", 15, INK)
text(56, 125, "24 resources created; two t3.small workers reached Ready.", 16, ACCENT)
text(56, 95, "Terraform later destroyed all 24 resources to stop AWS costs.", 15, MUTED)
finish()

# 6: Kubernetes
base(6, "Kubernetes and Helm", "The local Kind run exercised the same application chart")
shot("labpulse-ingress.jpg", 447, 111, 455, 292)
lines(58, 371, [
    "Helm installed PostgreSQL,",
    "two API pods, and two web pods.",
    "Services keep pod addressing stable.",
    "Ingress routes / and /api.",
], size=17, leading=35)
text(58, 166, "All application pods were Running/Ready.", 15, ACCENT)
text(58, 134, "HPA reported CPU metrics for the backend.", 15, MUTED)
finish()

# 7: Observability
base(7, "Observability", "Application traffic appeared in Prometheus and Grafana")
shot("prometheus-targets.jpg", 53, 190, 413, 220)
shot("grafana-dashboard.jpg", 494, 190, 413, 220)
text(55, 159, "Prometheus: both backend targets UP", 15, INK)
text(496, 159, "Grafana: request count, rate, p95 latency", 15, INK)
text(55, 108, "FastAPI exposes /metrics; Prometheus scrapes both API pods every 15 seconds.",
     15, MUTED)
finish()

# 8: Security and testing
base(8, "Tests and security", "The pipeline checks behavior before it publishes images")
text(62, 356, "10 API tests passed", 27, ACCENT, bold=True)
lines(62, 315, [
    "Tests use an isolated SQLite database.",
    "They cover equipment and incident flows",
    "along with health checks.",
], size=17, leading=29)
pdf.setStrokeColor(LINE)
pdf.line(62, 199, 894, 199)
text(62, 160, "Trivy blocked HIGH and CRITICAL findings", 23, INK, bold=True)
text(62, 121, "Both runtime images passed the final scan; new findings fail CI.", 16, MUTED)
finish()

# 9: What the work taught me
base(9, "What I learned", "The deployment evidence is reproducible, with clear limits")
lines(62, 364, [
    "A green pipeline needs tests, image checks, and published tags.",
    "Kubernetes health depends on readiness, Services, and routing.",
    "A dashboard needs real traffic and a healthy scrape target.",
    "Cloud evidence is useful only if cleanup is recorded too.",
], size=19, leading=51)
pdf.setStrokeColor(LINE)
pdf.line(62, 132, 892, 132)
text(62, 101, "Current limit: no login or role checks; the AWS stack is destroyed.",
     16, MUTED)
finish()

pdf.save()
print(OUTPUT)
