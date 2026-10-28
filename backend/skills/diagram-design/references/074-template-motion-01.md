<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Motion diagram template</title>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&family=Noto+Serif:ital@0;1&family=Noto+Sans+KR:wght@400;500;600&family=Noto+Serif+KR:wght@400&family=Noto+Sans+TC:wght@400;500;600&family=Noto+Serif+TC:wght@400&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    :root {
      --color-paper: #f5f5f5;
      --color-ink: #2d3142;
      --color-muted: #4f5d75;
      --color-soft: #5a6580;
      --color-accent: #bf4520;
      --color-rule: rgba(45,49,66,0.12);
      --font-sans: 'Geist', system-ui, sans-serif;
      --font-serif: 'Instrument Serif', 'Noto Serif', 'Noto Serif KR', serif;
      --font-mono: 'Geist Mono', ui-monospace, monospace;
      --motion-fast: 160ms;
      --motion-step: 480ms;
      --motion-hold: 720ms;
      --motion-total: 3600ms;
      --motion-ease: cubic-bezier(.2,.8,.2,1);
    }
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 48px 32px;
      color: var(--color-ink);
      background: var(--color-paper);
      font-family: var(--font-sans);
    }
    [data-motion-root] { width: min(100%, 1000px); }
    .eyebrow {
      margin: 0 0 8px;
      color: var(--color-muted);
      font: 500 12px/1.4 var(--font-mono);
      letter-spacing: .18em;
      text-transform: uppercase;
    }
    h1 { margin: 0 0 24px; font: 400 32px/1.15 var(--font-serif); }
    svg { display: block; width: 100%; min-width: 960px; }
    /* The SVG holds its readable width (min-width == the viewBox width, so the
       type ramp is never silently scaled down). This wrapper lets a narrow
       screen scroll the diagram instead of the whole page. body is a centred
       grid, so the root needs max-width/min-width to stop the grid item from
       sizing itself to the SVG's max-content width. */
    [data-motion-root] { max-width: 100%; min-width: 0; }
    .diagram-container { width: 100%; overflow-x: auto; }

    /* Static source is complete. Only an initialized enhancement hides items. */
    .motion-ready [data-motion-item] {
      opacity: .12;
      transform: translateY(8px);
      transform-box: fill-box;
      transform-origin: center;
      transition: opacity var(--motion-step) var(--motion-ease),
                  transform var(--motion-step) var(--motion-ease);
    }
    .motion-ready [data-motion-item].is-visible,
    .motion-ready[data-frame="end"] [data-motion-item],
    .motion-ready[data-frame="static"] [data-motion-item] {
      opacity: 1;
      transform: none;
    }
    .draw-path {
      fill: none;
      stroke: var(--color-accent);
      stroke-width: 3;
      stroke-dasharray: 1;
      stroke-dashoffset: 1;
      pointer-events: none;
    }
    .motion-ready .draw-path.is-visible {
      animation: draw-path var(--motion-step) linear forwards;
    }
    .flow-token { opacity: 0; pointer-events: none; }
    .motion-ready.is-playing .flow-token.is-visible {
      opacity: 1;
      animation: token-flow 3.2s linear 1 forwards;
    }
    .motion-ready[data-motion-mode="loop"].is-playing .flow-token.is-visible {
      animation-iteration-count: infinite;
    }
    @keyframes draw-path { to { stroke-dashoffset: 0; } }
    @keyframes token-flow {
      0% { transform: translateX(0); }
      100% { transform: translateX(240px); }
    }

    [data-motion-controls] {
      display: none;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid var(--color-rule);
    }
    .motion-ready [data-motion-controls] { display: flex; }
    [data-motion-controls][hidden] { display: none !important; }
    [data-motion-controls] button {
      min-width: 44px;
      min-height: 44px;
      padding: 8px 12px;
      border: 1px solid var(--color-muted);
      border-radius: 4px;
      color: var(--color-ink);
      background: var(--color-paper);
      font: 600 12px/1 var(--font-sans);
      cursor: pointer;
    }
    [data-motion-controls] button:hover { border-color: var(--color-accent); }
    [data-motion-controls] button:focus-visible {
      outline: 3px solid var(--color-accent);
      outline-offset: 2px;
    }
    [data-motion-controls] button:disabled { cursor: not-allowed; opacity: .45; }
    [data-motion-status-visible] {
      margin-left: auto;
      color: var(--color-muted);
      font: 500 12px/1.4 var(--font-mono);
    }
    .sr-only {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0,0,0,0);
      white-space: nowrap;
      border: 0;
    }
    noscript p {
      margin: 12px 0 0;
      color: var(--color-muted);
      font: 500 12px/1.4 var(--font-mono);
    }

    html[data-motion="static"] [data-motion-controls],
    html[data-motion="static"] [data-motion-decorative] { display: none !important; }
    html[data-motion="static"] [data-motion-item] {
      opacity: 1 !important;
      transform: none !important;
      animation: none !important;
      transition: none !important;
    }
    html[data-motion="step"] [data-motion-controls],
    html[data-motion="step"] [data-motion-decorative] { display: none !important; }
    html[data-motion="step"] [data-motion-item] {
      animation: none !important;
      transition: none !important;
    }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        animation-duration: .001ms !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
        transition-duration: .001ms !important;
      }
      [data-motion-item] { opacity: 1 !important; transform: none !important; }
      [data-motion-decorative] { display: none !important; }
      [data-motion-controls] { display: none !important; }
    }
    @media print {
      /* Paper has no scrollbar, so the local scroller would clip instead of
         scroll. Let the diagram scale down to the sheet: smaller but whole
         beats sharp but cut off. */
      .diagram-container { overflow-x: visible; }
      svg { min-width: 0; }
      [data-motion-controls], [data-motion-decorative] { display: none !important; }
      [data-motion-item] {
        opacity: 1 !important;
        transform: none !important;
        animation: none !important;
        transition: none !important;
      }
    }
  </style>
</head>
<body>
  <!-- Replace template-motion in IDs and prose when copying this file. -->
  <main data-motion-root data-motion-mode="step" data-step-count="5" data-step-current="5" data-frame="static" data-static-frame="complete">
    <p class="eyebrow">Process · Optional motion</p>
    <h1>Request evaluation</h1>

    <div class="diagram-container">
      <svg viewBox="0 0 960 480" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="template-motion-title template-motion-desc">
        <title id="template-motion-title">Request evaluation</title>
        <desc id="template-motion-desc">A request is validated, evaluated against a policy, queued, and appended to an audit log.</desc>
        <defs>
          <marker id="template-motion-arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
            <polygon points="0 0, 8 3, 0 6" fill="#4f5d75"/>
          </marker>
        </defs>
        <rect width="960" height="480" fill="#f5f5f5"/>

        <!-- Persistent connectors carry the static meaning. -->
        <path d="M248 180 H356" fill="none" stroke="#4f5d75" marker-end="url(#template-motion-arrow)"/>
        <path d="M556 180 H664" fill="none" stroke="#4f5d75" marker-end="url(#template-motion-arrow)"/>
        <path d="M764 232 V328" fill="none" stroke="#4f5d75" marker-end="url(#template-motion-arrow)"/>

        <g data-motion-item data-step="1" aria-label="Step 1: Request received">
          <rect x="48" y="128" width="200" height="104" rx="8" fill="#f5f5f5" stroke="#2d3142"/>
          <text x="148" y="172" text-anchor="middle" fill="#2d3142" font-family="Geist, sans-serif" font-size="16" font-weight="600">Request</text>
          <text x="148" y="196" text-anchor="middle" fill="#4f5d75" font-family="Geist Mono, monospace" font-size="12">fields complete</text>
        </g>
        <g data-motion-item data-step="2" aria-label="Step 2: Policy passed">
          <rect x="356" y="128" width="200" height="104" rx="8" fill="rgba(191,69,32,0.08)" stroke="#bf4520"/>
          <text x="456" y="168" text-anchor="middle" fill="#2d3142" font-family="Geist, sans-serif" font-size="16" font-weight="600">Policy</text>
          <text x="456" y="196" text-anchor="middle" fill="#4f5d75" font-family="Geist Mono, monospace" font-size="12">✓ PASS · rule 2</text>
        </g>
        <g data-motion-item data-step="3" aria-label="Step 3: Three items queued">
          <rect x="664" y="128" width="200" height="104" rx="8" fill="#f5f5f5" stroke="#2d3142"/>
          <text x="764" y="164" text-anchor="middle" fill="#2d3142" font-family="Geist, sans-serif" font-size="16" font-weight="600">Queue</text>
