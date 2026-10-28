<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Phone teardown · What sits under the glass</title>
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
    <h1>Phone teardown · What sits under the glass</h1>

    <div class="diagram-container">
      <svg viewBox="0 0 1000 624" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="exploded-phone-title exploded-phone-desc">
        <title id="exploded-phone-title">Phone teardown · What sits under the glass</title>
        <desc id="exploded-phone-desc">Exploded view of a phone: the display lifts off the housing to show the logic board and battery inside, with the logic board as the focal part.</desc>
        <rect width="100%" height="100%" fill="#f5f5f5"/>
        <g data-exploded data-origin="416 388" data-gap="160">
        <line data-role="trace" x1="150.06" y1="508" x2="150.06" y2="180" stroke="rgba(45,49,66,0.30)" stroke-width="0.8" stroke-dasharray="4,3"/><line data-role="trace" x1="541.94" y1="438" x2="541.94" y2="110" stroke="rgba(45,49,66,0.30)" stroke-width="0.8" stroke-dasharray="4,3"/>
        <g data-part="housing" data-name="Housing" data-rect="0 0 140 280 24" data-z="0" data-t="20" data-level="0" data-kind="housing"><path data-role="silhouette" d="M 150.06 508 A 33.94 16.97 0 0 1 160 496 L 392 380 A 33.94 16.97 0 0 1 440 380 L 532 426 A 33.94 16.97 0 0 1 541.94 438 L 541.94 458 A 33.94 16.97 0 0 1 532 470 L 300 586 A 33.94 16.97 0 0 1 252 586 L 160 540 A 33.94 16.97 0 0 1 150.06 528 Z" fill="#ffffff"/><path d="M 300 566 A 33.94 16.97 0 0 1 252 566 L 160 520 A 33.94 16.97 0 0 1 160 496 L 392 380 A 33.94 16.97 0 0 1 440 380 L 532 426 A 33.94 16.97 0 0 1 532 450 Z" fill="#ffffff"/><path d="M 295 563.5 A 26.87 13.44 0 0 1 257 563.5 L 165 517.5 A 26.87 13.44 0 0 1 165 498.5 L 397 382.5 A 26.87 13.44 0 0 1 435 382.5 L 527 428.5 A 26.87 13.44 0 0 1 527 447.5 Z" fill="#ffffff"/><path d="M 295 563.5 A 26.87 13.44 0 0 1 257 563.5 L 165 517.5 A 26.87 13.44 0 0 1 165 498.5 L 397 382.5 A 26.87 13.44 0 0 1 435 382.5 L 527 428.5 A 26.87 13.44 0 0 1 527 447.5 Z" fill="rgba(45,49,66,0.10)"/><clipPath id="exploded-phone-housing-cavity"><path d="M 295 563.5 A 26.87 13.44 0 0 1 257 563.5 L 165 517.5 A 26.87 13.44 0 0 1 165 498.5 L 397 382.5 A 26.87 13.44 0 0 1 435 382.5 L 527 428.5 A 26.87 13.44 0 0 1 527 447.5 Z"/></clipPath><g clip-path="url(#exploded-phone-housing-cavity)"><path d="M 295 580.5 A 26.87 13.44 0 0 1 257 580.5 L 165 534.5 A 26.87 13.44 0 0 1 165 515.5 L 397 399.5 A 26.87 13.44 0 0 1 435 399.5 L 527 445.5 A 26.87 13.44 0 0 1 527 464.5 Z" fill="#ffffff"/><path d="M 295 580.5 A 26.87 13.44 0 0 1 257 580.5 L 165 534.5 A 26.87 13.44 0 0 1 165 515.5 L 397 399.5 A 26.87 13.44 0 0 1 435 399.5 L 527 445.5 A 26.87 13.44 0 0 1 527 464.5 Z" fill="rgba(45,49,66,0.04)"/><path d="M 295 580.5 A 26.87 13.44 0 0 1 257 580.5 L 165 534.5 A 26.87 13.44 0 0 1 165 515.5 L 397 399.5 A 26.87 13.44 0 0 1 435 399.5 L 527 445.5 A 26.87 13.44 0 0 1 527 464.5 Z" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/></g><path d="M 295 563.5 A 26.87 13.44 0 0 1 257 563.5 L 165 517.5 A 26.87 13.44 0 0 1 165 498.5 L 397 382.5 A 26.87 13.44 0 0 1 435 382.5 L 527 428.5 A 26.87 13.44 0 0 1 527 447.5 Z" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 150.06 508 A 33.94 16.97 0 0 1 160 496 L 392 380 A 33.94 16.97 0 0 1 440 380 L 532 426 A 33.94 16.97 0 0 1 541.94 438" fill="none" stroke="#2d3142" stroke-width="1.2" stroke-linejoin="round"/><g data-role="label"><line data-role="leader" x1="547.94" y1="448" x2="593.94" y2="448" stroke="rgba(45,49,66,0.40)" stroke-width="0.8"/><circle cx="541.94" cy="448" r="2" fill="#2d3142"/><text data-role="name" x="605.94" y="447" fill="#2d3142" font-size="16" font-weight="600" font-family="'Geist', sans-serif">Housing</text><text x="605.94" y="463" fill="#4f5d75" font-size="10" font-family="'Geist Mono', monospace" letter-spacing="0.08em">aluminium frame</text></g></g>
