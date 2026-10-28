<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CI failure rate by service and sprint · Heatmap</title>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --color-paper:  #f5f5f5;
      --color-ink:    #2d3142;
      --color-muted:  #4f5d75;
      --color-accent: #bf4520;
      --font-sans:    'Geist', system-ui, sans-serif;
      --font-serif:   'Instrument Serif', serif;
      --font-mono:    'Geist Mono', ui-monospace, monospace;
    }
    body { font-family: var(--font-sans); background: var(--color-paper); color: var(--color-ink); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 3rem 2rem; }
    .frame { max-width: 1200px; width: 100%; }
    .eyebrow { font-family: var(--font-mono); font-size: 0.66rem; font-weight: 500; letter-spacing: 0.18em; text-transform: uppercase; color: var(--color-muted); margin-bottom: 0.5rem; }
    h1 { font-family: var(--font-serif); font-size: clamp(1.5rem, 2.4vw + 0.75rem, 2rem); font-weight: 400; letter-spacing: -0.02em; line-height: 1.15; margin-bottom: 1.5rem; }
    svg { display: block; width: 100%; height: auto; max-width: 100%; }
  </style>
</head>
<body>
  <div class="frame">
    <p class="eyebrow">Heatmap · Diagram Design</p>
    <h1>The week payments went dark</h1>

    <svg viewBox="0 0 1000 500" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="heatmap-title heatmap-desc">
      <title id="heatmap-title">The week payments went dark</title>
      <desc id="heatmap-desc">Heatmap of CI failure rate by service and sprint; payments service spiked to 47% in sprint 4 due to a deploy regression, recovered to 4% by sprint 6; billing carries the highest baseline failure rate at 9% in sprint 3.</desc>
      <defs>
        <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
          <circle cx="1" cy="1" r="0.9" fill="rgba(45,49,66,0.10)"/>
        </pattern>
      </defs>

      <rect width="100%" height="100%" fill="#f5f5f5"/>
      <rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>

      <!-- Cell grid: 6 columns (x=160,280,400,520,640,760), 5 rows (y=64,124,184,244,304).
           Cell size 116×56, gap 4px (col step=120, row step=60).
           Fill: single ink ramp for non-focal cells — opacity = max(0.07, value/9·0.65).
           Focal cell (payments·S4) uses the accent fill and carries data-focal="true".
           scripts/verify-heatmap.py enforces monotone opacity against data-value for every
           non-focal cell, complete 5×6 coverage, and at most one data-focal cell. -->

      <!-- SERVICE axis label (rotated) -->
      <text transform="rotate(-90 24 212)" x="24" y="212" fill="#4f5d75" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">SERVICE</text>

      <!-- SPRINT axis label -->
      <text x="518" y="36" fill="#4f5d75" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">SPRINT</text>

      <!-- Column headers -->
      <text data-axis="0" data-col="S1" x="218" y="52" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">S1</text>
      <text data-axis="1" data-col="S2" x="338" y="52" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">S2</text>
      <text data-axis="2" data-col="S3" x="458" y="52" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">S3</text>
      <text data-axis="3" data-col="S4" x="578" y="52" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">S4</text>
      <text data-axis="4" data-col="S5" x="698" y="52" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">S5</text>
      <text data-axis="5" data-col="S6" x="818" y="52" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">S6</text>

      <!-- Row labels -->
      <text data-row-label="auth" x="148" y="96" fill="#2d3142" font-size="9" font-family="'Geist Mono', monospace" text-anchor="end">auth</text>
      <text data-row-label="payments" x="148" y="156" fill="#2d3142" font-size="9" font-family="'Geist Mono', monospace" text-anchor="end">payments</text>
      <text data-row-label="api-gateway" x="148" y="216" fill="#2d3142" font-size="9" font-family="'Geist Mono', monospace" text-anchor="end">api-gateway</text>
      <text data-row-label="billing" x="148" y="276" fill="#2d3142" font-size="9" font-family="'Geist Mono', monospace" text-anchor="end">billing</text>
      <text data-row-label="notifications" x="148" y="336" fill="#2d3142" font-size="9" font-family="'Geist Mono', monospace" text-anchor="end">notifications</text>

      <!-- Row: auth (y=64) — values 4,5,6,3,2,2 -->
      <rect x="160" y="64" width="116" height="56" fill="#f5f5f5"/>
      <rect data-row="auth" data-col="S1" data-value="4" x="160" y="64" width="116" height="56" fill="rgba(45,49,66,0.29)"/>
      <text x="218" y="96" fill="#2d3142" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">4%</text>

      <rect x="280" y="64" width="116" height="56" fill="#f5f5f5"/>
      <rect data-row="auth" data-col="S2" data-value="5" x="280" y="64" width="116" height="56" fill="rgba(45,49,66,0.36)"/>
      <text x="338" y="96" fill="#2d3142" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">5%</text>

      <rect x="400" y="64" width="116" height="56" fill="#f5f5f5"/>
      <rect data-row="auth" data-col="S3" data-value="6" x="400" y="64" width="116" height="56" fill="rgba(45,49,66,0.43)"/>
      <text x="458" y="96" fill="#f5f5f5" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">6%</text>

      <rect x="520" y="64" width="116" height="56" fill="#f5f5f5"/>
      <rect data-row="auth" data-col="S4" data-value="3" x="520" y="64" width="116" height="56" fill="rgba(45,49,66,0.22)"/>
      <text x="578" y="96" fill="#2d3142" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">3%</text>

      <rect x="640" y="64" width="116" height="56" fill="#f5f5f5"/>
      <rect data-row="auth" data-col="S5" data-value="2" x="640" y="64" width="116" height="56" fill="rgba(45,49,66,0.14)"/>
      <text x="698" y="96" fill="#2d3142" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">2%</text>

      <rect x="760" y="64" width="116" height="56" fill="#f5f5f5"/>
      <rect data-row="auth" data-col="S6" data-value="2" x="760" y="64" width="116" height="56" fill="rgba(45,49,66,0.14)"/>
      <text x="818" y="96" fill="#2d3142" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">2%</text>

      <!-- Row: payments (y=124) — values 3,4,5,47(focal),6,4 -->
      <rect x="160" y="124" width="116" height="56" fill="#f5f5f5"/>
      <rect data-row="payments" data-col="S1" data-value="3" x="160" y="124" width="116" height="56" fill="rgba(45,49,66,0.22)"/>
      <text x="218" y="156" fill="#2d3142" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">3%</text>

      <rect x="280" y="124" width="116" height="56" fill="#f5f5f5"/>
      <rect data-row="payments" data-col="S2" data-value="4" x="280" y="124" width="116" height="56" fill="rgba(45,49,66,0.29)"/>
      <text x="338" y="156" fill="#2d3142" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">4%</text>

      <rect x="400" y="124" width="116" height="56" fill="#f5f5f5"/>
      <rect data-row="payments" data-col="S3" data-value="5" x="400" y="124" width="116" height="56" fill="rgba(45,49,66,0.36)"/>
      <text x="458" y="156" fill="#2d3142" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">5%</text>

      <!-- FOCAL CELL: payments·S4 = 47% deploy regression -->
      <rect x="520" y="124" width="116" height="56" fill="#f5f5f5"/>
      <rect data-row="payments" data-col="S4" data-value="47" data-focal="true" x="520" y="124" width="116" height="56" fill="rgba(191,69,32,0.85)" stroke="#bf4520" stroke-width="1.2"/>
      <text x="578" y="149" fill="#111111" font-size="10" font-weight="600" font-family="'Geist', sans-serif" text-anchor="middle">47%</text>
      <text x="578" y="163" fill="#111111" font-size="7" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.06em">REGRESSION</text>

      <rect x="640" y="124" width="116" height="56" fill="#f5f5f5"/>
      <rect data-row="payments" data-col="S5" data-value="6" x="640" y="124" width="116" height="56" fill="rgba(45,49,66,0.43)"/>
      <text x="698" y="156" fill="#f5f5f5" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">6%</text>

      <rect x="760" y="124" width="116" height="56" fill="#f5f5f5"/>
      <rect data-row="payments" data-col="S6" data-value="4" x="760" y="124" width="116" height="56" fill="rgba(45,49,66,0.29)"/>
      <text x="818" y="156" fill="#2d3142" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">4%</text>

