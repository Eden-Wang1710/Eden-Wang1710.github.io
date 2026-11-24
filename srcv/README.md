# SRCV interactive mid-report

Static research report and trajectory explorer. Entry points:

- `index.html`: report, experiments, figures, and PDF download.
- `trajectories/q68.html`: CLM-Agent / SRCV milestone comparison.

Open the HTML directly or serve this directory with any static HTTP server. No build step, external packages, analytics, or server is required. All links are relative, so the directory can be hosted at `/srcv/` on GitHub Pages.

The trajectory page uses curated milestones from the supplied Question 68 comparison, not reconstructed raw agent messages. It preserves grouped steps and labels approximate values. Exact benchmark question/answer text, original search terms, document identifiers, and corpus excerpts are deliberately absent from the published site. The PDF is the supplied report with compressed embedded images.

Source snapshot: November 24, 2026.
