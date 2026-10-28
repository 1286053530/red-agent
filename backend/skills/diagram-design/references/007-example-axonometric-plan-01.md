<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Level 3 office · Where the team actually sits</title>
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
    <h1>Level 3 office · Where the team actually sits</h1>

    <div class="diagram-container">
      <svg viewBox="0 0 1000 448" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="axonometric-plan-title axonometric-plan-desc">
        <title id="axonometric-plan-title">Level 3 office · Where the team actually sits</title>
        <desc id="axonometric-plan-desc">Axonometric floor plan of an office level with an open office, meeting room, kitchen, lobby, and phone booth, with the meeting room as the focal room.</desc>
        <rect width="100%" height="100%" fill="#f5f5f5"/>
        <g data-axo-plan data-origin="440 76">
        <g data-plate data-rect="0 0 360 240 0" data-z="0" data-t="6"><path data-role="silhouette" d="M 200 190 L 200 190 L 440 70 L 440 70 L 800 250 L 800 250 L 800 256 L 800 256 L 560 376 L 560 376 L 200 196 L 200 196 Z" fill="#ffffff"/><path d="M 200 190 L 200 190 L 560 370 L 560 370 L 560 376 L 560 376 L 200 196 L 200 196 Z" fill="rgba(45,49,66,0.07)"/><path d="M 560 370 L 560 370 L 800 250 L 800 250 L 800 256 L 800 256 L 560 376 L 560 376 Z" fill="rgba(45,49,66,0.15)"/><path d="M 200 190 L 200 190 L 560 370 L 560 370 L 800 250 L 800 250 M 560 370 L 560 376" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 200 190 L 200 190 L 440 70 L 440 70 L 800 250 L 800 250 L 800 256 L 800 256 L 560 376 L 560 376 L 200 196 L 200 196 Z" fill="none" stroke="#2d3142" stroke-width="1.2" stroke-linejoin="round"/></g>
        <g data-room data-name="Open office" data-rect="6 6 214 140 0"></g>
        <g data-room data-name="Meeting room" data-rect="220 6 354 100 0" data-focal><path d="M 694 297 L 694 297 L 560 230 L 560 230 L 654 183 L 654 183 L 788 250 L 788 250 Z" fill="rgba(191,69,32,0.12)"/></g>
        <g data-room data-name="Kitchen" data-rect="220 106 354 234 0"></g>
        <g data-room data-name="Lobby" data-rect="6 146 164 234 0"></g>
        <g data-room data-name="Booth" data-rect="170 146 214 234 0"></g>
        <g data-box data-rect="0 0 360 6 0" data-z="6" data-h="22" data-kind="wall"><path data-role="silhouette" d="M 434 51 L 434 51 L 440 48 L 440 48 L 800 228 L 800 228 L 800 250 L 800 250 L 794 253 L 794 253 L 434 73 L 434 73 Z" fill="#ffffff"/><path d="M 434 51 L 434 51 L 794 231 L 794 231 L 794 253 L 794 253 L 434 73 L 434 73 Z" fill="rgba(45,49,66,0.07)"/><path d="M 794 231 L 794 231 L 800 228 L 800 228 L 800 250 L 800 250 L 794 253 L 794 253 Z" fill="rgba(45,49,66,0.15)"/><path d="M 434 51 L 434 51 L 794 231 L 794 231 L 800 228 L 800 228 M 794 231 L 794 253" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 434 51 L 434 51 L 440 48 L 440 48 L 800 228 L 800 228 L 800 250 L 800 250 L 794 253 L 794 253 L 434 73 L 434 73 Z" fill="none" stroke="#2d3142" stroke-width="1.0" stroke-linejoin="round"/></g>
        <g data-box data-rect="0 6 6 240 0" data-z="6" data-h="22" data-kind="wall"><path data-role="silhouette" d="M 200 168 L 200 168 L 434 51 L 434 51 L 440 54 L 440 54 L 440 76 L 440 76 L 206 193 L 206 193 L 200 190 L 200 190 Z" fill="#ffffff"/><path d="M 200 168 L 200 168 L 206 171 L 206 171 L 206 193 L 206 193 L 200 190 L 200 190 Z" fill="rgba(45,49,66,0.07)"/><path d="M 206 171 L 206 171 L 440 54 L 440 54 L 440 76 L 440 76 L 206 193 L 206 193 Z" fill="rgba(45,49,66,0.15)"/><path d="M 200 168 L 200 168 L 206 171 L 206 171 L 440 54 L 440 54 M 206 171 L 206 193" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 200 168 L 200 168 L 434 51 L 434 51 L 440 54 L 440 54 L 440 76 L 440 76 L 206 193 L 206 193 L 200 190 L 200 190 Z" fill="none" stroke="#2d3142" stroke-width="1.0" stroke-linejoin="round"/></g>
        <g data-box data-rect="24 28 68 52 0" data-z="6" data-h="10" data-kind="furniture"><path data-role="silhouette" d="M 412 98 L 412 98 L 436 86 L 436 86 L 480 108 L 480 108 L 480 118 L 480 118 L 456 130 L 456 130 L 412 108 L 412 108 Z" fill="#ffffff"/><path d="M 412 98 L 412 98 L 456 120 L 456 120 L 456 130 L 456 130 L 412 108 L 412 108 Z" fill="rgba(45,49,66,0.07)"/><path d="M 456 120 L 456 120 L 480 108 L 480 108 L 480 118 L 480 118 L 456 130 L 456 130 Z" fill="rgba(45,49,66,0.15)"/><path d="M 456 117 L 456 117 L 418 98 L 418 98 L 436 89 L 436 89 L 474 108 L 474 108 Z" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.6"/><path d="M 412 98 L 412 98 L 456 120 L 456 120 L 480 108 L 480 108 M 456 120 L 456 130" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 412 98 L 412 98 L 436 86 L 436 86 L 480 108 L 480 108 L 480 118 L 480 118 L 456 130 L 456 130 L 412 108 L 412 108 Z" fill="none" stroke="#2d3142" stroke-width="0.8" stroke-linejoin="round"/></g>
        <g data-box data-rect="24 84 68 108 0" data-z="6" data-h="10" data-kind="furniture"><path data-role="silhouette" d="M 356 126 L 356 126 L 380 114 L 380 114 L 424 136 L 424 136 L 424 146 L 424 146 L 400 158 L 400 158 L 356 136 L 356 136 Z" fill="#ffffff"/><path d="M 356 126 L 356 126 L 400 148 L 400 148 L 400 158 L 400 158 L 356 136 L 356 136 Z" fill="rgba(45,49,66,0.07)"/><path d="M 400 148 L 400 148 L 424 136 L 424 136 L 424 146 L 424 146 L 400 158 L 400 158 Z" fill="rgba(45,49,66,0.15)"/><path d="M 400 145 L 400 145 L 362 126 L 362 126 L 380 117 L 380 117 L 418 136 L 418 136 Z" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.6"/><path d="M 356 126 L 356 126 L 400 148 L 400 148 L 424 136 L 424 136 M 400 148 L 400 158" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 356 126 L 356 126 L 380 114 L 380 114 L 424 136 L 424 136 L 424 146 L 424 146 L 400 158 L 400 158 L 356 136 L 356 136 Z" fill="none" stroke="#2d3142" stroke-width="0.8" stroke-linejoin="round"/></g>
        <g data-box data-rect="84 28 128 52 0" data-z="6" data-h="10" data-kind="furniture"><path data-role="silhouette" d="M 472 128 L 472 128 L 496 116 L 496 116 L 540 138 L 540 138 L 540 148 L 540 148 L 516 160 L 516 160 L 472 138 L 472 138 Z" fill="#ffffff"/><path d="M 472 128 L 472 128 L 516 150 L 516 150 L 516 160 L 516 160 L 472 138 L 472 138 Z" fill="rgba(45,49,66,0.07)"/><path d="M 516 150 L 516 150 L 540 138 L 540 138 L 540 148 L 540 148 L 516 160 L 516 160 Z" fill="rgba(45,49,66,0.15)"/><path d="M 516 147 L 516 147 L 478 128 L 478 128 L 496 119 L 496 119 L 534 138 L 534 138 Z" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.6"/><path d="M 472 128 L 472 128 L 516 150 L 516 150 L 540 138 L 540 138 M 516 150 L 516 160" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 472 128 L 472 128 L 496 116 L 496 116 L 540 138 L 540 138 L 540 148 L 540 148 L 516 160 L 516 160 L 472 138 L 472 138 Z" fill="none" stroke="#2d3142" stroke-width="0.8" stroke-linejoin="round"/></g>
        <g data-box data-rect="6 140 60 146 0" data-z="6" data-h="22" data-kind="wall"><path data-role="silhouette" d="M 300 124 L 300 124 L 306 121 L 306 121 L 360 148 L 360 148 L 360 170 L 360 170 L 354 173 L 354 173 L 300 146 L 300 146 Z" fill="#ffffff"/><path d="M 300 124 L 300 124 L 354 151 L 354 151 L 354 173 L 354 173 L 300 146 L 300 146 Z" fill="rgba(45,49,66,0.07)"/><path d="M 354 151 L 354 151 L 360 148 L 360 148 L 360 170 L 360 170 L 354 173 L 354 173 Z" fill="rgba(45,49,66,0.15)"/><path d="M 300 124 L 300 124 L 354 151 L 354 151 L 360 148 L 360 148 M 354 151 L 354 173" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 300 124 L 300 124 L 306 121 L 306 121 L 360 148 L 360 148 L 360 170 L 360 170 L 354 173 L 354 173 L 300 146 L 300 146 Z" fill="none" stroke="#2d3142" stroke-width="1.0" stroke-linejoin="round"/></g>
