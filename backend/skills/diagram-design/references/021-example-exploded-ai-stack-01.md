<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI agent stack · What sits under the prompt</title>
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
    <h1>AI agent stack · What sits under the prompt</h1>

    <div class="diagram-container">
      <svg viewBox="0 0 1000 808" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="exploded-ai-stack-title exploded-ai-stack-desc">
        <title id="exploded-ai-stack-title">AI agent stack · What sits under the prompt</title>
        <desc id="exploded-ai-stack-desc">Exploded view of an AI agent stack: a secrets vault at the base, then tools, skills, the agent harness that runs the model, and the chat or terminal interface on top, with skills as the focal layer.</desc>
        <rect width="100%" height="100%" fill="#f5f5f5"/>
        <g data-exploded data-origin="348 592" data-gap="120">
        <line data-role="trace" x1="224.69" y1="648" x2="224.69" y2="126" stroke="rgba(45,49,66,0.30)" stroke-width="0.8" stroke-dasharray="4,3"/><line data-role="trace" x1="471.31" y1="648" x2="471.31" y2="126" stroke="rgba(45,49,66,0.30)" stroke-width="0.8" stroke-dasharray="4,3"/>
        <g data-part="vault" data-name="Secrets vault" data-rect="16 16 144 144 8" data-z="0" data-t="24" data-level="0"><path data-role="silhouette" d="M 224.69 648 A 11.31 5.66 0 0 1 228 644 L 340 588 A 11.31 5.66 0 0 1 356 588 L 468 644 A 11.31 5.66 0 0 1 471.31 648 L 471.31 672 A 11.31 5.66 0 0 1 468 676 L 356 732 A 11.31 5.66 0 0 1 340 732 L 228 676 A 11.31 5.66 0 0 1 224.69 672 Z" fill="#ffffff"/><path d="M 224.69 648 A 11.31 5.66 0 0 0 228 652 L 340 708 A 11.31 5.66 0 0 0 348 709.66 L 348 733.66 A 11.31 5.66 0 0 1 340 732 L 228 676 A 11.31 5.66 0 0 1 224.69 672 Z" fill="rgba(45,49,66,0.07)"/><path d="M 348 709.66 A 11.31 5.66 0 0 0 356 708 L 468 652 A 11.31 5.66 0 0 0 471.31 648 L 471.31 672 A 11.31 5.66 0 0 1 468 676 L 356 732 A 11.31 5.66 0 0 1 348 733.66 Z" fill="rgba(45,49,66,0.15)"/><path d="M 224.69 648 A 11.31 5.66 0 0 0 228 652 L 340 708 A 11.31 5.66 0 0 0 356 708 L 468 652 A 11.31 5.66 0 0 0 471.31 648" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 224.69 648 A 11.31 5.66 0 0 1 228 644 L 340 588 A 11.31 5.66 0 0 1 356 588 L 468 644 A 11.31 5.66 0 0 1 471.31 648 L 471.31 672 A 11.31 5.66 0 0 1 468 676 L 356 732 A 11.31 5.66 0 0 1 340 732 L 228 676 A 11.31 5.66 0 0 1 224.69 672 Z" fill="none" stroke="#2d3142" stroke-width="1.2" stroke-linejoin="round"/><path d="M 348 700 L 348 700 L 244 648 L 244 648 L 348 596 L 348 596 L 452 648 L 452 648 Z" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 322.54 643 A 25.46 12.73 0 0 1 330 634 L 330 634 A 25.46 12.73 0 0 1 366 634 L 366 634 A 25.46 12.73 0 0 1 373.46 643 L 373.46 648 A 25.46 12.73 0 0 1 366 657 L 366 657 A 25.46 12.73 0 0 1 330 657 L 330 657 A 25.46 12.73 0 0 1 322.54 648 Z" fill="#ffffff"/><path d="M 322.54 643 A 25.46 12.73 0 0 0 330 652 L 330 652 A 25.46 12.73 0 0 0 348 655.73 L 348 660.73 A 25.46 12.73 0 0 1 330 657 L 330 657 A 25.46 12.73 0 0 1 322.54 648 Z" fill="rgba(45,49,66,0.07)"/><path d="M 348 655.73 A 25.46 12.73 0 0 0 366 652 L 366 652 A 25.46 12.73 0 0 0 373.46 643 L 373.46 648 A 25.46 12.73 0 0 1 366 657 L 366 657 A 25.46 12.73 0 0 1 348 660.73 Z" fill="rgba(45,49,66,0.15)"/><path d="M 322.54 643 A 25.46 12.73 0 0 0 330 652 L 330 652 A 25.46 12.73 0 0 0 366 652 L 366 652 A 25.46 12.73 0 0 0 373.46 643" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.5"/><path d="M 322.54 643 A 25.46 12.73 0 0 1 330 634 L 330 634 A 25.46 12.73 0 0 1 366 634 L 366 634 A 25.46 12.73 0 0 1 373.46 643 L 373.46 648 A 25.46 12.73 0 0 1 366 657 L 366 657 A 25.46 12.73 0 0 1 330 657 L 330 657 A 25.46 12.73 0 0 1 322.54 648 Z" fill="none" stroke="#2d3142" stroke-width="0.8" stroke-linejoin="round"/><path d="M 360 649 A 16.97 8.49 0 0 1 336 649 L 336 649 A 16.97 8.49 0 0 1 336 637 L 336 637 A 16.97 8.49 0 0 1 360 637 L 360 637 A 16.97 8.49 0 0 1 360 649 Z" fill="none" stroke="rgba(45,49,66,0.55)" stroke-width="0.8"/><path d="M 352 645 A 5.66 2.83 0 0 1 344 645 L 344 645 A 5.66 2.83 0 0 1 344 641 L 344 641 A 5.66 2.83 0 0 1 352 641 L 352 641 A 5.66 2.83 0 0 1 352 645 Z" fill="#4f5d75"/><g data-role="label"><line data-role="leader" x1="477.31" y1="660" x2="554.14" y2="660" stroke="rgba(45,49,66,0.40)" stroke-width="0.8"/><circle cx="471.31" cy="660" r="2" fill="#2d3142"/><text data-role="name" x="566.14" y="659" fill="#2d3142" font-size="16" font-weight="600" font-family="'Geist', sans-serif">Secrets vault</text><text x="566.14" y="675" fill="#4f5d75" font-size="10" font-family="'Geist Mono', monospace" letter-spacing="0.08em">scoped service token</text></g></g>
