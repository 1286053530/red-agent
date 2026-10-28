          <rect x="264" y="80" width="160" height="64" rx="6" fill="rgba(45,49,66,0.05)" stroke="#4f5d75" stroke-width="1"/>
          <rect x="272" y="88" width="24" height="12" rx="2" fill="transparent" stroke="rgba(79,93,117,0.50)" stroke-width="0.8"/>
          <text x="284" y="97" fill="#4f5d75" font-size="7" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.08em">KV</text>
          <text x="344" y="116" fill="#2d3142" font-size="12" font-weight="600" font-family="'Geist', sans-serif" text-anchor="middle">Key Vault</text>
          <text x="344" y="132" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" text-anchor="middle">managed</text>
        </g>

        <!-- Compute inside the app subnet -->
        <g data-node-id="app" data-kind="compute" data-parent="snet-app">
          <rect data-role="bounds" x="200" y="344" width="160" height="64" rx="6" fill="#f5f5f5"/>
          <rect x="200" y="344" width="160" height="64" rx="6" fill="rgba(191,69,32,0.08)" stroke="#bf4520" stroke-width="1"/>
          <rect x="208" y="352" width="32" height="12" rx="2" fill="transparent" stroke="rgba(191,69,32,0.50)" stroke-width="0.8"/>
          <text x="224" y="361" fill="#bf4520" font-size="7" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.08em">APP</text>
          <text x="280" y="380" fill="#2d3142" font-size="12" font-weight="600" font-family="'Geist', sans-serif" text-anchor="middle">Checkout API</text>
          <text x="280" y="396" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" text-anchor="middle">snet-app</text>
        </g>

        <!-- Private endpoints inside the spoke subnet -->
        <g data-node-id="pe-sql" data-kind="endpoint" data-parent="snet-pe" data-target="sql">
          <rect data-role="bounds" x="564" y="280" width="144" height="64" rx="6" fill="#f5f5f5"/>
          <rect x="564" y="280" width="144" height="64" rx="6" fill="#ffffff" stroke="#2d3142" stroke-width="1"/>
          <rect x="572" y="288" width="24" height="12" rx="2" fill="transparent" stroke="rgba(45,49,66,0.40)" stroke-width="0.8"/>
          <text x="584" y="297" fill="#2d3142" font-size="7" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.08em">PE</text>
          <text x="636" y="316" fill="#2d3142" font-size="12" font-weight="600" font-family="'Geist', sans-serif" text-anchor="middle">PE · SQL</text>
          <text x="636" y="332" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" text-anchor="middle">snet-pe</text>
        </g>
        <g data-node-id="pe-kv" data-kind="endpoint" data-parent="snet-pe" data-target="kv">
          <rect data-role="bounds" x="732" y="280" width="144" height="64" rx="6" fill="#f5f5f5"/>
          <rect x="732" y="280" width="144" height="64" rx="6" fill="#ffffff" stroke="#2d3142" stroke-width="1"/>
          <rect x="740" y="288" width="24" height="12" rx="2" fill="transparent" stroke="rgba(45,49,66,0.40)" stroke-width="0.8"/>
          <text x="752" y="297" fill="#2d3142" font-size="7" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.08em">PE</text>
          <text x="804" y="316" fill="#2d3142" font-size="12" font-weight="600" font-family="'Geist', sans-serif" text-anchor="middle">PE · Vault</text>
          <text x="804" y="332" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" text-anchor="middle">snet-pe</text>
        </g>

        <!-- Legend -->
        <line x1="80" y1="640" x2="920" y2="640" stroke="rgba(45,49,66,0.10)" stroke-width="0.8"/>
        <text x="80" y="656" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" letter-spacing="0.18em">LEGEND</text>
        <rect x="80" y="664" width="28" height="10" rx="2" fill="rgba(45,49,66,0.015)" stroke="rgba(45,49,66,0.22)" stroke-width="0.8" stroke-dasharray="4,4"/>
        <text x="116" y="672" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Admin band</text>
        <rect x="220" y="664" width="28" height="10" rx="2" fill="rgba(45,49,66,0.02)" stroke="rgba(45,49,66,0.20)" stroke-width="0.8"/>
        <text x="256" y="672" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Traffic box</text>
        <rect x="360" y="664" width="14" height="10" rx="2" fill="rgba(45,49,66,0.05)" stroke="#4f5d75" stroke-width="1"/>
        <text x="380" y="672" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Managed PaaS</text>
        <rect x="500" y="664" width="14" height="10" rx="2" fill="#ffffff" stroke="#2d3142" stroke-width="1"/>
        <text x="520" y="672" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Private endpoint</text>
        <rect x="656" y="664" width="14" height="10" rx="2" fill="rgba(191,69,32,0.08)" stroke="#bf4520" stroke-width="1"/>
        <text x="676" y="672" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">Workload</text>
      </svg>
    </div>
  </div>
</body>
</html>
