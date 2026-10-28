<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Per-request latency, one dot per request · Beeswarm</title>
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
    body { font-family: var(--font-sans); background: var(--color-paper); color: var(--color-ink); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 3rem 2rem; }
    .frame { max-width: 1200px; width: 100%; }
    .eyebrow { font-family: var(--font-mono); font-size: 0.66rem; font-weight: 500; letter-spacing: 0.18em; text-transform: uppercase; color: var(--color-muted); margin-bottom: 0.5rem; }
    h1 { font-family: var(--font-serif); font-size: clamp(1.5rem, 2.4vw + 0.75rem, 2rem); font-weight: 400; letter-spacing: -0.02em; line-height: 1.15; margin-bottom: 1.5rem; }
    svg { width: 100%; min-width: 760px; display: block; }
  </style>
</head>
<body>
  <div class="frame">
    <p class="eyebrow">Beeswarm · Diagram Design</p>
    <h1>The median hides the tail</h1>

    <!-- Value axis: 0-440ms over 880px, x = 80 + 2*ms, linear from zero.
         The vertical (swarm) axis carries NO meaning: each dot's y offset is
         greedy packing at pitch 10 (2r+2) around the y=230 midline, first
         free slot alternating above/below, and overlap is never resolved by
         moving a dot along the value axis. scripts/verify-beeswarm.py derives
         the value scale from the dots themselves and flags any dot that
         disagrees with its peers, any overlapping pair, and any second dot
         radius or non-focal fill. -->
    <svg viewBox="0 0 1000 500" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="beeswarm-title beeswarm-desc">
      <title id="beeswarm-title">The median hides the tail</title>
      <desc id="beeswarm-desc">Beeswarm of 138 per-request latency samples for one checkout endpoint on a shared linear value axis from zero; vertical spread is packing only and carries no value, and three requests past 380 ms form the p99 tail.</desc>
      <defs>
        <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
          <circle cx="1" cy="1" r="0.9" fill="rgba(45,49,66,0.10)"/>
        </pattern>
      </defs>

      <rect width="100%" height="100%" fill="#f5f5f5"/>
      <rect width="100%" height="100%" fill="url(#dots)" opacity="0.55"/>

      <!-- Axis caption -->
      <text x="520" y="492" fill="#4f5d75" font-size="7" font-family="'Geist Mono', monospace" letter-spacing="0.14em" text-anchor="middle">PER-REQUEST LATENCY, MS</text>

      <!-- Vertical gridlines only: the swarm axis has no scale to grid.
           A horizontal rule through the band would invite reading the
           packing offsets as values, which they are not. -->
      <line x1="280" y1="40" x2="280" y2="420" stroke="rgba(45,49,66,0.08)" stroke-width="0.8"/>
      <line x1="480" y1="40" x2="480" y2="420" stroke="rgba(45,49,66,0.08)" stroke-width="0.8"/>
      <line x1="680" y1="40" x2="680" y2="420" stroke="rgba(45,49,66,0.08)" stroke-width="0.8"/>
      <line x1="880" y1="40" x2="880" y2="420" stroke="rgba(45,49,66,0.08)" stroke-width="0.8"/>

      <!-- Value axis, from zero. -->
      <line x1="80" y1="420" x2="960" y2="420" stroke="rgba(45,49,66,0.25)" stroke-width="1"/>

      <!-- Tick labels are BOUND: data-tick names the (one) value axis and
           data-value the number the tick claims to sit at. verify-beeswarm.py
           cross-checks each against the scale the dots themselves describe. -->
      <text data-tick="x" data-value="0" x="80" y="440" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">0</text>
      <text data-tick="x" data-value="100" x="280" y="440" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">100</text>
      <text data-tick="x" data-value="200" x="480" y="440" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">200</text>
      <text data-tick="x" data-value="300" x="680" y="440" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">300</text>
      <text data-tick="x" data-value="400" x="880" y="440" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">400</text>

      <!-- ─── THE SWARM. One dot = one request, every dot exactly at its
           value on the shared axis; the vertical offset is the greedy dodge
           and states nothing. One radius for every dot (size as a second
           encoding is a bubble chart) and one ink fill for every non-focal
           dot (opacity as a value encoding is banned while dodging). Each
           dot sits on a paper underlay so gridlines do not show through
           the translucent fill. -->
      <circle cx="184" cy="230" r="4" fill="#f5f5f5"/>
      <circle data-value="52" cx="184" cy="230" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="186" cy="220" r="4" fill="#f5f5f5"/>
      <circle data-value="53" cx="186" cy="220" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="190" cy="240" r="4" fill="#f5f5f5"/>
      <circle data-value="55" cx="190" cy="240" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="192" cy="210" r="4" fill="#f5f5f5"/>
      <circle data-value="56" cx="192" cy="210" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="200" cy="230" r="4" fill="#f5f5f5"/>
      <circle data-value="60" cx="200" cy="230" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="202" cy="220" r="4" fill="#f5f5f5"/>
      <circle data-value="61" cx="202" cy="220" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="202" cy="240" r="4" fill="#f5f5f5"/>
      <circle data-value="61" cx="202" cy="240" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="214" cy="230" r="4" fill="#f5f5f5"/>
      <circle data-value="67" cx="214" cy="230" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="218" cy="220" r="4" fill="#f5f5f5"/>
      <circle data-value="69" cx="218" cy="220" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="226" cy="230" r="4" fill="#f5f5f5"/>
      <circle data-value="73" cx="226" cy="230" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="232" cy="220" r="4" fill="#f5f5f5"/>
      <circle data-value="76" cx="232" cy="220" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="232" cy="240" r="4" fill="#f5f5f5"/>
      <circle data-value="76" cx="232" cy="240" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="234" cy="210" r="4" fill="#f5f5f5"/>
      <circle data-value="77" cx="234" cy="210" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="240" cy="230" r="4" fill="#f5f5f5"/>
      <circle data-value="80" cx="240" cy="230" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="240" cy="250" r="4" fill="#f5f5f5"/>
      <circle data-value="80" cx="240" cy="250" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="244" cy="220" r="4" fill="#f5f5f5"/>
      <circle data-value="82" cx="244" cy="220" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="244" cy="240" r="4" fill="#f5f5f5"/>
      <circle data-value="82" cx="244" cy="240" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="246" cy="210" r="4" fill="#f5f5f5"/>
      <circle data-value="83" cx="246" cy="210" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="248" cy="200" r="4" fill="#f5f5f5"/>
      <circle data-value="84" cx="248" cy="200" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="248" cy="260" r="4" fill="#f5f5f5"/>
      <circle data-value="84" cx="248" cy="260" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="248" cy="190" r="4" fill="#f5f5f5"/>
      <circle data-value="84" cx="248" cy="190" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="250" cy="230" r="4" fill="#f5f5f5"/>
      <circle data-value="85" cx="250" cy="230" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="250" cy="250" r="4" fill="#f5f5f5"/>
      <circle data-value="85" cx="250" cy="250" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="252" cy="270" r="4" fill="#f5f5f5"/>
