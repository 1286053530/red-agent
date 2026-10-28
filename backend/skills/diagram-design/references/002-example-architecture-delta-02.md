<text x="456" y="108" data-change="CHANGED" data-target="api" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" letter-spacing="0.06em">CHANGED · api<tspan x="456" y="131" fill="#2d3142" font-size="12" font-family="'Geist', sans-serif" letter-spacing="0">Orders API v1 → v2</tspan></text>
<path d="M 456 148 H 776" stroke="rgba(45,49,66,0.12)" stroke-width="0.8"/>
<text x="424" y="170" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" >02</text>
<text x="456" y="168" data-change="REMOVED" data-target="legacy" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" letter-spacing="0.06em">REMOVED · legacy<tspan x="456" y="191" fill="#2d3142" font-size="12" font-family="'Geist', sans-serif" letter-spacing="0">Retire legacy dispatcher</tspan></text>
<path d="M 456 208 H 776" stroke="rgba(45,49,66,0.12)" stroke-width="0.8"/>
<text x="424" y="230" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" >03</text>
<text x="456" y="228" data-change="ADDED" data-target="queue" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" letter-spacing="0.06em">ADDED · queue<tspan x="456" y="251" fill="#2d3142" font-size="12" font-family="'Geist', sans-serif" letter-spacing="0">Introduce durable order queue</tspan></text>
<path d="M 456 268 H 776" stroke="rgba(45,49,66,0.12)" stroke-width="0.8"/>
<text x="424" y="290" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" >04</text>
<text x="456" y="288" data-change="MOVED" data-target="worker" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" letter-spacing="0.06em">MOVED · worker<tspan x="456" y="311" fill="#2d3142" font-size="12" font-family="'Geist', sans-serif" letter-spacing="0">Fulfilment worker: left → right</tspan></text>
<path d="M 456 328 H 776" stroke="rgba(45,49,66,0.12)" stroke-width="0.8"/>
<text x="424" y="350" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" >05</text>
<text x="456" y="348" data-change="REWIRED" data-target="r2" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" letter-spacing="0.06em">REWIRED · r2<tspan x="456" y="371" fill="#2d3142" font-size="12" font-family="'Geist', sans-serif" letter-spacing="0">Orders API: dispatcher → queue</tspan></text>
<path d="M 456 388 H 776" stroke="rgba(45,49,66,0.12)" stroke-width="0.8"/>
<text x="424" y="410" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" >06</text>
<text x="456" y="408" data-change="REMOVED" data-target="r3" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" letter-spacing="0.06em">REMOVED · r3<tspan x="456" y="431" fill="#2d3142" font-size="12" font-family="'Geist', sans-serif" letter-spacing="0">Dispatcher → worker</tspan></text>
<path d="M 456 448 H 776" stroke="rgba(45,49,66,0.12)" stroke-width="0.8"/>
<text x="424" y="470" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" >07</text>
<text x="456" y="468" data-change="ADDED" data-target="r4" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" letter-spacing="0.06em">ADDED · r4<tspan x="456" y="491" fill="#2d3142" font-size="12" font-family="'Geist', sans-serif" letter-spacing="0">Queue → worker</tspan></text>
<text x="424" y="544" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" letter-spacing="0.14em">PRESERVED</text>
<text x="424" y="564" fill="#4f5d75" font-size="11" font-family="'Geist', sans-serif" >Storefront · database · r1 · r5</text>
        <g data-snapshot="after" transform="translate(840 96)" data-grid="336 480 4">
<!-- Relationships precede components; endpoints meet the declared bounds. -->
<path data-kind="relationship" data-object-id="r1" data-status="unchanged" data-signature="https:create" data-from="storefront" data-to="api" d="M 168 64 V 96" fill="none" stroke="#4f5d75" stroke-width="1.2" marker-end="url(#architecture-delta-arrow)"/>
<path data-kind="relationship" data-object-id="r2" data-status="rewired" data-signature="submit-order" data-from="api" data-to="queue" d="M 168 160 V 192" fill="none" stroke="#4f5d75" stroke-width="1.2" stroke-dasharray="8 3 2 3" marker-end="url(#architecture-delta-arrow)"/>
<path data-kind="relationship" data-object-id="r4" data-status="added" data-signature="deliver" data-from="queue" data-to="worker" d="M 168 256 V 272 Q 168 280 176 280 H 248 Q 256 280 256 288 V 304" fill="none" stroke="#4f5d75" stroke-width="2" marker-end="url(#architecture-delta-arrow)"/>
<path data-kind="relationship" data-object-id="r5" data-status="unchanged" data-signature="write-order" data-from="worker" data-to="db" d="M 256 368 V 384 Q 256 392 248 392 H 176 Q 168 392 168 400 V 416" fill="none" stroke="#4f5d75" stroke-width="1.2" marker-end="url(#architecture-delta-arrow)"/>
<rect x="176" y="72" width="92" height="16" rx="2" fill="#f5f5f5"/>
<text x="180" y="84" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" >r1 · HTTPS</text>
<rect x="176" y="168" width="92" height="16" rx="2" fill="#f5f5f5"/>
<text x="180" y="180" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" >r2 · REWIRED</text>
<rect x="68" y="260" width="92" height="16" rx="2" fill="#f5f5f5"/>
<text x="156" y="272" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" text-anchor="end">r4 · ADDED</text>
<rect x="92" y="396" width="68" height="16" rx="2" fill="#f5f5f5"/>
<text x="156" y="408" fill="#4f5d75" font-size="8" font-family="'Geist Mono', monospace" text-anchor="end">r5 · SQL</text>
<g data-kind="component" data-object-id="storefront" data-status="unchanged" data-signature="web:v1">
<rect data-role="bounds" x="96" y="0" width="144" height="64" rx="6" fill="#ffffff" stroke="#4f5d75" stroke-width="1.2"/>
<text x="108" y="15" fill="#4f5d75" font-size="7.5" font-family="'Geist Mono', monospace" >= storefront · UNCHANGED</text>
<text x="108" y="36" fill="#2d3142" font-size="12" font-family="'Geist', sans-serif" font-weight="600">Storefront</text>
<text x="108" y="53" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" >web:v1</text>
</g>
<g data-kind="component" data-object-id="api" data-status="changed" data-signature="orders:v2">
<rect data-role="bounds" x="96" y="96" width="144" height="64" rx="6" fill="rgba(191,69,32,0.08)" stroke="#bf4520" stroke-width="1.2"/>
<path d="M 97 108 V 148" fill="none" stroke="#bf4520" stroke-width="3"/>
<text x="108" y="111" fill="#4f5d75" font-size="7.5" font-family="'Geist Mono', monospace" >~ api · CHANGED</text>
<text x="108" y="132" fill="#2d3142" font-size="12" font-family="'Geist', sans-serif" font-weight="600">Orders API</text>
<text x="108" y="149" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" >/orders · v2</text>
</g>
<g data-kind="component" data-object-id="queue" data-status="added" data-signature="orders:durable:v1">
<rect data-role="bounds" x="96" y="192" width="144" height="64" rx="6" fill="#ffffff" stroke="#4f5d75" stroke-width="1.2"/>
<rect x="100" y="196" width="136" height="56" rx="4" fill="none" stroke="#4f5d75" stroke-width="0.8"/>
<text x="108" y="207" fill="#4f5d75" font-size="7.5" font-family="'Geist Mono', monospace" >+ queue · ADDED</text>
<text x="108" y="228" fill="#2d3142" font-size="12" font-family="'Geist', sans-serif" font-weight="600">Order queue</text>
<text x="108" y="245" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" >durable · at-least-once</text>
</g>
<g data-kind="component" data-object-id="worker" data-status="moved" data-signature="fulfilment:v1">
<rect data-role="bounds" x="184" y="304" width="144" height="64" rx="6" fill="#ffffff" stroke="#4f5d75" stroke-width="1.2" stroke-dasharray="1 4" stroke-linecap="round"/>
<text x="196" y="319" fill="#4f5d75" font-size="7.5" font-family="'Geist Mono', monospace" >↔ worker · MOVED</text>
<text x="196" y="340" fill="#2d3142" font-size="12" font-family="'Geist', sans-serif" font-weight="600">Fulfilment worker</text>
<text x="196" y="357" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" >fulfilment:v1</text>
</g>
<g data-kind="component" data-object-id="db" data-status="unchanged" data-signature="orders:postgres">
<rect data-role="bounds" x="96" y="416" width="144" height="64" rx="6" fill="#ffffff" stroke="#4f5d75" stroke-width="1.2"/>
<text x="108" y="431" fill="#4f5d75" font-size="7.5" font-family="'Geist Mono', monospace" >= db · UNCHANGED</text>
<text x="108" y="452" fill="#2d3142" font-size="12" font-family="'Geist', sans-serif" font-weight="600">Orders database</text>
<text x="108" y="469" fill="#4f5d75" font-size="9" font-family="'Geist Mono', monospace" >PostgreSQL</text>
</g>
<text x="16" y="332" fill="#4f5d75" font-size="12" font-family="'Geist', sans-serif" >Same worker,</text>
<text x="16" y="352" fill="#4f5d75" font-size="12" font-family="'Geist', sans-serif" >new placement.</text>
</g>
        <path d="M 24 608 H 1176" stroke="rgba(45,49,66,0.12)" stroke-width="1"/>
<rect x="24" y="624" width="20" height="16" rx="3" fill="none" stroke="#4f5d75" stroke-width="1"/>
<text x="56" y="636" fill="#4f5d75" font-size="11" font-family="'Geist', sans-serif" >= Unchanged</text>
<rect x="220" y="624" width="20" height="16" rx="3" fill="none" stroke="#4f5d75" stroke-width="1"/>
<rect x="224" y="628" width="12" height="8" rx="1" fill="none" stroke="#4f5d75" stroke-width="0.8"/>
<text x="252" y="636" fill="#4f5d75" font-size="11" font-family="'Geist', sans-serif" >+ Added</text>
