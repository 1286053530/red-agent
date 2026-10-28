<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Commerce schema · database schema</title>
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

    .frame { max-width: 1240px; width: 100%; }

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

    svg { width: 100%; min-width: 960px; display: block; }
  </style>
</head>
<body>
  <div class="frame">
    <p class="eyebrow">Database schema · Diagram Design</p>
    <h1>Commerce schema · public + billing</h1>

    <svg viewBox="0 0 1080 560" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="db-schema-title db-schema-desc">
      <title id="db-schema-title">Commerce schema · public + billing</title>
      <desc id="db-schema-desc">Physical database schema diagram showing five commerce tables with column-level foreign keys, SQL types, and constraint chips, including a cascading delete from orders into order_items and a billing schema group.</desc>
      <defs>
        <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#4f5d75"/></marker>
        <marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#bf4520"/></marker>
        <marker id="arrow-link" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#2e5aa8"/></marker>
      </defs>

      <rect width="100%" height="100%" fill="#f5f5f5"/>

      <!-- BILLING schema group (drawn first so tables paint over it) -->
      <rect x="744" y="332" width="272" height="152" rx="8" fill="rgba(45,49,66,0.02)" stroke="rgba(45,49,66,0.20)" stroke-width="0.8" stroke-dasharray="4,4"/>
      <text x="756" y="348" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" letter-spacing="0.14em">BILLING</text>

      <!-- FK connectors (drawn before boxes) -->
      <!-- FK1: orders.customer_id -> customers.id · ON DELETE RESTRICT -->
      <path d="M 400,104 H 348 Q 340,104 340,112 Q 340,120 332,120 H 280" fill="none" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>
      <!-- FK2: order_items.order_id -> orders.id · ON DELETE CASCADE (focal) -->
      <path d="M 640,384 H 660 Q 668,384 668,376 V 96 Q 668,88 660,88 H 640" fill="none" stroke="#bf4520" stroke-width="1.2" marker-end="url(#arrow-accent)"/>
      <!-- FK3: order_items.product_id -> products.id · ON DELETE RESTRICT -->
      <path d="M 640,408 H 708 Q 716,408 716,400 V 88 Q 716,80 724,80 H 760" fill="none" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>
      <!-- FK4: invoices.order_id -> orders.id · ON DELETE RESTRICT -->
      <path d="M 760,432 H 700 Q 692,432 692,424 V 416 a 8,8 0 0,0 0,-16 V 80 Q 692,72 684,72 H 640" fill="none" stroke="#4f5d75" stroke-width="1" marker-end="url(#arrow)"/>

      <!-- FK labels (masked, 6-10px gap above/beside their connector) -->
      <rect x="284" y="82" width="112" height="12" rx="2" fill="#f5f5f5"/>
      <text x="340" y="91" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.06em">ON DELETE RESTRICT</text>

      <rect x="572" y="274" width="88" height="12" rx="2" fill="#f5f5f5"/>
      <text x="616" y="283" fill="#bf4520" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.06em">ON DELETE CASCADE</text>

      <rect x="724" y="252" width="112" height="12" rx="2" fill="#f5f5f5"/>
      <text x="780" y="261" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.06em">ON DELETE RESTRICT</text>

      <rect x="644" y="440" width="112" height="12" rx="2" fill="#f5f5f5"/>
      <text x="700" y="449" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.06em">ON DELETE RESTRICT</text>

      <!-- Table: public.customers -->
      <rect x="40" y="80" width="240" height="100" rx="6" fill="#ffffff" stroke="#2d3142" stroke-width="1"/>
      <rect x="40" y="80" width="240" height="28" rx="6" fill="rgba(45,49,66,0.04)" stroke="none"/>
      <rect x="40" y="100" width="240" height="8" fill="rgba(45,49,66,0.04)"/>
      <line x1="40" y1="108" x2="280" y2="108" stroke="rgba(45,49,66,0.22)" stroke-width="1"/>
      <text x="52" y="98" fill="#2d3142" font-size="12" font-weight="600" font-family="'Geist', sans-serif">public.customers</text>
      <rect x="228" y="88" width="40" height="12" rx="2" fill="none" stroke="rgba(45,49,66,0.40)" stroke-width="0.8"/>
      <text x="248" y="97" fill="#2d3142" opacity="0.8" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.08em">TABLE</text>

      <rect x="40" y="108" width="240" height="24" fill="rgba(45,49,66,0.02)"/>
      <text x="52" y="124" fill="#2d3142" font-size="12" font-family="'Geist', sans-serif">id</text>
      <rect x="160" y="116" width="20" height="12" rx="2" fill="none" stroke="rgba(45,49,66,0.35)" stroke-width="0.8"/>
      <text x="170" y="125" fill="#2d3142" opacity="0.75" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">PK</text>
      <text x="268" y="124" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" text-anchor="end">uuid</text>

      <text x="52" y="148" fill="#2d3142" font-size="12" font-family="'Geist', sans-serif">email</text>
      <rect x="160" y="140" width="20" height="12" rx="2" fill="none" stroke="rgba(45,49,66,0.35)" stroke-width="0.8"/>
      <text x="170" y="149" fill="#2d3142" opacity="0.75" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">UQ</text>
      <rect x="184" y="140" width="20" height="12" rx="2" fill="none" stroke="rgba(45,49,66,0.35)" stroke-width="0.8"/>
      <text x="194" y="149" fill="#2d3142" opacity="0.75" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">NN</text>
      <text x="268" y="148" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" text-anchor="end">text</text>

      <rect x="40" y="156" width="240" height="24" fill="rgba(45,49,66,0.02)"/>
      <text x="52" y="172" fill="#2d3142" font-size="12" font-family="'Geist', sans-serif">created_at</text>
      <rect x="160" y="164" width="20" height="12" rx="2" fill="none" stroke="rgba(45,49,66,0.35)" stroke-width="0.8"/>
      <text x="170" y="173" fill="#2d3142" opacity="0.75" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">NN</text>
      <text x="268" y="172" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" text-anchor="end">timestamptz</text>

      <!-- Table: public.orders -->
      <rect x="400" y="40" width="240" height="200" rx="6" fill="#ffffff" stroke="#2d3142" stroke-width="1"/>
      <rect x="400" y="40" width="240" height="28" rx="6" fill="rgba(45,49,66,0.04)" stroke="none"/>
      <rect x="400" y="60" width="240" height="8" fill="rgba(45,49,66,0.04)"/>
      <line x1="400" y1="68" x2="640" y2="68" stroke="rgba(45,49,66,0.22)" stroke-width="1"/>
      <text x="412" y="58" fill="#2d3142" font-size="12" font-weight="600" font-family="'Geist', sans-serif">public.orders</text>
      <rect x="588" y="48" width="40" height="12" rx="2" fill="none" stroke="rgba(45,49,66,0.40)" stroke-width="0.8"/>
      <text x="608" y="57" fill="#2d3142" opacity="0.8" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.08em">TABLE</text>

      <rect x="400" y="68" width="240" height="24" fill="rgba(45,49,66,0.02)"/>
      <text x="412" y="84" fill="#2d3142" font-size="12" font-family="'Geist', sans-serif">id</text>
      <rect x="520" y="76" width="20" height="12" rx="2" fill="none" stroke="rgba(45,49,66,0.35)" stroke-width="0.8"/>
      <text x="530" y="85" fill="#2d3142" opacity="0.75" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle">PK</text>
      <text x="628" y="84" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" text-anchor="end">uuid</text>

      <text x="412" y="108" fill="#2d3142" font-size="12" font-family="'Geist', sans-serif">customer_id</text>
