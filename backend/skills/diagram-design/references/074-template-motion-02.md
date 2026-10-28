          <rect x="700" y="184" width="16" height="16" fill="#4f5d75"/><rect x="724" y="184" width="16" height="16" fill="#4f5d75"/><rect x="748" y="184" width="16" height="16" fill="#4f5d75"/>
          <text x="796" y="196" fill="#4f5d75" font-family="Geist Mono, monospace" font-size="12">3 queued</text>
        </g>
        <g data-motion-item data-step="4" aria-label="Step 4: Audit entry appended">
          <rect x="664" y="328" width="200" height="88" rx="8" fill="#f5f5f5" stroke="#2d3142"/>
          <text x="764" y="364" text-anchor="middle" fill="#2d3142" font-family="Geist, sans-serif" font-size="16" font-weight="600">Audit log</text>
          <text x="764" y="388" text-anchor="middle" fill="#4f5d75" font-family="Geist Mono, monospace" font-size="12">0042 · appended</text>
        </g>
        <g data-motion-item data-step="5" aria-label="Step 5: Evaluation complete">
          <text x="48" y="376" fill="#2d3142" font-family="Geist, sans-serif" font-size="16" font-weight="600">Outcome: accepted and recorded</text>
        </g>

        <!-- Decorative duplicate path and token never carry unique meaning. -->
        <path data-motion-item data-step="2" data-motion-decorative aria-hidden="true" focusable="false" pathLength="1" class="draw-path" d="M248 180 H356"/>
        <circle data-motion-item data-step="3" data-motion-decorative aria-hidden="true" focusable="false" class="flow-token" cx="556" cy="180" r="6" fill="#bf4520"/>
      </svg>
    </div>

    <div data-motion-controls role="group" aria-label="Diagram playback controls">
      <button type="button" data-motion-action="prev">Previous</button>
      <button type="button" data-motion-action="play" aria-pressed="false">Play</button>
      <button type="button" data-motion-action="pause" aria-pressed="true">Pause</button>
      <button type="button" data-motion-action="next">Next</button>
      <button type="button" data-motion-action="replay">Replay</button>
      <span class="keyboard-help">←/→ step · Space play/pause · R replay · Home/End jump</span>
      <span data-motion-status-visible aria-hidden="true">Step <span data-motion-step-label>5</span> of 5</span>
    </div>
    <p class="sr-only" data-motion-status role="status" aria-live="polite" aria-atomic="true"></p>
    <noscript><p>Animation controls require JavaScript. The complete final diagram is shown above.</p></noscript>
  </main>

  <script data-diagram-controls>
    (() => {
      const params = new URLSearchParams(location.search);
      const staticOverride = params.get('motion') === 'static' || document.documentElement.dataset.motion === 'static';
      const requestedStep = params.get('step');
      const reduce = matchMedia('(prefers-reduced-motion: reduce)');
      document.fonts.ready.then(() => { document.documentElement.dataset.fontsReady = 'true'; });

      document.querySelectorAll('[data-motion-root]').forEach((root) => {
        const count = Number(root.dataset.stepCount);
        const hold = parseFloat(getComputedStyle(root).getPropertyValue('--motion-hold')) || 720;
        const parsedStep = requestedStep !== null && /^\d+$/.test(requestedStep) ? Number(requestedStep) : null;
        const exactStep = params.get('motion') === 'step' && Number.isSafeInteger(parsedStep) && parsedStep >= 0 && parsedStep <= count ? parsedStep : null;
        const items = [...root.querySelectorAll('[data-motion-item]')];
        const labels = Array.from({ length: count + 1 }, (_, index) => index === 0
          ? 'Ready'
          : items.filter((item) => !item.hasAttribute('data-motion-decorative') && Number(item.dataset.step) === index)
              .map((item) => item.getAttribute('aria-label')).join('; '));
        const controls = root.querySelector('[data-motion-controls]');
        const status = root.querySelector('[data-motion-status]');
        const visibleStep = root.querySelector('[data-motion-step-label]');
        let step = count;
        let timer = 0;
        let playing = false;
        let stepBeforeReduce = 0;
        let resumeAfterReduce = root.dataset.motionMode === 'reveal';

        const buttons = (action) => controls.querySelector(`[data-motion-action="${action}"]`);
        const clearClock = () => { window.clearTimeout(timer); timer = 0; };
        const announce = () => { status.textContent = `Step ${step} of ${count}: ${labels[step] || 'Complete'}`; };
        const setControlsAvailable = (available) => {
          controls.hidden = !available;
          controls.setAttribute('aria-hidden', String(!available));
          controls.dataset.playbackDisabled = String(!available);
          controls.querySelectorAll('button').forEach((control) => { control.disabled = !available; });
        };

        function render(next, userInitiated = false) {
          step = Math.max(0, Math.min(count, next));
          root.dataset.stepCurrent = String(step);
          root.dataset.frame = step === count ? 'end' : step === 0 ? 'start' : 'step';
          items.forEach((item) => {
            const itemStep = Number(item.dataset.step);
            item.classList.toggle('is-visible', itemStep <= step);
            item.classList.toggle('is-current', itemStep === step);
          });
          if (visibleStep) visibleStep.textContent = String(step);
          const unavailable = controls.dataset.playbackDisabled === 'true';
          buttons('prev').disabled = unavailable || step === 0;
          buttons('next').disabled = unavailable || step === count;
          if (userInitiated) announce();
        }

        function pause(userInitiated = false) {
          clearClock();
          playing = false;
          root.classList.remove('is-playing');
          buttons('play').setAttribute('aria-pressed', 'false');
          buttons('pause').setAttribute('aria-pressed', 'true');
          if (userInitiated) status.textContent = `Paused at step ${step} of ${count}`;
        }

        function finish() {
          pause(false);
          root.dataset.frame = 'end';
          status.textContent = `Complete · step ${count} of ${count}`;
        }

        function tick() {
          if (!playing) return;
          if (step >= count) { finish(); return; }
          render(step + 1, false);
          if (step >= count) { finish(); return; }
          timer = window.setTimeout(tick, hold);
        }

        function play(fromStart = false, userInitiated = false) {
          clearClock();
          if (fromStart || step >= count) render(0, userInitiated);
          playing = true;
          root.classList.add('is-playing');
          buttons('play').setAttribute('aria-pressed', 'true');
          buttons('pause').setAttribute('aria-pressed', 'false');
          timer = window.setTimeout(tick, hold);
        }

        controls.addEventListener('click', (event) => {
          const button = event.target.closest('[data-motion-action]');
          if (!button) return;
          const action = button.dataset.motionAction;
          if (action === 'play') play(false, true);
          if (action === 'pause') pause(true);
          if (action === 'replay') play(true, true);
          if (action === 'prev') { pause(false); render(step - 1, true); }
          if (action === 'next') { pause(false); render(step + 1, true); }
        });

        root.addEventListener('keydown', (event) => {
          if (event.target.matches('input, textarea, select, a[href]')) return;
          const keys = { ArrowLeft: step - 1, ArrowRight: step + 1, Home: 0, End: count };
          if (event.code === 'Space' && !event.target.closest('button')) {
            event.preventDefault();
            playing ? pause(true) : play(false, true);
            return;
          }
          if (!event.ctrlKey && !event.metaKey && !event.altKey && event.key.toLowerCase() === 'r') {
            event.preventDefault();
            play(true, true);
            return;
          }
          if (!(event.key in keys)) return;
          event.preventDefault();
          pause(false);
          render(keys[event.key], true);
        });

        document.addEventListener('visibilitychange', () => {
          if (document.visibilityState === 'hidden' && playing) pause(false);
        });
        reduce.addEventListener('change', (event) => {
          if (event.matches && root.dataset.motionState !== 'reduced') {
            stepBeforeReduce = step;
            resumeAfterReduce = playing;
          }
          pause(false);
          if (event.matches) {
            setControlsAvailable(false);
            render(count, false);
            root.dataset.frame = 'static';
            root.dataset.motionState = 'reduced';
            status.textContent = 'Reduced motion · complete static frame · playback controls unavailable';
          } else if (staticOverride || root.dataset.motionMode === 'none') {
            setControlsAvailable(false);
            render(count, false);
            root.dataset.frame = 'static';
            root.dataset.motionState = 'static';
            status.textContent = 'Static frame · complete diagram · playback controls unavailable';
          } else {
            delete root.dataset.motionState;
            if (exactStep !== null) {
              setControlsAvailable(false);
              render(exactStep, false);
              root.dataset.frame = 'step';
              root.dataset.motionState = 'test';
