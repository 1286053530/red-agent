      <circle cx="652" cy="240" r="4" fill="#f5f5f5"/>
      <circle data-value="286" cx="652" cy="240" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="658" cy="230" r="4" fill="#f5f5f5"/>
      <circle data-value="289" cx="658" cy="230" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="658" cy="210" r="4" fill="#f5f5f5"/>
      <circle data-value="289" cx="658" cy="210" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="704" cy="230" r="4" fill="#f5f5f5"/>
      <circle data-value="312" cx="704" cy="230" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="856" cy="230" r="4" fill="#f5f5f5"/>
      <circle data-value="388" data-name="req-77d3" cx="856" cy="230" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="884" cy="230" r="4" fill="#f5f5f5"/>
      <circle data-value="402" data-name="req-09aa" cx="884" cy="230" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <circle cx="942" cy="230" r="4" fill="#f5f5f5"/>
      <circle data-value="431" data-name="req-4c1f" cx="942" cy="230" r="4" fill="rgba(191,69,32,0.55)" stroke="#bf4520" stroke-width="1.2"/>

      <!-- Labels: the p99 tail only, one tier per label, alternating sides,
           each bound to its dot by data-name and tied to it by a hairline
           leader. verify-beeswarm.py proves each label sits nearer its own
           dot than any other named dot along the value axis. -->
      <line x1="856" y1="222" x2="856" y2="158" stroke="rgba(45,49,66,0.10)" stroke-width="0.8"/>
      <rect x="826" y="141" width="60" height="12" rx="2" fill="#f5f5f5"/>
      <text data-name="req-77d3" data-role="label" x="856" y="150" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.06em">REQ-77D3</text>
      <line x1="884" y1="238" x2="884" y2="298" stroke="rgba(45,49,66,0.10)" stroke-width="0.8"/>
      <rect x="854" y="301" width="60" height="12" rx="2" fill="#f5f5f5"/>
      <text data-name="req-09aa" data-role="label" x="884" y="310" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.06em">REQ-09AA</text>
      <line x1="942" y1="222" x2="942" y2="128" stroke="rgba(45,49,66,0.10)" stroke-width="0.8"/>
      <rect x="912" y="111" width="60" height="12" rx="2" fill="#f5f5f5"/>
      <text data-name="req-4c1f" data-role="label" x="942" y="120" fill="#2d3142" font-size="8" font-family="'Geist Mono', monospace" text-anchor="middle" letter-spacing="0.06em">REQ-4C1F</text>

      <!-- Legend -->
      <line x1="40" y1="462" x2="960" y2="462" stroke="rgba(45,49,66,0.10)" stroke-width="0.8"/>
      <text x="40" y="478" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" letter-spacing="0.18em">LEGEND</text>
      <text x="960" y="478" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" letter-spacing="0.06em" text-anchor="end">ONE DOT = ONE REQUEST · VALUE AXIS 0–440 MS, LINEAR FROM ZERO · VERTICAL SPREAD IS PACKING, NOT A VALUE · ILLUSTRATIVE FIGURES, NOT MEASURED TRAFFIC</text>

      <circle cx="52" cy="490" r="4" fill="rgba(191,69,32,0.55)" stroke="#bf4520" stroke-width="1.2"/>
      <text x="68" y="494" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">req-4c1f · focal, the slowest request in the window</text>
      <circle cx="660" cy="490" r="4" fill="rgba(45,49,66,0.55)" stroke="#4f5d75" stroke-width="0.75"/>
      <text x="676" y="494" fill="#4f5d75" font-size="8.5" font-family="'Geist', sans-serif">request · vertical offset is packing only</text>
    </svg>
  </div>
</body>
</html>
