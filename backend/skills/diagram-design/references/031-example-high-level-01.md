<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>High-level architecture · End-to-end stack</title>
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
    <h1>High-level architecture · End-to-end stack</h1>

    <svg viewBox="0 0 1000 540" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="high-level-title high-level-desc">
      <title id="high-level-title">High-level architecture · End-to-end stack</title>
      <desc id="high-level-desc">Architecture diagram showing data sources moving through Apache NiFi and MinIO into Trino, data modeling, and Superset dashboards, with Airflow orchestration.</desc>
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
        <marker id="arrow-sm" markerWidth="6" markerHeight="5" refX="5" refY="2.5" orient="auto">
          <polygon points="0 0, 6 2.5, 0 5" fill="#4f5d75"/>
        </marker>
      </defs>

      <!-- Background -->
      <rect width="100%" height="100%" fill="#f5f5f5"/>
      <rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>

      <!-- ═══════════════════════════════════════════
           PHASE CHEVRON BANNER
           ═══════════════════════════════════════════ -->
      <polygon points="0,4 188,4 200,18 188,32 0,32" fill="#2d3142"/>
      <polygon points="200,4 388,4 400,18 388,32 200,32 212,18" fill="#3d4460"/>
      <polygon points="400,4 588,4 600,18 588,32 400,32 412,18" fill="#2d3142"/>
      <polygon points="600,4 788,4 800,18 788,32 600,32 612,18" fill="#3d4460"/>
      <polygon points="800,4 1000,4 1000,32 800,32 812,18" fill="#2d3142"/>

      <text x="100" y="21" fill="#f5f5f5" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">DATA SOURCES</text>
      <text x="300" y="21" fill="#f5f5f5" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">INGESTION</text>
      <text x="500" y="21" fill="#f5f5f5" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">STORAGE</text>
      <text x="700" y="21" fill="#f5f5f5" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.13em" text-anchor="middle">TRANSFORMATION &amp; ANALYSIS</text>
      <text x="900" y="21" fill="#f5f5f5" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">VISUALIZATION</text>

      <!-- ═══════════════════════════════════════════
           STRUCTURAL ZONES
           ═══════════════════════════════════════════ -->
      <!-- Data sources zone (external, dashed border) -->
      <rect x="4" y="40" width="152" height="336" rx="6" fill="rgba(45,49,66,0.02)" stroke="rgba(45,49,66,0.20)" stroke-width="0.8" stroke-dasharray="6,3"/>
      <text x="80" y="52" fill="#4f5d75" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">SOURCES</text>

      <!-- Kubernetes boundary (solid) -->
      <rect x="164" y="40" width="832" height="336" rx="8" fill="rgba(45,49,66,0.02)" stroke="rgba(45,49,66,0.18)" stroke-width="1.2"/>

      <!-- Identity Manager bar -->
      <rect x="4" y="388" width="992" height="40" rx="6" fill="rgba(45,49,66,0.05)" stroke="rgba(45,49,66,0.20)" stroke-width="0.8"/>

      <!-- ═══════════════════════════════════════════
           ARROWS — drawn before boxes (z-order rule)
           ═══════════════════════════════════════════ -->

      <!-- Data sources → NiFi: WEB and FTP enter the left edge, DB and Legacy rise into the bottom edge -->
      <path d="M 128,124 Q 128,132 136,132 H 176" fill="none" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>
      <path d="M 144,172 H 176" fill="none" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>
      <path d="M 144,252 H 196 Q 204,252 204,244 V 192" fill="none" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>
      <path d="M 144,336 H 220 Q 228,336 228,328 V 192" fill="none" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>

      <!-- Airflow → tools (dashed orchestration drops) -->
      <line x1="452" y1="96" x2="452" y2="104" stroke="#4f5d75" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrow-sm)"/>
      <line x1="682" y1="96" x2="682" y2="144" stroke="#4f5d75" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrow-sm)"/>
      <line x1="896" y1="96" x2="896" y2="144" stroke="#4f5d75" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrow-sm)"/>

      <!-- NiFi → Trino (straight, own port) -->
      <path d="M 328,140 H 372" fill="none" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>

      <!-- NiFi → MinIO (bend down — ACCENT primary path) -->
      <path d="M 328,164 H 344 Q 352,164 352,172 V 240 Q 352,248 360,248 H 372" fill="none" stroke="#bf4520" stroke-width="1.2" marker-end="url(#arrow-accent)"/>

      <!-- Trino → MinIO (vertical, Trino queries storage) -->
      <line x1="444" y1="176" x2="444" y2="208" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>
      <!-- MinIO → Trino (write-back, dashed) -->
      <line x1="460" y1="208" x2="460" y2="176" stroke="rgba(45,49,66,0.30)" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrow)"/>

      <!-- Trino → Data Modeling (bend down) -->
      <path d="M 532,140 H 556 Q 564,140 564,148 V 160 Q 564,168 572,168 H 600" fill="none" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>

      <!-- MinIO → Data Modeling (bend up — ACCENT primary path) -->
      <path d="M 532,248 H 556 Q 564,248 564,240 V 208 Q 564,200 572,200 H 600" fill="none" stroke="#bf4520" stroke-width="1.2" marker-end="url(#arrow-accent)"/>

      <!-- Data Modeling → Dashboards (straight) -->
      <line x1="764" y1="184" x2="820" y2="184" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>

      <!-- ═══════════════════════════════════════════
           NODES
           ═══════════════════════════════════════════ -->

      <!-- ── WEB ── -->
      <rect x="12" y="60" width="132" height="64" rx="6" fill="#f5f5f5"/>
      <rect x="12" y="60" width="132" height="64" rx="6" fill="white" stroke="rgba(45,49,66,0.22)" stroke-width="1"/>
      <rect x="20" y="66" width="22" height="12" rx="2" fill="transparent" stroke="rgba(45,49,66,0.28)" stroke-width="0.8"/>
      <text x="31" y="75" fill="rgba(45,49,66,0.55)" font-size="7" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.08em">EXT</text>
      <svg x="66" y="66" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2d3142" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="9"/>
        <path d="M3.6 9h16.8M3.6 15h16.8"/>
        <path d="M11.5 3a17 17 0 0 0 0 18M12.5 3a17 17 0 0 1 0 18"/>
      </svg>
      <text x="78" y="102" fill="#2d3142" font-size="11" font-weight="600" font-family="'Geist', sans-serif" text-anchor="middle">WEB</text>
      <text x="78" y="114" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">Census · Survey · Admin</text>

      <!-- ── FTP ── -->
      <rect x="12" y="140" width="132" height="64" rx="6" fill="#f5f5f5"/>
      <rect x="12" y="140" width="132" height="64" rx="6" fill="white" stroke="rgba(45,49,66,0.22)" stroke-width="1"/>
      <rect x="20" y="146" width="22" height="12" rx="2" fill="transparent" stroke="rgba(45,49,66,0.28)" stroke-width="0.8"/>
