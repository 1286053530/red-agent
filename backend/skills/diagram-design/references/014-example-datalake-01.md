<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Open data lake · Architecture</title>
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
    body {
      font-family: var(--font-sans);
      background: var(--color-paper);
      color: var(--color-ink);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 3rem 2rem;
    }
    .frame { max-width: 1200px; width: 100%; }
    .eyebrow {
      font-family: var(--font-mono);
      font-size: 0.66rem;
      font-weight: 500;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--color-muted);
      margin-bottom: 0.5rem;
    }
    h1 {
      font-family: var(--font-serif);
      font-size: clamp(1.5rem, 2.4vw + 0.75rem, 2rem);
      font-weight: 400;
      letter-spacing: -0.02em;
      line-height: 1.15;
      margin-bottom: 1.5rem;
    }
    svg { width: 100%; min-width: 960px; display: block; }
  </style>
</head>
<body>
  <div class="frame">
    <p class="eyebrow">Architecture · Diagram Design</p>
    <h1>Open data lake · End-to-end stack</h1>

    <svg viewBox="0 0 1000 488" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="datalake-title datalake-desc">
      <title id="datalake-title">Open data lake · End-to-end stack</title>
      <desc id="datalake-desc">Data lake architecture showing app servers and databases flowing through Apache NiFi into MinIO, then Trino, StarRocks, Superset, JupyterLab, and Python.</desc>
      <defs>
        <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
          <circle cx="1" cy="1" r="0.9" fill="rgba(45,49,66,0.10)"/>
        </pattern>
        <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
          <polygon points="0 0, 8 3, 0 6" fill="#4f5d75"/>
        </marker>
        <marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
          <polygon points="0 0, 8 3, 0 6" fill="#bf4520"/>
        </marker>
      </defs>

      <!-- Background -->
      <rect width="100%" height="100%" fill="#f5f5f5"/>
      <rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>

      <!-- Zone rects (drawn before labels, arrows, nodes) -->
      <rect x="4"   y="32" width="160" height="200" rx="8" fill="rgba(45,49,66,0.02)" stroke="rgba(45,49,66,0.10)" stroke-width="0.8"/>
      <rect x="176" y="32" width="160" height="200" rx="8" fill="rgba(45,49,66,0.02)" stroke="rgba(45,49,66,0.10)" stroke-width="0.8"/>
      <rect x="380" y="32" width="184" height="160" rx="8" fill="rgba(191,69,32,0.04)" stroke="rgba(191,69,32,0.20)" stroke-width="0.8"/>
      <rect x="600" y="32" width="168" height="200" rx="8" fill="rgba(45,49,66,0.02)" stroke="rgba(45,49,66,0.10)" stroke-width="0.8"/>
      <rect x="804" y="32" width="164" height="280" rx="8" fill="rgba(45,49,66,0.02)" stroke="rgba(45,49,66,0.10)" stroke-width="0.8"/>

      <!-- Zone labels -->
      <text x="84"  y="44" fill="#4f5d75" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.16em" text-anchor="middle">SOURCES</text>
      <text x="256" y="44" fill="#4f5d75" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.16em" text-anchor="middle">INGEST</text>
      <text x="472" y="44" fill="#bf4520" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.16em" text-anchor="middle">DATA LAKE</text>
      <text x="688" y="44" fill="#4f5d75" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.16em" text-anchor="middle">QUERY</text>
      <text x="876" y="44" fill="#4f5d75" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.16em" text-anchor="middle">CONSUME</text>

      <!-- ═══════════════════════════════════════════
           ARROWS — drawn before boxes (z-order rule)
           ═══════════════════════════════════════════ -->

      <!-- AppServer → NiFi -->
      <line x1="152" y1="88" x2="187" y2="88" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>
      <!-- DBSource → Airflow -->
      <line x1="152" y1="192" x2="187" y2="192" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>

      <!-- NiFi → MinIO -->
      <path d="M 324,80 H 350 Q 358,80 358,88 V 112 Q 358,120 366,120 H 391" fill="none" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>
      <!-- Airflow → MinIO -->
      <path d="M 324,200 H 350 Q 358,200 358,192 V 168 Q 358,160 366,160 H 391" fill="none" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>

      <!-- MinIO → Trino (accent — primary query path) -->
      <path d="M 553,128 H 576 Q 584,128 584,120 V 96 Q 584,88 592,88 H 615" fill="none" stroke="#bf4520" stroke-width="1.2" marker-end="url(#arrow-accent)"/>
      <!-- MinIO → StarRocks -->
      <path d="M 553,152 H 576 Q 584,152 584,160 V 180 Q 584,188 592,188 H 615" fill="none" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>

      <!-- Arrow label on MinIO→Trino (on vertical segment at x=584) -->
      <rect x="586" y="102" width="28" height="12" rx="2" fill="#f5f5f5"/>
      <text x="600" y="111" fill="#bf4520" font-size="7" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.08em">SQL</text>

      <!-- Trino → Superset (same row → left/right port) -->
      <line x1="760" y1="88" x2="815" y2="88" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>
      <!-- Trino → Jupyter (vertical-primary → exit Trino bottom, enter Jupyter top) -->
      <path d="M 688,116 V 132 Q 688,140 696,140 H 876 Q 884,140 884,148 V 152" fill="none" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>
      <!-- StarRocks → Jupyter (nearly horizontal → left/right port) -->
      <line x1="760" y1="180" x2="815" y2="180" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>
      <!-- StarRocks → Python (vertical-primary → exit StarRocks bottom, enter Python top) -->
      <path d="M 688,220 V 232 Q 688,240 696,240 H 876 Q 884,240 884,244" fill="none" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>

      <!-- Python → MinIO (write-back, dashed — orthogonal via bottom gutter at y=320) -->
      <path d="M 884,300 V 312 Q 884,320 876,320 H 480 Q 472,320 472,312 V 180" fill="none" stroke="rgba(45,49,66,0.30)" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrow)"/>
      <rect x="660" y="314" width="36" height="12" rx="2" fill="#f5f5f5"/>
      <text x="678" y="323" fill="#5a6580" font-size="7" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.08em">WRITE</text>

      <!-- ═══════════════════════════════════════════
           NODES
           ═══════════════════════════════════════════ -->

      <!-- ── App servers ── -->
      <rect x="16" y="60" width="136" height="56" rx="6" fill="#f5f5f5"/>
      <rect x="16" y="60" width="136" height="56" rx="6" fill="white" stroke="rgba(45,49,66,0.25)" stroke-width="1"/>
      <rect x="24" y="66" width="26" height="12" rx="2" fill="transparent" stroke="rgba(45,49,66,0.30)" stroke-width="0.8"/>
      <text x="37" y="75" fill="rgba(45,49,66,0.55)" font-size="7" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.08em">EXT</text>
      <svg x="72" y="66" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2d3142" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M3 7a3 3 0 0 1 3 -3h12a3 3 0 0 1 3 3v2a3 3 0 0 1 -3 3h-12a3 3 0 0 1 -3 -3"/>
        <path d="M3 15a3 3 0 0 1 3 -3h12a3 3 0 0 1 3 3v2a3 3 0 0 1 -3 3h-12a3 3 0 0 1 -3 -3l0 -2"/>
        <path d="M7 8l0 .01"/><path d="M7 16l0 .01"/>
      </svg>
      <text x="84" y="102" fill="#2d3142" font-size="11" font-weight="600" font-family="'Geist', sans-serif" text-anchor="middle">App servers</text>
      <text x="84" y="114" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">Events · logs</text>

      <!-- ── Databases ── -->
      <rect x="16" y="164" width="136" height="56" rx="6" fill="#f5f5f5"/>
      <rect x="16" y="164" width="136" height="56" rx="6" fill="white" stroke="rgba(45,49,66,0.25)" stroke-width="1"/>
      <rect x="24" y="170" width="26" height="12" rx="2" fill="transparent" stroke="rgba(45,49,66,0.30)" stroke-width="0.8"/>
      <text x="37" y="179" fill="rgba(45,49,66,0.55)" font-size="7" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.08em">EXT</text>
      <svg x="72" y="170" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2d3142" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M4 6a8 3 0 1 0 16 0a8 3 0 1 0 -16 0"/>
        <path d="M4 6v6a8 3 0 0 0 16 0v-6"/>
        <path d="M4 12v6a8 3 0 0 0 16 0v-6"/>
      </svg>
