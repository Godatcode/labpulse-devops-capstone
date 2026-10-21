# LabPulse walkthrough

The [narrated video](walkthrough.mp4) runs for about five minutes. It has a spoken explanation, on-screen captions, and a separate [caption file](captions.srt). The opening uses the [presentation slides](slides.pdf); the rest follows the application and repository through delivery, infrastructure, GitOps, and monitoring.

## Demo sequence

1. Present the product and architecture, then show the working overview and incident screen.
2. Tour the codebase and identify the workflow, Helm, Terraform, GitOps, and monitoring files.
3. Show the push of commit `e89dc05`, the [Actions run in progress and its successful result](https://github.com/Godatcode/labpulse-devops-capstone/actions/runs/39595649955), including tests, builds, scans, and publication.
4. Show Terraform validation and the authenticated `24 to add` plan, followed by the VPC and EKS Console captures.
5. Show Argo CD `Synced` and `Healthy`, then the local pods, Services, Ingress, and HPA.
6. Show both Prometheus backend targets `UP` and the Grafana request and latency panels.
7. Close with the completed AWS teardown and the evidence available in the repository.

The terminal clips were recorded from the real GitHub repository, Kind cluster, and AWS account. The Console captures show the first short-lived AWS deployment; the 21 October deployment and teardown are recorded in the CLI evidence. The fresh plan shown in the video was generated after teardown and did not create resources. For exact commands, see [the local demo runbook](../docs/DEMO.md), [GitOps setup](../gitops/README.md), and [validation record](../docs/evidence/validation.md).

The [narration script](walkthrough-script.md), [assembly script](build_walkthrough.py), and source captures under `source/` are included so the edit can be reviewed or rebuilt. Rebuilding needs Pillow and ffmpeg; the recorded voice segments are already in `source/voice/`.
