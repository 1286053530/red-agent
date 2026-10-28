      <rect x="624" y="80" width="192" height="84" rx="6" fill="#f5f5f5"/>
      <rect x="624" y="80" width="192" height="84" rx="6" fill="rgba(191,69,32,0.08)" stroke="#bf4520" stroke-width="1"/>
      <rect x="632" y="88" width="64" height="12" rx="2" fill="transparent" stroke="rgba(191,69,32,0.50)" stroke-width="0.8"/>
      <text x="664" y="97" fill="#bf4520" font-size="7" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.08em">MANAGED</text>
      <text x="720" y="120" fill="#2d3142" font-size="12" font-weight="600" font-family="'Geist', sans-serif" text-anchor="middle">rds-primary</text>
      <rect x="632" y="132" width="176" height="24" rx="4" fill="rgba(45,49,66,0.05)" stroke="#4f5d75" stroke-width="0.8"/>
      <text x="640" y="148" fill="#2d3142" font-size="12" font-family="'Geist', sans-serif">postgres</text>
      <text x="800" y="148" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" text-anchor="end">16.2</text>

      <!-- Node: rds-standby -->
      <rect x="624" y="212" width="192" height="84" rx="6" fill="#f5f5f5"/>
      <rect x="624" y="212" width="192" height="84" rx="6" fill="rgba(45,49,66,0.05)" stroke="#4f5d75" stroke-width="1"/>
      <rect x="632" y="220" width="64" height="12" rx="2" fill="transparent" stroke="rgba(79,93,117,0.50)" stroke-width="0.8"/>
      <text x="664" y="229" fill="#4f5d75" font-size="7" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.08em">MANAGED</text>
      <text x="720" y="252" fill="#2d3142" font-size="12" font-weight="600" font-family="'Geist', sans-serif" text-anchor="middle">rds-standby</text>
      <rect x="632" y="264" width="176" height="24" rx="4" fill="rgba(45,49,66,0.05)" stroke="#4f5d75" stroke-width="0.8"/>
      <text x="640" y="280" fill="#2d3142" font-size="12" font-family="'Geist', sans-serif">postgres</text>
      <text x="800" y="280" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" text-anchor="end">16.2</text>

      <!-- Legend strip -->
      <line x1="40" y1="340" x2="1000" y2="340" stroke="rgba(45,49,66,0.10)" stroke-width="0.8"/>
      <text x="40" y="356" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" letter-spacing="0.18em">LEGEND</text>

      <rect x="40" y="372" width="14" height="10" rx="2" fill="rgba(191,69,32,0.08)" stroke="#bf4520" stroke-width="1"/>
      <text x="60" y="380" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Focal / primary</text>

      <rect x="180" y="372" width="14" height="10" rx="2" fill="#ffffff" stroke="#2d3142" stroke-width="1"/>
      <text x="200" y="380" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Infra node</text>

      <rect x="320" y="372" width="14" height="10" rx="2" fill="rgba(45,49,66,0.05)" stroke="#4f5d75" stroke-width="1"/>
      <text x="340" y="380" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Store / standby</text>

      <rect x="460" y="372" width="14" height="10" rx="2" fill="rgba(45,49,66,0.03)" stroke="rgba(45,49,66,0.30)" stroke-width="1"/>
      <text x="480" y="380" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Managed / CDN</text>

      <line x1="600" y1="376" x2="628" y2="376" stroke="#2e5aa8" stroke-width="1.2" marker-end="url(#arrow-link)"/>
      <text x="636" y="380" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Cross-zone</text>

      <line x1="740" y1="376" x2="768" y2="376" stroke="#bf4520" stroke-width="1" stroke-dasharray="5,4" marker-end="url(#arrow-accent)"/>
      <text x="776" y="380" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Replication</text>

      <line x1="880" y1="376" x2="908" y2="376" stroke="#4f5d75" stroke-width="1.2" marker-end="url(#arrow)"/>
      <text x="916" y="380" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">In-zone call</text>
    </svg>
  </div>
</body>
</html>
