      <rect x="594" y="204" width="100" height="64" rx="6" fill="#f5f5f5" stroke="rgba(45,49,66,0.25)"/>
      <rect x="598" y="208" width="18" height="10" rx="3" fill="rgba(45,49,66,0.12)"/><text x="607" y="213" class="role-text">ANL</text>
      <text x="644" y="227" class="node-title">Publish Dashboard</text><text x="644" y="239" class="node-sub">metrics → decisions</text><text x="644" y="251" class="node-tool">BI workspace</text>
      <rect x="598" y="258" width="16" height="8" rx="3" fill="#b8915a"/><text x="606" y="264" class="chip-text">TB</text>
      <rect x="674" y="258" width="16" height="8" rx="3" fill="#9c6b50"/><text x="682" y="264" class="chip-text">FL</text>

      <!-- Legend: steps -->
      <text x="164" y="293" class="legend-label">STEPS</text>
      <rect x="180" y="284" width="24" height="12" rx="6" fill="rgba(45,49,66,0.12)"/><text x="192" y="292" class="step-number">01</text><text x="212" y="293" class="legend-text">Ingest</text>
      <rect x="272" y="284" width="24" height="12" rx="6" fill="rgba(45,49,66,0.12)"/><text x="284" y="292" class="step-number">02</text><text x="304" y="293" class="legend-text">Store</text>
      <rect x="360" y="284" width="24" height="12" rx="6" fill="rgba(191,69,32,0.20)"/><text x="372" y="292" class="step-number focal-text">03</text><text x="392" y="293" class="legend-text">Transform</text>
      <rect x="468" y="284" width="24" height="12" rx="6" fill="rgba(45,49,66,0.12)"/><text x="480" y="292" class="step-number">04</text><text x="500" y="293" class="legend-text">Analyze</text>
      <rect x="568" y="284" width="24" height="12" rx="6" fill="rgba(45,49,66,0.12)"/><text x="580" y="292" class="step-number">05</text><text x="600" y="293" class="legend-text">Publish</text>

      <!-- Legend: data types -->
      <text x="164" y="314" class="legend-label">DATA TYPE</text>
      <rect x="180" y="306" width="16" height="8" rx="3" fill="#7c8f6f"/><text x="188" y="312" class="chip-text">LS</text><text x="202" y="314" class="legend-text">Stream</text>
      <rect x="252" y="306" width="16" height="8" rx="3" fill="#5e7a9b"/><text x="260" y="312" class="chip-text">DB</text><text x="274" y="314" class="legend-text">Dataset</text>
      <rect x="332" y="306" width="16" height="8" rx="3" fill="#b8915a"/><text x="340" y="312" class="chip-text">TB</text><text x="354" y="314" class="legend-text">Table</text>
      <rect x="404" y="306" width="16" height="8" rx="3" fill="#9c6b50"/><text x="412" y="312" class="chip-text">FL</text><text x="426" y="314" class="legend-text">Dashboard</text>
      <text x="500" y="314" class="legend-text">left chip = input · right chip = output</text>

      <!-- Legend: flow -->
      <text x="164" y="336" class="legend-label">FLOW</text>
      <line x1="180" y1="333" x2="204" y2="333" stroke="#4f5d75" marker-end="url(#arr-muted)"/><text x="212" y="336" class="legend-text">Standard handoff</text>
      <line x1="324" y1="333" x2="348" y2="333" stroke="#bf4520" stroke-width="1.2" marker-end="url(#arr-accent)"/><text x="356" y="336" class="legend-text">Focal handoff</text>
      <line x1="460" y1="333" x2="484" y2="333" stroke="#2e5aa8" marker-end="url(#arr-link)"/><text x="492" y="336" class="legend-text">Published output</text>
    </svg>
  </main>
</body>
</html>
