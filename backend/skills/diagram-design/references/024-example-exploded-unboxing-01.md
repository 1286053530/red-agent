<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Unboxing · What you see, in the order you see it</title>
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
    <h1>Unboxing · What you see, in the order you see it</h1>

    <div class="diagram-container">
      <svg viewBox="0 0 1000 964" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="exploded-unboxing-title exploded-unboxing-desc">
        <title id="exploded-unboxing-title">Unboxing · What you see, in the order you see it</title>
        <desc id="exploded-unboxing-desc">Exploded view of product packaging: printed lid, the speaker and its cable, the moulded insert that holds them, and the rigid box, with the speaker as the focal part.</desc>
        <rect width="100%" height="100%" fill="#f5f5f5"/>
        <g data-exploded data-origin="348 752" data-gap="180">
        <line data-role="trace" x1="170.34" y1="770" x2="170.34" y2="158" stroke="rgba(45,49,66,0.30)" stroke-width="0.8" stroke-dasharray="4,3"/><line data-role="trace" x1="525.66" y1="770" x2="525.66" y2="158" stroke="rgba(45,49,66,0.30)" stroke-width="0.8" stroke-dasharray="4,3"/>
        <g data-part="box" data-name="Box" data-rect="0 0 180 180 4" data-z="0" data-t="72" data-level="0" data-kind="housing"><path data-role="silhouette" d="M 170.34 770 A 5.66 2.83 0 0 1 172 768 L 344 682 A 5.66 2.83 0 0 1 352 682 L 524 768 A 5.66 2.83 0 0 1 525.66 770 L 525.66 842 A 5.66 2.83 0 0 1 524 844 L 352 930 A 5.66 2.83 0 0 1 344 930 L 172 844 A 5.66 2.83 0 0 1 170.34 842 Z" fill="#ffffff"/><path d="M 352 858 A 5.66 2.83 0 0 1 344 858 L 172 772 A 5.66 2.83 0 0 1 172 768 L 344 682 A 5.66 2.83 0 0 1 352 682 L 524 768 A 5.66 2.83 0 0 1 524 772 Z" fill="#ffffff"/><path d="M 348 855 L 348 855 L 178 770 L 178 770 L 348 685 L 348 685 L 518 770 L 518 770 Z" fill="#ffffff"/><path d="M 348 855 L 348 855 L 178 770 L 178 770 L 348 685 L 348 685 L 518 770 L 518 770 Z" fill="rgba(45,49,66,0.10)"/><clipPath id="exploded-unboxing-box-cavity"><path d="M 348 855 L 348 855 L 178 770 L 178 770 L 348 685 L 348 685 L 518 770 L 518 770 Z"/></clipPath><g clip-path="url(#exploded-unboxing-box-cavity)"><path d="M 348 924 L 348 924 L 178 839 L 178 839 L 348 754 L 348 754 L 518 839 L 518 839 Z" fill="#ffffff"/><path d="M 348 924 L 348 924 L 178 839 L 178 839 L 348 754 L 348 754 L 518 839 L 518 839 Z" fill="rgba(45,49,66,0.04)"/><path d="M 348 924 L 348 924 L 178 839 L 178 839 L 348 754 L 348 754 L 518 839 L 518 839 Z" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/></g><path d="M 348 855 L 348 855 L 178 770 L 178 770 L 348 685 L 348 685 L 518 770 L 518 770 Z" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 170.34 770 A 5.66 2.83 0 0 1 172 768 L 344 682 A 5.66 2.83 0 0 1 352 682 L 524 768 A 5.66 2.83 0 0 1 525.66 770" fill="none" stroke="#2d3142" stroke-width="1.2" stroke-linejoin="round"/><g data-role="label"><line data-role="leader" x1="531.66" y1="806" x2="582.49" y2="806" stroke="rgba(45,49,66,0.40)" stroke-width="0.8"/><circle cx="525.66" cy="806" r="2" fill="#2d3142"/><text data-role="name" x="594.49" y="805" fill="#2d3142" font-size="16" font-weight="600" font-family="'Geist', sans-serif">Box</text><text x="594.49" y="821" fill="#4f5d75" font-size="10" font-family="'Geist Mono', monospace" letter-spacing="0.08em">rigid board</text></g></g>
        <g data-part="insert" data-name="Insert" data-rect="6 6 174 174 2" data-z="252" data-t="12" data-level="1"><path data-role="silhouette" d="M 181.17 578 A 2.83 1.41 0 0 1 182 577 L 346 495 A 2.83 1.41 0 0 1 350 495 L 514 577 A 2.83 1.41 0 0 1 514.83 578 L 514.83 590 A 2.83 1.41 0 0 1 514 591 L 350 673 A 2.83 1.41 0 0 1 346 673 L 182 591 A 2.83 1.41 0 0 1 181.17 590 Z" fill="#ffffff"/><path d="M 181.17 578 A 2.83 1.41 0 0 0 182 579 L 346 661 A 2.83 1.41 0 0 0 348 661.41 L 348 673.41 A 2.83 1.41 0 0 1 346 673 L 182 591 A 2.83 1.41 0 0 1 181.17 590 Z" fill="rgba(45,49,66,0.07)"/><path d="M 348 661.41 A 2.83 1.41 0 0 0 350 661 L 514 579 A 2.83 1.41 0 0 0 514.83 578 L 514.83 590 A 2.83 1.41 0 0 1 514 591 L 350 673 A 2.83 1.41 0 0 1 348 673.41 Z" fill="rgba(45,49,66,0.15)"/><path d="M 382 603 A 70.71 35.36 0 0 1 282 603 L 282 603 A 70.71 35.36 0 0 1 282 553 L 282 553 A 70.71 35.36 0 0 1 382 553 L 382 553 A 70.71 35.36 0 0 1 382 603 Z" fill="rgba(45,49,66,0.14)" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 451 609.5 A 7.07 3.54 0 0 1 441 609.5 L 413 595.5 A 7.07 3.54 0 0 1 413 590.5 L 441 576.5 A 7.07 3.54 0 0 1 451 576.5 L 479 590.5 A 7.07 3.54 0 0 1 479 595.5 Z" fill="rgba(45,49,66,0.14)" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 181.17 578 A 2.83 1.41 0 0 0 182 579 L 346 661 A 2.83 1.41 0 0 0 350 661 L 514 579 A 2.83 1.41 0 0 0 514.83 578" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 181.17 578 A 2.83 1.41 0 0 1 182 577 L 346 495 A 2.83 1.41 0 0 1 350 495 L 514 577 A 2.83 1.41 0 0 1 514.83 578 L 514.83 590 A 2.83 1.41 0 0 1 514 591 L 350 673 A 2.83 1.41 0 0 1 346 673 L 182 591 A 2.83 1.41 0 0 1 181.17 590 Z" fill="none" stroke="#2d3142" stroke-width="1.2" stroke-linejoin="round"/><g data-role="label"><line data-role="leader" x1="520.83" y1="584" x2="582.49" y2="584" stroke="rgba(45,49,66,0.40)" stroke-width="0.8"/><circle cx="514.83" cy="584" r="2" fill="#2d3142"/><text data-role="name" x="594.49" y="583" fill="#2d3142" font-size="16" font-weight="600" font-family="'Geist', sans-serif">Insert</text><text x="594.49" y="599" fill="#4f5d75" font-size="10" font-family="'Geist Mono', monospace" letter-spacing="0.08em">moulded pulp</text></g></g>
