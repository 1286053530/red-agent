        <rect x="288" y="80" width="32" height="12" rx="2" fill="transparent" stroke="rgba(45,49,66,0.22)" stroke-width="0.8"/>
        <text x="304" y="89" fill="#5a6580" font-size="7" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.08em">EDGE</text>
        <text x="352" y="104" fill="#2d3142" font-size="12" font-weight="600" font-family="'Geist', sans-serif" text-anchor="middle">Cloudflare</text>
        <text x="352" y="119" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" text-anchor="middle">Pages · cache</text>

        <!-- Actor 3: Astro Origin (focal / coral) -->
        <rect x="504" y="72" width="160" height="56" rx="6" fill="#f5f5f5"/>
        <rect x="504" y="72" width="160" height="56" rx="6" fill="rgba(191,69,32,0.08)" stroke="#bf4520" stroke-width="1"/>
        <rect x="512" y="80" width="32" height="12" rx="2" fill="transparent" stroke="rgba(191,69,32,0.50)" stroke-width="0.8"/>
        <text x="528" y="89" fill="#bf4520" font-size="7" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.08em">ORIG</text>
        <text x="584" y="104" fill="#2d3142" font-size="12" font-weight="600" font-family="'Geist', sans-serif" text-anchor="middle">Astro Origin</text>
        <text x="584" y="119" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" text-anchor="middle">SSR + MDX</text>

        <!-- Actor 4: Analytics (optional / dashed) -->
        <rect x="728" y="72" width="144" height="56" rx="6" fill="#f5f5f5"/>
        <rect x="728" y="72" width="144" height="56" rx="6" fill="rgba(45,49,66,0.02)" stroke="rgba(45,49,66,0.22)" stroke-width="1" stroke-dasharray="4,3"/>
        <rect x="736" y="80" width="28" height="12" rx="2" fill="transparent" stroke="rgba(45,49,66,0.22)" stroke-width="0.8"/>
        <text x="750" y="89" fill="#5a6580" font-size="7" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.08em">ASY</text>
        <text x="800" y="104" fill="#2d3142" font-size="12" font-weight="600" font-family="'Geist', sans-serif" text-anchor="middle">Analytics</text>
        <text x="800" y="119" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" text-anchor="middle">Beacon · async</text>

        <!-- =================================================================
             LEGEND — horizontal strip at the bottom.
             Separator at y=504, eyebrow at y=520, items at y=540–548.
             ================================================================= -->
        <line x1="56" y1="504" x2="944" y2="504" stroke="rgba(45,49,66,0.10)" stroke-width="0.8"/>
        <text x="56" y="520" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" letter-spacing="0.18em">LEGEND</text>

        <!-- Item 1: Actor swatch (coral focal) -->
        <rect x="56" y="540" width="14" height="10" rx="2" fill="rgba(191,69,32,0.08)" stroke="#bf4520" stroke-width="1"/>
        <text x="76" y="548" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Focal actor</text>

        <!-- Item 2: Activation bar swatch -->
        <rect x="188" y="536" width="4" height="18" fill="rgba(45,49,66,0.06)" stroke="#4f5d75" stroke-width="0.8"/>
        <text x="200" y="548" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Activation</text>

        <!-- Item 3: Request arrow (link-blue) -->
        <line x1="308" y1="546" x2="336" y2="546" stroke="#2e5aa8" stroke-width="1.2" marker-end="url(#arrow-link)"/>
        <text x="344" y="548" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">HTTP request</text>

        <!-- Item 4: Return / async (muted dashed) -->
        <line x1="476" y1="546" x2="504" y2="546" stroke="#4f5d75" stroke-width="1.2" stroke-dasharray="5,4" marker-end="url(#arrow)"/>
        <text x="512" y="548" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Return / async</text>

        <!-- Item 5: Primary response (coral) -->
        <line x1="652" y1="546" x2="680" y2="546" stroke="#bf4520" stroke-width="1.4" marker-end="url(#arrow-accent)"/>
        <text x="688" y="548" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Primary response</text>

      </svg>
  </div>
</body>
</html>
