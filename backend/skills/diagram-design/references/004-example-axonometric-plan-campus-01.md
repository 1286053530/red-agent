<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>North campus · Three phases, six buildings</title>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --color-paper:   #f5f5f5;
      --color-ink:     #2d3142;
      --color-muted:   #4f5d75;
      --color-accent:  #bf4520;
      --font-sans:     'Geist', system-ui, sans-serif;
      --font-serif:    'Instrument Serif', serif;
      --font-mono:     'Geist Mono', ui-monospace, monospace;
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
    .diagram-container { width: 100%; overflow-x: auto; }

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
      color: var(--color-ink);
      margin-bottom: 1.5rem;
    }

    svg { width: 100%; min-width: 1000px; display: block; }
    @media print {
      .diagram-container { overflow-x: visible; }
      svg { min-width: 0; }
    }
  </style>
</head>
<body>
  <div class="frame">
    <p class="eyebrow">Axonometric plan · Diagram Design</p>
    <h1>North campus · Three phases, six buildings</h1>

    <div class="diagram-container">
      <svg viewBox="0 0 1000 496" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="axonometric-plan-campus-title axonometric-plan-campus-desc">
        <title id="axonometric-plan-campus-title">North campus · Three phases, six buildings</title>
        <desc id="axonometric-plan-campus-desc">Campus site plan with the library and labs in phase 1, two dorms in phase 2, and the sports hall and parking in phase 3, with the library as the focal building.</desc>
        <rect width="100%" height="100%" fill="#f5f5f5"/>
        <g data-axo-plan data-origin="440 64">
        <g data-plate data-rect="0 0 420 300 6" data-z="0" data-t="8"><path data-role="silhouette" d="M 143.51 206 A 8.49 4.24 0 0 1 146 203 L 434 59 A 8.49 4.24 0 0 1 446 59 L 854 263 A 8.49 4.24 0 0 1 856.49 266 L 856.49 274 A 8.49 4.24 0 0 1 854 277 L 566 421 A 8.49 4.24 0 0 1 554 421 L 146 217 A 8.49 4.24 0 0 1 143.51 214 Z" fill="#ffffff"/><path d="M 143.51 206 A 8.49 4.24 0 0 0 146 209 L 554 413 A 8.49 4.24 0 0 0 560 414.24 L 560 422.24 A 8.49 4.24 0 0 1 554 421 L 146 217 A 8.49 4.24 0 0 1 143.51 214 Z" fill="rgba(45,49,66,0.07)"/><path d="M 560 414.24 A 8.49 4.24 0 0 0 566 413 L 854 269 A 8.49 4.24 0 0 0 856.49 266 L 856.49 274 A 8.49 4.24 0 0 1 854 277 L 566 421 A 8.49 4.24 0 0 1 560 422.24 Z" fill="rgba(45,49,66,0.15)"/><path d="M 143.51 206 A 8.49 4.24 0 0 0 146 209 L 554 413 A 8.49 4.24 0 0 0 566 413 L 854 269 A 8.49 4.24 0 0 0 856.49 266" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 143.51 206 A 8.49 4.24 0 0 1 146 203 L 434 59 A 8.49 4.24 0 0 1 446 59 L 854 263 A 8.49 4.24 0 0 1 856.49 266 L 856.49 274 A 8.49 4.24 0 0 1 854 277 L 566 421 A 8.49 4.24 0 0 1 554 421 L 146 217 A 8.49 4.24 0 0 1 143.51 214 Z" fill="none" stroke="#2d3142" stroke-width="1.2" stroke-linejoin="round"/></g>
        <path d="M 692 350 L 692 350 L 272 140 L 272 140 L 296 128 L 296 128 L 716 338 L 716 338 Z" fill="rgba(45,49,66,0.07)"/>
        <path d="M 360 316 L 360 316 L 336 304 L 336 304 L 636 154 L 636 154 L 660 166 L 660 166 Z" fill="rgba(45,49,66,0.07)"/>
        <line x1="284" y1="134" x2="704" y2="344" stroke="rgba(45,49,66,0.25)" stroke-width="0.8" stroke-dasharray="6,5"/>
        <line x1="648" y1="160" x2="348" y2="310" stroke="rgba(45,49,66,0.25)" stroke-width="0.8" stroke-dasharray="6,5"/>
        <g data-box data-rect="30 30 120 110 0" data-z="8" data-h="40" data-kind="building" data-name="Library" data-focal><path data-role="silhouette" d="M 360 86 L 360 86 L 440 46 L 440 46 L 530 91 L 530 91 L 530 131 L 530 131 L 450 171 L 450 171 L 360 126 L 360 126 Z" fill="#ffffff"/><path d="M 450 131 L 450 131 L 360 86 L 360 86 L 440 46 L 440 46 L 530 91 L 530 91 Z" fill="rgba(191,69,32,0.10)"/><path d="M 360 86 L 360 86 L 450 131 L 450 131 L 450 171 L 450 171 L 360 126 L 360 126 Z" fill="rgba(191,69,32,0.20)"/><path d="M 450 131 L 450 131 L 530 91 L 530 91 L 530 131 L 530 131 L 450 171 L 450 171 Z" fill="rgba(191,69,32,0.32)"/><path d="M 450 128 L 450 128 L 366 86 L 366 86 L 440 49 L 440 49 L 524 91 L 524 91 Z" fill="none" stroke="rgba(191,69,32,0.70)" stroke-width="0.6"/><path d="M 360 86 L 360 86 L 450 131 L 450 131 L 530 91 L 530 91 M 450 131 L 450 171" fill="none" stroke="rgba(191,69,32,0.70)" stroke-width="0.8"/><path d="M 360 86 L 360 86 L 440 46 L 440 46 L 530 91 L 530 91 L 530 131 L 530 131 L 450 171 L 450 171 L 360 126 L 360 126 Z" fill="none" stroke="#bf4520" stroke-width="1.0" stroke-linejoin="round"/></g>
        <g data-box data-rect="30 118 50 138 10" data-z="16" data-h="6" data-kind="tree"><path data-role="silhouette" d="M 337.86 126 A 14.14 7.07 0 0 1 342 121 L 342 121 A 14.14 7.07 0 0 1 362 121 L 362 121 A 14.14 7.07 0 0 1 366.14 126 L 366.14 132 A 14.14 7.07 0 0 1 362 137 L 362 137 A 14.14 7.07 0 0 1 342 137 L 342 137 A 14.14 7.07 0 0 1 337.86 132 Z" fill="#ffffff"/><path d="M 349 132 L 349 132 L 352 130.5 L 352 130.5 L 355 132 L 355 132 L 355 140 L 355 140 L 352 141.5 L 352 141.5 L 349 140 L 349 140 Z" fill="#2d3142"/><path d="M 337.86 126 A 14.14 7.07 0 0 1 342 121 L 342 121 A 14.14 7.07 0 0 1 362 121 L 362 121 A 14.14 7.07 0 0 1 366.14 126 L 366.14 132 A 14.14 7.07 0 0 1 362 137 L 362 137 A 14.14 7.07 0 0 1 342 137 L 342 137 A 14.14 7.07 0 0 1 337.86 132 Z" fill="#ffffff"/><path d="M 352 133.07 A 14.14 7.07 0 0 0 362 131 L 362 131 A 14.14 7.07 0 0 0 366.14 126 L 366.14 132 A 14.14 7.07 0 0 1 362 137 L 362 137 A 14.14 7.07 0 0 1 352 139.07 Z" fill="rgba(45,49,66,0.12)"/><path d="M 362 131 A 14.14 7.07 0 0 1 342 131 L 342 131 A 14.14 7.07 0 0 1 342 121 L 342 121 A 14.14 7.07 0 0 1 362 121 L 362 121 A 14.14 7.07 0 0 1 362 131 Z" fill="#bfc0c0"/><path d="M 337.86 126 A 14.14 7.07 0 0 1 342 121 L 342 121 A 14.14 7.07 0 0 1 362 121 L 362 121 A 14.14 7.07 0 0 1 366.14 126 L 366.14 132 A 14.14 7.07 0 0 1 362 137 L 362 137 A 14.14 7.07 0 0 1 342 137 L 342 137 A 14.14 7.07 0 0 1 337.86 132 Z" fill="none" stroke="#2d3142" stroke-width="0.6"/></g>
        <g data-box data-rect="174 14 194 34 10" data-z="16" data-h="6" data-kind="tree"><path data-role="silhouette" d="M 585.86 146 A 14.14 7.07 0 0 1 590 141 L 590 141 A 14.14 7.07 0 0 1 610 141 L 610 141 A 14.14 7.07 0 0 1 614.14 146 L 614.14 152 A 14.14 7.07 0 0 1 610 157 L 610 157 A 14.14 7.07 0 0 1 590 157 L 590 157 A 14.14 7.07 0 0 1 585.86 152 Z" fill="#ffffff"/><path d="M 597 152 L 597 152 L 600 150.5 L 600 150.5 L 603 152 L 603 152 L 603 160 L 603 160 L 600 161.5 L 600 161.5 L 597 160 L 597 160 Z" fill="#2d3142"/><path d="M 585.86 146 A 14.14 7.07 0 0 1 590 141 L 590 141 A 14.14 7.07 0 0 1 610 141 L 610 141 A 14.14 7.07 0 0 1 614.14 146 L 614.14 152 A 14.14 7.07 0 0 1 610 157 L 610 157 A 14.14 7.07 0 0 1 590 157 L 590 157 A 14.14 7.07 0 0 1 585.86 152 Z" fill="#ffffff"/><path d="M 600 153.07 A 14.14 7.07 0 0 0 610 151 L 610 151 A 14.14 7.07 0 0 0 614.14 146 L 614.14 152 A 14.14 7.07 0 0 1 610 157 L 610 157 A 14.14 7.07 0 0 1 600 159.07 Z" fill="rgba(45,49,66,0.12)"/><path d="M 610 151 A 14.14 7.07 0 0 1 590 151 L 590 151 A 14.14 7.07 0 0 1 590 141 L 590 141 A 14.14 7.07 0 0 1 610 141 L 610 141 A 14.14 7.07 0 0 1 610 151 Z" fill="#bfc0c0"/><path d="M 585.86 146 A 14.14 7.07 0 0 1 590 141 L 590 141 A 14.14 7.07 0 0 1 610 141 L 610 141 A 14.14 7.07 0 0 1 614.14 146 L 614.14 152 A 14.14 7.07 0 0 1 610 157 L 610 157 A 14.14 7.07 0 0 1 590 157 L 590 157 A 14.14 7.07 0 0 1 585.86 152 Z" fill="none" stroke="#2d3142" stroke-width="0.6"/></g>
