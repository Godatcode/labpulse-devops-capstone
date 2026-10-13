---
name: LabPulse interface
type:
  body: IBM Plex Sans
  data: IBM Plex Mono
color:
  canvas: "oklch(0.973 0.008 85)"
  surface: "oklch(0.996 0.004 85)"
  ink: "oklch(0.235 0.032 235)"
  muted: "oklch(0.49 0.022 230)"
  line: "oklch(0.865 0.014 85)"
  accent: "oklch(0.54 0.13 185)"
  warning: "oklch(0.67 0.135 65)"
  danger: "oklch(0.54 0.19 28)"
space: [4, 8, 12, 16, 24, 32, 48, 64]
radius: [6, 10, 16]
motion:
  quick: 140ms
  standard: 190ms
  ease: cubic-bezier(0.2, 0.8, 0.2, 1)
---

# LabPulse design system

The page reads like a field ledger: a clear status line, a visible set of benches, then the incidents that need action. The equipment code and room are as easy to find as the fault title. Color has a specific job: teal for healthy or primary actions, amber for attention, and red for equipment out of service.

Plex Sans handles interface copy. Plex Mono is limited to IDs, dates, counts, and small labels. Text sizes use 12, 14, 16, 20, 28, and 40 px. Body copy is 16 px with a 1.5 line height; headings tighten slightly. Long prose stops near 68 characters per line.

Surfaces use borders and spacing rather than floating shadows. The sidebar is dark ink; the main canvas is warm and bright. Buttons and rows expose hover, focus, active, disabled, loading, empty, and error states. Focus outlines remain visible by keyboard. Motion stays below 200 ms and turns off when reduced motion is requested.
