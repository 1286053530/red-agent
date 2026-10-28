<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Fulfillment floor · Dock to dock</title>
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
    <h1>Fulfillment floor · Dock to dock</h1>

    <div class="diagram-container">
      <svg viewBox="0 0 1000 528" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="axonometric-plan-warehouse-title axonometric-plan-warehouse-desc">
        <title id="axonometric-plan-warehouse-title">Fulfillment floor · Dock to dock</title>
        <desc id="axonometric-plan-warehouse-desc">Axonometric plan of a fulfillment warehouse: receiving docks, storage racks, a pick zone, packing stations, and shipping docks, with packing as the focal zone.</desc>
        <rect width="100%" height="100%" fill="#f5f5f5"/>
        <g data-axo-plan data-origin="420 76">
        <g data-plate data-rect="0 0 460 300 0" data-z="0" data-t="6"><path data-role="silhouette" d="M 120 220 L 120 220 L 420 70 L 420 70 L 880 300 L 880 300 L 880 306 L 880 306 L 580 456 L 580 456 L 120 226 L 120 226 Z" fill="#ffffff"/><path d="M 120 220 L 120 220 L 580 450 L 580 450 L 580 456 L 580 456 L 120 226 L 120 226 Z" fill="rgba(45,49,66,0.07)"/><path d="M 580 450 L 580 450 L 880 300 L 880 300 L 880 306 L 880 306 L 580 456 L 580 456 Z" fill="rgba(45,49,66,0.15)"/><path d="M 120 220 L 120 220 L 580 450 L 580 450 L 880 300 L 880 300 M 580 450 L 580 456" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 120 220 L 120 220 L 420 70 L 420 70 L 880 300 L 880 300 L 880 306 L 880 306 L 580 456 L 580 456 L 120 226 L 120 226 Z" fill="none" stroke="#2d3142" stroke-width="1.2" stroke-linejoin="round"/></g>
        <path d="M 368 114 L 368 114 L 356 108 L 356 108 L 396 88 L 396 88 L 408 94 L 408 94 Z" fill="rgba(45,49,66,0.07)"/>
        <path d="M 278 159 L 278 159 L 266 153 L 266 153 L 306 133 L 306 133 L 318 139 L 318 139 Z" fill="rgba(45,49,66,0.07)"/>
        <path d="M 188 204 L 188 204 L 176 198 L 176 198 L 216 178 L 216 178 L 228 184 L 228 184 Z" fill="rgba(45,49,66,0.07)"/>
        <line x1="510" y1="121" x2="222" y2="265" stroke="rgba(45,49,66,0.25)" stroke-width="0.8" stroke-dasharray="6,5"/>
        <line x1="720" y1="226" x2="432" y2="370" stroke="rgba(45,49,66,0.25)" stroke-width="0.8" stroke-dasharray="6,5"/>
        <line x1="794" y1="263" x2="506" y2="407" stroke="rgba(45,49,66,0.25)" stroke-width="0.8" stroke-dasharray="6,5"/>
        <line x1="320" y1="216" x2="530" y2="321" stroke="rgba(45,49,66,0.25)" stroke-width="0.8" stroke-dasharray="6,5"/>
        <g data-room data-name="Receiving" data-rect="6 6 96 294 0"></g>
        <g data-room data-name="Storage" data-rect="96 6 306 196 0"></g>
        <g data-room data-name="Pick zone" data-rect="96 196 306 294 0"></g>
        <g data-room data-name="Packing" data-rect="306 6 380 294 0" data-focal><path d="M 506 407 L 506 407 L 432 370 L 432 370 L 720 226 L 720 226 L 794 263 L 794 263 Z" fill="rgba(191,69,32,0.12)"/></g>
        <g data-room data-name="Shipping" data-rect="380 6 454 294 0"></g>
        <g data-box data-rect="0 0 460 6 0" data-z="6" data-h="22" data-kind="wall"><path data-role="silhouette" d="M 414 51 L 414 51 L 420 48 L 420 48 L 880 278 L 880 278 L 880 300 L 880 300 L 874 303 L 874 303 L 414 73 L 414 73 Z" fill="#ffffff"/><path d="M 414 51 L 414 51 L 874 281 L 874 281 L 874 303 L 874 303 L 414 73 L 414 73 Z" fill="rgba(45,49,66,0.07)"/><path d="M 874 281 L 874 281 L 880 278 L 880 278 L 880 300 L 880 300 L 874 303 L 874 303 Z" fill="rgba(45,49,66,0.15)"/><path d="M 414 51 L 414 51 L 874 281 L 874 281 L 880 278 L 880 278 M 874 281 L 874 303" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 414 51 L 414 51 L 420 48 L 420 48 L 880 278 L 880 278 L 880 300 L 880 300 L 874 303 L 874 303 L 414 73 L 414 73 Z" fill="none" stroke="#2d3142" stroke-width="1.0" stroke-linejoin="round"/></g>
        <g data-box data-rect="0 6 6 30 0" data-z="6" data-h="22" data-kind="wall"><path data-role="silhouette" d="M 390 63 L 390 63 L 414 51 L 414 51 L 420 54 L 420 54 L 420 76 L 420 76 L 396 88 L 396 88 L 390 85 L 390 85 Z" fill="#ffffff"/><path d="M 390 63 L 390 63 L 396 66 L 396 66 L 396 88 L 396 88 L 390 85 L 390 85 Z" fill="rgba(45,49,66,0.07)"/><path d="M 396 66 L 396 66 L 420 54 L 420 54 L 420 76 L 420 76 L 396 88 L 396 88 Z" fill="rgba(45,49,66,0.15)"/><path d="M 390 63 L 390 63 L 396 66 L 396 66 L 420 54 L 420 54 M 396 66 L 396 88" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 390 63 L 390 63 L 414 51 L 414 51 L 420 54 L 420 54 L 420 76 L 420 76 L 396 88 L 396 88 L 390 85 L 390 85 Z" fill="none" stroke="#2d3142" stroke-width="1.0" stroke-linejoin="round"/></g>
        <g data-box data-rect="0 70 6 120 0" data-z="6" data-h="22" data-kind="wall"><path data-role="silhouette" d="M 300 108 L 300 108 L 350 83 L 350 83 L 356 86 L 356 86 L 356 108 L 356 108 L 306 133 L 306 133 L 300 130 L 300 130 Z" fill="#ffffff"/><path d="M 300 108 L 300 108 L 306 111 L 306 111 L 306 133 L 306 133 L 300 130 L 300 130 Z" fill="rgba(45,49,66,0.07)"/><path d="M 306 111 L 306 111 L 356 86 L 356 86 L 356 108 L 356 108 L 306 133 L 306 133 Z" fill="rgba(45,49,66,0.15)"/><path d="M 300 108 L 300 108 L 306 111 L 306 111 L 356 86 L 356 86 M 306 111 L 306 133" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 300 108 L 300 108 L 350 83 L 350 83 L 356 86 L 356 86 L 356 108 L 356 108 L 306 133 L 306 133 L 300 130 L 300 130 Z" fill="none" stroke="#2d3142" stroke-width="1.0" stroke-linejoin="round"/></g>
        <g data-box data-rect="36 36 64 64 0" data-z="6" data-h="14" data-kind="furniture"><path data-role="silhouette" d="M 392 106 L 392 106 L 420 92 L 420 92 L 448 106 L 448 106 L 448 120 L 448 120 L 420 134 L 420 134 L 392 120 L 392 120 Z" fill="#ffffff"/><path d="M 392 106 L 392 106 L 420 120 L 420 120 L 420 134 L 420 134 L 392 120 L 392 120 Z" fill="rgba(45,49,66,0.07)"/><path d="M 420 120 L 420 120 L 448 106 L 448 106 L 448 120 L 448 120 L 420 134 L 420 134 Z" fill="rgba(45,49,66,0.15)"/><path d="M 420 117 L 420 117 L 398 106 L 398 106 L 420 95 L 420 95 L 442 106 L 442 106 Z" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.6"/><path d="M 392 106 L 392 106 L 420 120 L 420 120 L 448 106 L 448 106 M 420 120 L 420 134" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 392 106 L 392 106 L 420 92 L 420 92 L 448 106 L 448 106 L 448 120 L 448 120 L 420 134 L 420 134 L 392 120 L 392 120 Z" fill="none" stroke="#2d3142" stroke-width="0.8" stroke-linejoin="round"/></g>
