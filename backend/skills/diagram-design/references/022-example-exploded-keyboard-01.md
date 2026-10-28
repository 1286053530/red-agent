<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mechanical keyboard · Five layers under your fingers</title>
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
    <p class="eyebrow">Exploded axonometric · Diagram Design</p>
    <h1>Mechanical keyboard · Five layers under your fingers</h1>

    <div class="diagram-container">
      <svg viewBox="0 0 1000 736" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="exploded-keyboard-title exploded-keyboard-desc">
        <title id="exploded-keyboard-title">Mechanical keyboard · Five layers under your fingers</title>
        <desc id="exploded-keyboard-desc">Exploded view of a mechanical keyboard: the case, the PCB with hot-swap sockets, the steel plate, a switch for every key, and the keycaps on top, with the switches as the focal part.</desc>
        <rect width="100%" height="100%" fill="#f5f5f5"/>
        <g data-exploded data-origin="280 540" data-gap="116">
        <line data-role="trace" x1="183.51" y1="568" x2="183.51" y2="88" stroke="rgba(45,49,66,0.30)" stroke-width="0.8" stroke-dasharray="4,3"/><line data-role="trace" x1="504.49" y1="632" x2="504.49" y2="152" stroke="rgba(45,49,66,0.30)" stroke-width="0.8" stroke-dasharray="4,3"/>
        <g data-part="case" data-name="Case" data-rect="0 0 228 100 6" data-z="0" data-t="22" data-level="0" data-kind="housing"><path data-role="silhouette" d="M 183.51 568 A 8.49 4.24 0 0 1 186 565 L 274 521 A 8.49 4.24 0 0 1 286 521 L 502 629 A 8.49 4.24 0 0 1 504.49 632 L 504.49 654 A 8.49 4.24 0 0 1 502 657 L 414 701 A 8.49 4.24 0 0 1 402 701 L 186 593 A 8.49 4.24 0 0 1 183.51 590 Z" fill="#ffffff"/><path d="M 414 679 A 8.49 4.24 0 0 1 402 679 L 186 571 A 8.49 4.24 0 0 1 186 565 L 274 521 A 8.49 4.24 0 0 1 286 521 L 502 629 A 8.49 4.24 0 0 1 502 635 Z" fill="#ffffff"/><path d="M 409 676.5 A 1.41 0.71 0 0 1 407 676.5 L 191 568.5 A 1.41 0.71 0 0 1 191 567.5 L 279 523.5 A 1.41 0.71 0 0 1 281 523.5 L 497 631.5 A 1.41 0.71 0 0 1 497 632.5 Z" fill="#ffffff"/><path d="M 409 676.5 A 1.41 0.71 0 0 1 407 676.5 L 191 568.5 A 1.41 0.71 0 0 1 191 567.5 L 279 523.5 A 1.41 0.71 0 0 1 281 523.5 L 497 631.5 A 1.41 0.71 0 0 1 497 632.5 Z" fill="rgba(45,49,66,0.10)"/><clipPath id="exploded-keyboard-case-cavity"><path d="M 409 676.5 A 1.41 0.71 0 0 1 407 676.5 L 191 568.5 A 1.41 0.71 0 0 1 191 567.5 L 279 523.5 A 1.41 0.71 0 0 1 281 523.5 L 497 631.5 A 1.41 0.71 0 0 1 497 632.5 Z"/></clipPath><g clip-path="url(#exploded-keyboard-case-cavity)"><path d="M 409 695.5 A 1.41 0.71 0 0 1 407 695.5 L 191 587.5 A 1.41 0.71 0 0 1 191 586.5 L 279 542.5 A 1.41 0.71 0 0 1 281 542.5 L 497 650.5 A 1.41 0.71 0 0 1 497 651.5 Z" fill="#ffffff"/><path d="M 409 695.5 A 1.41 0.71 0 0 1 407 695.5 L 191 587.5 A 1.41 0.71 0 0 1 191 586.5 L 279 542.5 A 1.41 0.71 0 0 1 281 542.5 L 497 650.5 A 1.41 0.71 0 0 1 497 651.5 Z" fill="rgba(45,49,66,0.04)"/><path d="M 409 695.5 A 1.41 0.71 0 0 1 407 695.5 L 191 587.5 A 1.41 0.71 0 0 1 191 586.5 L 279 542.5 A 1.41 0.71 0 0 1 281 542.5 L 497 650.5 A 1.41 0.71 0 0 1 497 651.5 Z" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/></g><path d="M 409 676.5 A 1.41 0.71 0 0 1 407 676.5 L 191 568.5 A 1.41 0.71 0 0 1 191 567.5 L 279 523.5 A 1.41 0.71 0 0 1 281 523.5 L 497 631.5 A 1.41 0.71 0 0 1 497 632.5 Z" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 183.51 568 A 8.49 4.24 0 0 1 186 565 L 274 521 A 8.49 4.24 0 0 1 286 521 L 502 629 A 8.49 4.24 0 0 1 504.49 632" fill="none" stroke="#2d3142" stroke-width="1.2" stroke-linejoin="round"/><g data-role="label"><line data-role="leader" x1="510.49" y1="643" x2="556.49" y2="643" stroke="rgba(45,49,66,0.40)" stroke-width="0.8"/><circle cx="504.49" cy="643" r="2" fill="#2d3142"/><text data-role="name" x="568.49" y="642" fill="#2d3142" font-size="16" font-weight="600" font-family="'Geist', sans-serif">Case</text><text x="568.49" y="658" fill="#4f5d75" font-size="10" font-family="'Geist Mono', monospace" letter-spacing="0.08em">aluminium tray</text></g></g>
