<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>High-level architecture · Vertical chevrons (Orchestration + Security)</title>
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
    <p class="eyebrow">Architecture · Diagram Design · Parametric</p>
    <h1>High-level architecture · Vertical Orchestration + Security</h1>

    <svg viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="high-level-vertical-title high-level-vertical-desc">
      <title id="high-level-vertical-title">High-level architecture · Vertical Orchestration + Security</title>
      <desc id="high-level-vertical-desc">Architecture diagram showing data sources moving through ingestion, storage, transformation, and visualization alongside orchestration, security, and observability.</desc>
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
        <marker id="arrow-dim" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
          <polygon points="0 0, 8 3, 0 6" fill="rgba(45,49,66,0.45)"/>
        </marker>
      </defs>

      <!-- Background -->
      <rect width="100%" height="100%" fill="#f5f5f5"/>
      <rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>

      <!-- ═══════════════════════════════════════════
           PHASE CHEVRON BANNER  (horizontal, 5 phases)
           effective_w=964 (8-px margin to right strip), widths=[192,192,192,192,196], cx=[96,288,480,672,866]
           ═══════════════════════════════════════════ -->
      <polygon points="0,4 180,4 192,18 180,32 0,32" fill="#2d3142"/>
      <polygon points="192,4 372,4 384,18 372,32 192,32 204,18" fill="#3d4460"/>
      <polygon points="384,4 564,4 576,18 564,32 384,32 396,18" fill="#2d3142"/>
      <polygon points="576,4 756,4 768,18 756,32 576,32 588,18" fill="#3d4460"/>
      <polygon points="768,4 964,4 964,32 768,32 780,18" fill="#2d3142"/>

      <text x="96"  y="21" fill="#f5f5f5" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">DATA SOURCES</text>
      <text x="288" y="21" fill="#f5f5f5" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">INGESTION</text>
      <text x="480" y="21" fill="#f5f5f5" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">STORAGE</text>
      <text x="672" y="21" fill="#f5f5f5" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">TRANSFORM</text>
      <text x="866" y="21" fill="#f5f5f5" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">VISUALIZATION</text>

      <!-- ═══════════════════════════════════════════
           RIGHT STRIP — vertical chevrons (Orchestration / Security / Observability)
           strip_x=972 w=28, n_cross=2 → strip_y_bot=472, heights=[144,144,144]
           layout: [40..184, 184..328, 328..472]
           ═══════════════════════════════════════════ -->
      <!-- Orchestration (first/topmost): flat top, point at bottom -->
      <polygon points="972,40 1000,40 1000,172 986,184 972,172" fill="#2d3142"/>
      <text x="986" y="112" fill="#f5f5f5" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle" transform="rotate(-90 986 112)">ORCHESTRATION</text>
      <!-- Security (middle): notch on top, point on bottom — chevron color=#b85450 rust-red to pair with Identity bar -->
      <polygon points="972,184 986,196 1000,184 1000,316 986,328 972,316" fill="#b85450"/>
      <text x="986" y="256" fill="#f5f5f5" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle" transform="rotate(-90 986 256)">SECURITY</text>
      <!-- Observability (last/bottommost): notch on top, flat bottom -->
      <polygon points="972,328 986,340 1000,328 1000,472 972,472" fill="#2d3142"/>
      <text x="986" y="400" fill="#f5f5f5" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle" transform="rotate(-90 986 400)">OBSERVABILITY</text>

      <!-- ═══════════════════════════════════════════
           STRUCTURAL ZONES
           ═══════════════════════════════════════════ -->
      <!-- Sources zone (dashed external) -->
      <rect x="4" y="40" width="184" height="336" rx="6" fill="rgba(45,49,66,0.02)" stroke="rgba(45,49,66,0.20)" stroke-width="0.8" stroke-dasharray="6,3"/>
      <text x="96" y="52" fill="#4f5d75" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">SOURCES</text>

      <!-- Cluster boundary (solid) — right edge at 964 (8-px gap to strip at 972) -->
      <rect x="196" y="40" width="768" height="336" rx="8" fill="rgba(45,49,66,0.02)" stroke="rgba(45,49,66,0.18)" stroke-width="1.2"/>

      <!-- Identity / cross-cutting bar (color=#b85450 rust-red) -->
      <rect x="4" y="388" width="960" height="40" rx="6" fill="rgba(184,84,80,0.06)" stroke="rgba(184,84,80,0.35)" stroke-width="0.8"/>

      <!-- ═══════════════════════════════════════════
           ARROWS  (drawn before nodes — z-order rule)
           ═══════════════════════════════════════════ -->

      <!-- Sources → NiFi: PostgreSQL and SFTP enter the left edge (y=132, 172); Web forms and Legacy rise into the bottom edge (x=236, 260) -->
      <path d="M 168,124 Q 168,132 176,132 H 212" fill="none" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>
      <path d="M 184,172 H 212" fill="none" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>
      <path d="M 184,252 H 228 Q 236,252 236,244 V 200" fill="none" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>
      <path d="M 184,332 H 252 Q 260,332 260,324 V 200" fill="none" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>

      <!-- Airflow bar → NiFi, Trino, Notebooks (trigger drops at each node's cx, from bar.bottom=96 to node.top=120) -->
      <line x1="288" y1="96" x2="288" y2="120" stroke="#4f5d75" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrow-sm)"/>
      <line x1="480" y1="96" x2="480" y2="120" stroke="#4f5d75" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrow-sm)"/>
      <line x1="672" y1="96" x2="672" y2="120" stroke="#4f5d75" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrow-sm)"/>

      <!-- NiFi → Trino (secondary, straight at y=148) -->
      <line x1="364" y1="148" x2="404" y2="148" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>
      <!-- NiFi → MinIO (PRIMARY accent — own port at y=176, trunk at boundary x=388, drop to MinIO cy=256) -->
      <path d="M 364,176 H 380 Q 388,176 388,184 V 248 Q 388,256 396,256 H 404" fill="none" stroke="#bf4520" stroke-width="1.2" marker-end="url(#arrow-accent)"/>

      <!-- Trino ↔ MinIO (query read-back, dashed) -->
      <line x1="480" y1="200" x2="480" y2="216" stroke="rgba(45,49,66,0.30)" stroke-width="1" stroke-dasharray="4,3" marker-end="url(#arrow-dim)"/>

      <!-- MinIO → Notebooks (PRIMARY accent — trunk at boundary x=580, rise to Notebooks cy=160) -->
      <path d="M 556,256 H 576 Q 580,256 580,248 V 168 Q 580,160 588,160 H 596" fill="none" stroke="#bf4520" stroke-width="1.2" marker-end="url(#arrow-accent)"/>

      <!-- Notebooks → Superset (secondary, straight at cy=160) -->
