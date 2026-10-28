        <!-- Entity: Tag -->
        <rect x="780" y="120" width="200" height="128" rx="6" fill="#ffffff" stroke="#2d3142" stroke-width="1"/>
        <rect x="780" y="120" width="200" height="40" rx="6" fill="rgba(45,49,66,0.04)" stroke="none"/>
        <rect x="780" y="152" width="200" height="8" fill="rgba(45,49,66,0.04)"/>
        <line x1="780" y1="160" x2="980" y2="160" stroke="rgba(45,49,66,0.22)" stroke-width="1"/>
        <text x="796" y="136" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" letter-spacing="0.14em">ENTITY</text>
        <text x="796" y="152" fill="#2d3142" font-size="14" font-weight="600" font-family="'Geist', sans-serif">Tag</text>
        <text x="796" y="180" fill="#2d3142" font-size="10" font-family="'Geist Mono', monospace"># id</text>
        <text x="940" y="180" fill="#4f5d75" font-size="10" font-family="'Geist Mono', monospace" text-anchor="end">uuid</text>
        <text x="796" y="200" fill="#2d3142" font-size="10" font-family="'Geist Mono', monospace">slug</text>
        <text x="940" y="200" fill="#4f5d75" font-size="10" font-family="'Geist Mono', monospace" text-anchor="end">text · unique</text>
        <text x="796" y="220" fill="#2d3142" font-size="10" font-family="'Geist Mono', monospace">name</text>
        <text x="940" y="220" fill="#4f5d75" font-size="10" font-family="'Geist Mono', monospace" text-anchor="end">text</text>
        <text x="796" y="240" fill="#2d3142" font-size="10" font-family="'Geist Mono', monospace">description</text>
        <text x="940" y="240" fill="#4f5d75" font-size="10" font-family="'Geist Mono', monospace" text-anchor="end">text</text>

        <!-- Entity: ArticleTag (join) -->
        <rect x="780" y="280" width="200" height="96" rx="6" fill="rgba(45,49,66,0.04)" stroke="#4f5d75" stroke-width="1" stroke-dasharray="4,3"/>
        <rect x="780" y="280" width="200" height="40" rx="6" fill="rgba(45,49,66,0.06)" stroke="none"/>
        <rect x="780" y="312" width="200" height="8" fill="rgba(45,49,66,0.06)"/>
        <line x1="780" y1="320" x2="980" y2="320" stroke="rgba(45,49,66,0.22)" stroke-width="1"/>
        <text x="796" y="296" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" letter-spacing="0.14em">JOIN</text>
        <text x="796" y="312" fill="#2d3142" font-size="14" font-weight="600" font-family="'Geist', sans-serif">ArticleTag</text>
        <text x="796" y="340" fill="#2d3142" font-size="10" font-family="'Geist Mono', monospace">→ article_id</text>
        <text x="940" y="340" fill="#4f5d75" font-size="10" font-family="'Geist Mono', monospace" text-anchor="end">uuid</text>
        <text x="796" y="360" fill="#2d3142" font-size="10" font-family="'Geist Mono', monospace">→ tag_id</text>
        <text x="940" y="360" fill="#4f5d75" font-size="10" font-family="'Geist Mono', monospace" text-anchor="end">uuid</text>

        <!-- Legend -->
        <line x1="40" y1="404" x2="960" y2="404" stroke="rgba(45,49,66,0.10)" stroke-width="0.8"/>
        <text x="40" y="420" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" letter-spacing="0.18em">LEGEND</text>

        <rect x="40" y="436" width="14" height="10" rx="2" fill="rgba(191,69,32,0.04)" stroke="#bf4520" stroke-width="1"/>
        <text x="60" y="444" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Aggregate root</text>

        <rect x="180" y="436" width="14" height="10" rx="2" fill="#ffffff" stroke="#2d3142" stroke-width="1"/>
        <text x="200" y="444" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Entity</text>

        <rect x="268" y="436" width="14" height="10" rx="2" fill="rgba(45,49,66,0.04)" stroke="#4f5d75" stroke-width="1" stroke-dasharray="3,2"/>
        <text x="288" y="444" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Join table</text>

        <text x="372" y="444" fill="#2d3142" font-size="10" font-family="'Geist Mono', monospace" font-weight="600">#</text>
        <text x="388" y="444" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Primary key</text>

        <text x="476" y="444" fill="#2d3142" font-size="10" font-family="'Geist Mono', monospace" font-weight="600">→</text>
        <text x="492" y="444" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Foreign key</text>

        <text x="584" y="444" fill="#4f5d75" font-size="10" font-family="'Geist Mono', monospace" font-weight="600">1 / N</text>
        <text x="616" y="444" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Cardinality</text>
      </svg>
  </div>
</body>
</html>
