<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Corner coffee shop · From the door to a seat</title>
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
    <h1>Corner coffee shop · From the door to a seat</h1>

    <div class="diagram-container">
      <svg viewBox="0 0 1000 460" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="axonometric-plan-coffee-shop-title axonometric-plan-coffee-shop-desc">
        <title id="axonometric-plan-coffee-shop-title">Corner coffee shop · From the door to a seat</title>
        <desc id="axonometric-plan-coffee-shop-desc">Axonometric floor plan of a small coffee shop with an entrance and queue, an espresso bar, seating, a kitchen, and a restroom, with the espresso bar as the focal room.</desc>
        <rect width="100%" height="100%" fill="#f5f5f5"/>
        <g data-axo-plan data-origin="448 76">
        <g data-plate data-rect="0 0 360 260 0" data-z="0" data-t="6"><path data-role="silhouette" d="M 188 200 L 188 200 L 448 70 L 448 70 L 808 250 L 808 250 L 808 256 L 808 256 L 548 386 L 548 386 L 188 206 L 188 206 Z" fill="#ffffff"/><path d="M 188 200 L 188 200 L 548 380 L 548 380 L 548 386 L 548 386 L 188 206 L 188 206 Z" fill="rgba(45,49,66,0.07)"/><path d="M 548 380 L 548 380 L 808 250 L 808 250 L 808 256 L 808 256 L 548 386 L 548 386 Z" fill="rgba(45,49,66,0.15)"/><path d="M 188 200 L 188 200 L 548 380 L 548 380 L 808 250 L 808 250 M 548 380 L 548 386" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 188 200 L 188 200 L 448 70 L 448 70 L 808 250 L 808 250 L 808 256 L 808 256 L 548 386 L 548 386 L 188 206 L 188 206 Z" fill="none" stroke="#2d3142" stroke-width="1.2" stroke-linejoin="round"/></g>
        <g data-room data-name="Entrance" data-rect="100 86 196 254 0"></g>
        <g data-room data-name="Espresso bar" data-rect="6 86 100 254 0" data-focal><path d="M 294 247 L 294 247 L 200 200 L 200 200 L 368 116 L 368 116 L 462 163 L 462 163 Z" fill="rgba(191,69,32,0.12)"/></g>
        <g data-room data-name="Seating" data-rect="196 86 354 254 0"></g>
        <g data-room data-name="Kitchen" data-rect="6 6 250 80 0"></g>
        <g data-room data-name="Restroom" data-rect="256 6 354 80 0"></g>
        <g data-box data-rect="0 0 360 6 0" data-z="6" data-h="22" data-kind="wall"><path data-role="silhouette" d="M 442 51 L 442 51 L 448 48 L 448 48 L 808 228 L 808 228 L 808 250 L 808 250 L 802 253 L 802 253 L 442 73 L 442 73 Z" fill="#ffffff"/><path d="M 442 51 L 442 51 L 802 231 L 802 231 L 802 253 L 802 253 L 442 73 L 442 73 Z" fill="rgba(45,49,66,0.07)"/><path d="M 802 231 L 802 231 L 808 228 L 808 228 L 808 250 L 808 250 L 802 253 L 802 253 Z" fill="rgba(45,49,66,0.15)"/><path d="M 442 51 L 442 51 L 802 231 L 802 231 L 808 228 L 808 228 M 802 231 L 802 253" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 442 51 L 442 51 L 448 48 L 448 48 L 808 228 L 808 228 L 808 250 L 808 250 L 802 253 L 802 253 L 442 73 L 442 73 Z" fill="none" stroke="#2d3142" stroke-width="1.0" stroke-linejoin="round"/></g>
        <g data-box data-rect="0 6 6 260 0" data-z="6" data-h="22" data-kind="wall"><path data-role="silhouette" d="M 188 178 L 188 178 L 442 51 L 442 51 L 448 54 L 448 54 L 448 76 L 448 76 L 194 203 L 194 203 L 188 200 L 188 200 Z" fill="#ffffff"/><path d="M 188 178 L 188 178 L 194 181 L 194 181 L 194 203 L 194 203 L 188 200 L 188 200 Z" fill="rgba(45,49,66,0.07)"/><path d="M 194 181 L 194 181 L 448 54 L 448 54 L 448 76 L 448 76 L 194 203 L 194 203 Z" fill="rgba(45,49,66,0.15)"/><path d="M 188 178 L 188 178 L 194 181 L 194 181 L 448 54 L 448 54 M 194 181 L 194 203" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 188 178 L 188 178 L 442 51 L 442 51 L 448 54 L 448 54 L 448 76 L 448 76 L 194 203 L 194 203 L 188 200 L 188 200 Z" fill="none" stroke="#2d3142" stroke-width="1.0" stroke-linejoin="round"/></g>
        <g data-box data-rect="12 12 64 26 0" data-z="6" data-h="34" data-kind="rack"><path data-role="silhouette" d="M 434 55 L 434 55 L 448 48 L 448 48 L 500 74 L 500 74 L 500 108 L 500 108 L 486 115 L 486 115 L 434 89 L 434 89 Z" fill="#ffffff"/><path d="M 434 55 L 434 55 L 486 81 L 486 81 L 486 115 L 486 115 L 434 89 L 434 89 Z" fill="rgba(45,49,66,0.07)"/><path d="M 486 81 L 486 81 L 500 74 L 500 74 L 500 108 L 500 108 L 486 115 L 486 115 Z" fill="rgba(45,49,66,0.15)"/><path d="M 434 75 L 486 101 L 500 94" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.6"/><path d="M 434 61 L 486 87 L 500 80" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.6"/><line x1="460" y1="102" x2="460" y2="68" stroke="rgba(45,49,66,0.55)" stroke-width="0.6"/><path d="M 434 55 L 434 55 L 486 81 L 486 81 L 500 74 L 500 74 M 486 81 L 486 115" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 434 55 L 434 55 L 448 48 L 448 48 L 500 74 L 500 74 L 500 108 L 500 108 L 486 115 L 486 115 L 434 89 L 434 89 Z" fill="none" stroke="#2d3142" stroke-width="0.8" stroke-linejoin="round"/></g>
        <g data-box data-rect="6 80 30 86 0" data-z="6" data-h="22" data-kind="wall"><path data-role="silhouette" d="M 368 94 L 368 94 L 374 91 L 374 91 L 398 103 L 398 103 L 398 125 L 398 125 L 392 128 L 392 128 L 368 116 L 368 116 Z" fill="#ffffff"/><path d="M 368 94 L 368 94 L 392 106 L 392 106 L 392 128 L 392 128 L 368 116 L 368 116 Z" fill="rgba(45,49,66,0.07)"/><path d="M 392 106 L 392 106 L 398 103 L 398 103 L 398 125 L 398 125 L 392 128 L 392 128 Z" fill="rgba(45,49,66,0.15)"/><path d="M 368 94 L 368 94 L 392 106 L 392 106 L 398 103 L 398 103 M 392 106 L 392 128" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 368 94 L 368 94 L 374 91 L 374 91 L 398 103 L 398 103 L 398 125 L 398 125 L 392 128 L 392 128 L 368 116 L 368 116 Z" fill="none" stroke="#2d3142" stroke-width="1.0" stroke-linejoin="round"/></g>
        <g data-box data-rect="84 12 124 36 0" data-z="6" data-h="18" data-kind="furniture"><path data-role="silhouette" d="M 496 112 L 496 112 L 520 100 L 520 100 L 560 120 L 560 120 L 560 138 L 560 138 L 536 150 L 536 150 L 496 130 L 496 130 Z" fill="#ffffff"/><path d="M 496 112 L 496 112 L 536 132 L 536 132 L 536 150 L 536 150 L 496 130 L 496 130 Z" fill="rgba(45,49,66,0.07)"/><path d="M 536 132 L 536 132 L 560 120 L 560 120 L 560 138 L 560 138 L 536 150 L 536 150 Z" fill="rgba(45,49,66,0.15)"/><path d="M 496 112 L 496 112 L 536 132 L 536 132 L 560 120 L 560 120 M 536 132 L 536 150" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 496 112 L 496 112 L 520 100 L 520 100 L 560 120 L 560 120 L 560 138 L 560 138 L 536 150 L 536 150 L 496 130 L 496 130 Z" fill="none" stroke="#2d3142" stroke-width="0.8" stroke-linejoin="round"/></g>
        <g data-box data-rect="10 96 32 118 0" data-z="6" data-h="30" data-kind="furniture"><path data-role="silhouette" d="M 340 104 L 340 104 L 362 93 L 362 93 L 384 104 L 384 104 L 384 134 L 384 134 L 362 145 L 362 145 L 340 134 L 340 134 Z" fill="#ffffff"/><path d="M 340 104 L 340 104 L 362 115 L 362 115 L 362 145 L 362 145 L 340 134 L 340 134 Z" fill="rgba(45,49,66,0.07)"/><path d="M 362 115 L 362 115 L 384 104 L 384 104 L 384 134 L 384 134 L 362 145 L 362 145 Z" fill="rgba(45,49,66,0.15)"/><path d="M 340 104 L 340 104 L 362 115 L 362 115 L 384 104 L 384 104 M 362 115 L 362 145" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 340 104 L 340 104 L 362 93 L 362 93 L 384 104 L 384 104 L 384 134 L 384 134 L 362 145 L 362 145 L 340 134 L 340 134 Z" fill="none" stroke="#2d3142" stroke-width="0.8" stroke-linejoin="round"/></g>
