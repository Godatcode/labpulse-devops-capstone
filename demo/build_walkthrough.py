"""Assemble the narrated LabPulse walkthrough from recorded project evidence.

Requires Pillow and ffmpeg. The voice tracks and their timed captions are kept in
demo/source/voice so the published video can be rebuilt without a TTS service.
"""

from __future__ import annotations

import math
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "demo"
WORK = Path("/tmp/labpulse-walkthrough-build")
WORK.mkdir(exist_ok=True)
FPS = 24
SIZE = (1920, 1080)
BG = (13, 22, 29)
PANEL = (20, 33, 42)
INK = (245, 249, 250)
MUTED = (171, 194, 202)
ACCENT = (91, 219, 197)
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

SCENES = [
    ("01", "LabPulse", ["demo/source/title-slide.png"]),
    ("02", "The working application", [
        "docs/evidence/labpulse-live-overview-2026-10-21.png",
        "docs/evidence/labpulse-live-incidents-2026-10-21.png",
    ]),
    ("03", "How it fits together", ["demo/source/architecture-slide.png"]),
    ("04", "Repository tour", ["demo/source/code-tour.mp4"]),
    ("05", "Key files", ["card:key-files"]),
    ("06", "A push starts the pipeline", ["demo/source/push.mp4"]),
    ("07", "Build, test, scan, publish", [
        "demo/source/ci-running.mp4",
        "docs/evidence/github-actions-2026-10-21.png",
    ]),
    ("08", "Terraform plan", ["demo/source/terraform-plan.mp4"]),
    ("09", "AWS VPC", ["docs/evidence/aws-vpc-active.jpg"]),
    ("10", "AWS EKS", ["docs/evidence/aws-eks-active.jpg"]),
    ("11", "Argo CD and GitOps", ["docs/evidence/argocd-synced.png"]),
    ("12", "Kubernetes health", ["demo/source/kubernetes-checks.mp4"]),
    ("13", "Prometheus targets", ["docs/evidence/prometheus-targets-2026-10-21.png"]),
    ("14", "Grafana dashboard", ["docs/evidence/grafana-dashboard-2026-10-21.png"]),
    ("15", "AWS teardown", ["demo/source/aws-cleanup.mp4"]),
    ("16", "Results and evidence", ["card:closing"]),
]


def run(*args: str) -> None:
    subprocess.run(args, check=True)


def duration(path: Path) -> float:
    value = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        text=True,
    )
    return float(value)


def base_frame(number: str, title: str) -> Image.Image:
    frame = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(frame)
    draw.rectangle((0, 0, 1920, 105), fill=PANEL)
    draw.rectangle((80, 102, 1840, 106), fill=ACCENT)
    draw.rounded_rectangle((78, 124, 1842, 899), radius=22, fill=(9, 16, 22), outline=(44, 68, 76), width=2)
    draw.rectangle((0, 920, 1920, 1080), fill=PANEL)
    draw.text((82, 23), title, font=ImageFont.truetype(BOLD, 48), fill=INK)
    credit = "ARKA GHOSH  /  GODATCODE"
    credit_font = ImageFont.truetype(BOLD, 19)
    credit_width = draw.textbbox((0, 0), credit, font=credit_font)[2]
    draw.text((1740 - credit_width, 42), credit, font=credit_font, fill=MUTED)
    draw.rounded_rectangle((1763, 30, 1838, 82), radius=13, fill=ACCENT)
    draw.text((1780, 39), number, font=ImageFont.truetype(BOLD, 28), fill=BG)
    return frame


def card(number: str, title: str, which: str) -> Image.Image:
    frame = base_frame(number, title)
    draw = ImageDraw.Draw(frame)
    if which == "key-files":
        items = [
            (".github/workflows/ci.yml", "Tests, build, Trivy, GHCR"),
            ("helm/labpulse/templates/", "Pods, Services, Ingress, HPA"),
            ("terraform/main.tf", "VPC, routing, EKS workers"),
            ("gitops/ + monitoring/", "Reconciliation and API metrics"),
        ]
        for i, (path, note) in enumerate(items):
            x = 135 + (i % 2) * 840
            y = 220 + (i // 2) * 300
            draw.rounded_rectangle((x, y, x + 735, y + 240), radius=20, fill=(25, 43, 51), outline=(60, 88, 94), width=2)
            draw.rectangle((x + 33, y + 38, x + 45, y + 181), fill=ACCENT)
            draw.text((x + 75, y + 55), path, font=ImageFont.truetype(BOLD, 34), fill=INK)
            draw.text((x + 75, y + 133), note, font=ImageFont.truetype(FONT, 30), fill=MUTED)
    else:
        items = [
            ("BUILD", "10 API tests\nCI and image scans"),
            ("DEPLOY", "Helm and GitOps\nEKS verified, then removed"),
            ("OBSERVE", "2 targets UP\nRequests and p95 latency"),
        ]
        for i, (label, note) in enumerate(items):
            x = 129 + i * 560
            draw.rounded_rectangle((x, 244, x + 525, 638), radius=22, fill=(25, 43, 51), outline=(60, 88, 94), width=2)
            draw.text((x + 41, 290), label, font=ImageFont.truetype(BOLD, 42), fill=ACCENT)
            draw.multiline_text((x + 41, 395), note, font=ImageFont.truetype(FONT, 34), fill=INK, spacing=18)
        draw.text((183, 754), "Setup steps and evidence are in the repository.", font=ImageFont.truetype(BOLD, 40), fill=INK)
    return frame


def still_frame(number: str, title: str, source: str) -> Path:
    if source.startswith("card:"):
        frame = card(number, title, source.split(":", 1)[1])
    else:
        frame = base_frame(number, title)
        shot = Image.open(ROOT / source).convert("RGB")
        if "argocd-synced" in source:
            shot = shot.crop((0, 0, min(1500, shot.width), min(1050, shot.height)))
        elif "github-actions-2026" in source:
            shot = shot.crop((0, 0, shot.width, min(1130, shot.height)))
        elif "prometheus-targets-2026" in source:
            shot = shot.crop((0, 0, shot.width, min(990, shot.height)))
        backdrop = ImageOps.fit(shot, (1744, 754), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(26))
        backdrop = Image.blend(backdrop, Image.new("RGB", backdrop.size, BG), 0.42)
        frame.paste(backdrop, (88, 133))
        shot = ImageOps.contain(shot, (1720, 738), Image.Resampling.LANCZOS)
        frame.paste(shot, ((1920 - shot.width) // 2, 141 + (738 - shot.height) // 2))
    dest = WORK / f"frame-{number}-{Path(source).stem}.png"
    frame.save(dest, optimize=True)
    return dest


def overlay_frame(number: str, title: str) -> Path:
    overlay = base_frame(number, title).convert("RGBA")
    overlay.putalpha(255)
    transparent = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    transparent.alpha_composite(overlay.crop((0, 0, 1920, 108)), (0, 0))
    transparent.alpha_composite(overlay.crop((0, 920, 1920, 1080)), (0, 920))
    draw = ImageDraw.Draw(transparent)
    draw.rounded_rectangle((78, 124, 1842, 899), radius=22, outline=(44, 68, 76, 255), width=2)
    dest = WORK / f"overlay-{number}.png"
    transparent.save(dest)
    return dest


def render_visual(number: str, title: str, source: str, frames: int, part: int) -> Path:
    output = WORK / f"visual-{number}-{part}.mp4"
    seconds = frames / FPS
    fade_start = max(0, seconds - 0.25)
    if source.endswith(".mp4"):
        overlay = overlay_frame(number, title)
        background = WORK / f"video-base-{number}.png"
        if not background.exists():
            base_frame(number, title).save(background)
        run("ffmpeg", "-y", "-loglevel", "error", "-i", str(ROOT / source), "-loop", "1", "-framerate", str(FPS),
            "-i", str(background), "-loop", "1", "-framerate", str(FPS), "-i", str(overlay),
            "-filter_complex", "[0:v]scale=1728:744:force_original_aspect_ratio=decrease,pad=1744:754:(ow-iw)/2:(oh-ih)/2:color=0x101a20,tpad=stop_mode=clone:stop_duration=30[shot];[1:v][shot]overlay=88:133:shortest=1[base];[base][2:v]overlay=0:0:shortest=1,format=yuv420p,fade=t=in:st=0:d=0.25,fade=t=out:st=" + f"{fade_start:.3f}" + ":d=0.25[v]",
            "-map", "[v]", "-an", "-frames:v", str(frames), "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", str(output))
    else:
        frame = still_frame(number, title, source)
        run("ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS), "-i", str(frame),
            "-vf", "zoompan=z='min(zoom+0.000035,1.025)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=24,"
            f"fade=t=in:st=0:d=0.25,fade=t=out:st={fade_start:.3f}:d=0.25",
            "-frames:v", str(frames), "-r", str(FPS), "-pix_fmt", "yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", str(output))
    return output


def parse_srt(path: Path, offset_ms: int) -> list[tuple[int, int, str]]:
    entries = []
    pattern = re.compile(r"(?m)^\d+\n(\d\d:\d\d:\d\d,\d{3}) --> (\d\d:\d\d:\d\d,\d{3})\n(.+?)(?=\n\n|\Z)", re.S)

    def milliseconds(value: str) -> int:
        hours, minutes, rest = value.split(":")
        seconds, ms = rest.split(",")
        return ((int(hours) * 60 + int(minutes)) * 60 + int(seconds)) * 1000 + int(ms)

    for start, end, words in pattern.findall(path.read_text()):
        entries.append((offset_ms + milliseconds(start), offset_ms + milliseconds(end), words.strip()))
    return entries


def timestamp(milliseconds: int) -> str:
    seconds, ms = divmod(milliseconds, 1000)
    minutes, sec = divmod(seconds, 60)
    hours, minute = divmod(minutes, 60)
    return f"{hours:02d}:{minute:02d}:{sec:02d},{ms:03d}"


def caption_strip(captions: list[tuple[int, int, str]], total_ms: int) -> Path:
    """Render a timed footer video; the local ffmpeg build has no libass."""
    strip = WORK / "caption-strip"
    strip.mkdir(exist_ok=True)
    blank = strip / "blank.png"
    Image.new("RGB", (1920, 160), PANEL).save(blank)
    font = ImageFont.truetype(BOLD, 31)
    files = []
    for i, (_, _, words) in enumerate(captions):
        image = Image.new("RGB", (1920, 160), PANEL)
        draw = ImageDraw.Draw(image)
        lines = [""]
        for word in words.split():
            test = (lines[-1] + " " + word).strip()
            if draw.textbbox((0, 0), test, font=font)[2] > 1720:
                lines.append(word)
            else:
                lines[-1] = test
        y = 55 if len(lines) == 1 else 33
        for line in lines:
            width = draw.textbbox((0, 0), line, font=font)[2]
            draw.text(((1920 - width) // 2, y), line, font=font, fill=INK)
            y += 44
        path = strip / f"caption-{i:03}.png"
        image.save(path)
        files.append(path)

    boundaries = sorted({0, total_ms, *(start for start, _, _ in captions), *(end for _, end, _ in captions)})
    timeline = []
    for start, end in zip(boundaries, boundaries[1:]):
        if end <= start:
            continue
        active = [i for i, (cue_start, cue_end, _) in enumerate(captions) if cue_start <= start < cue_end]
        path = files[active[-1]] if active else blank
        timeline.append((path, (end - start) / 1000))
    listing = strip / "frames.txt"
    listing.write_text("".join(f"file '{path}'\nduration {seconds:.3f}\n" for path, seconds in timeline) + f"file '{timeline[-1][0]}'\n")
    output = WORK / "caption-strip.mp4"
    run("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
        "-vf", f"fps={FPS}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", str(output))
    return output


def main() -> None:
    script = (HERE / "walkthrough-script.md").read_text()
    sections = re.findall(r"^## (\d+) · ([^\n]+)\n\n([^#]+?)(?=\n## |\Z)", script, re.M | re.S)
    assert [item[0] for item in sections] == [item[0] for item in SCENES]
    clips: list[Path] = []
    captions: list[tuple[int, int, str]] = []
    elapsed_frames = 0

    for number, title, visuals in SCENES:
        voice = HERE / "source" / "voice" / f"{number}.mp3"
        frame_count = math.ceil((duration(voice) + 1.15) * FPS)
        if number == "06":
            frame_count = max(frame_count, math.ceil(duration(ROOT / visuals[0]) * FPS))
        base, extra = divmod(frame_count, len(visuals))
        parts = [render_visual(number, title, source, base + (i < extra), i) for i, source in enumerate(visuals)]
        video = WORK / f"scene-{number}-video.mp4"
        listing = WORK / f"scene-{number}.txt"
        listing.write_text("".join(f"file '{part}'\n" for part in parts))
        run("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(video))
        final = WORK / f"scene-{number}.mp4"
        run("ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(voice),
            "-filter_complex", "[1:a]apad[a]", "-map", "0:v", "-map", "[a]", "-t", f"{frame_count / FPS:.5f}",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", str(final))
        clips.append(final)
        captions.extend(parse_srt(HERE / "source" / "voice" / f"{number}.srt", round(elapsed_frames * 1000 / FPS)))
        elapsed_frames += frame_count
        print(number, title, f"{frame_count / FPS:.1f}s", flush=True)

    srt_text = "\n\n".join(
        f"{i}\n{timestamp(start)} --> {timestamp(end)}\n{words}"
        for i, (start, end, words) in enumerate(captions, 1)
    ) + "\n"
    (HERE / "captions.srt").write_text(srt_text)
    local_srt = WORK / "captions.srt"
    local_srt.write_text(srt_text)
    listing = WORK / "all-scenes.txt"
    listing.write_text("".join(f"file '{clip}'\n" for clip in clips))
    combined = WORK / "combined.mp4"
    run("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(combined))
    strip = caption_strip(captions, round(elapsed_frames * 1000 / FPS))
    run("ffmpeg", "-y", "-loglevel", "error", "-i", str(combined), "-i", str(strip),
        "-filter_complex", "[0:v][1:v]overlay=0:920:shortest=1[v]", "-map", "[v]", "-map", "0:a",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=9", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
        "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
        "-metadata", "title=LabPulse DevOps capstone walkthrough", "-metadata", "artist=Arka Ghosh", str(HERE / "walkthrough.mp4"))
    print("Wrote", HERE / "walkthrough.mp4")


if __name__ == "__main__":
    main()
