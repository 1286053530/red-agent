              status.textContent = `Test frame · step ${step} of ${count} · playback controls unavailable`;
            } else {
              setControlsAvailable(true);
              render(stepBeforeReduce, false);
              status.textContent = `Ready · step ${step} of ${count}`;
              if (resumeAfterReduce && root.dataset.motionMode === 'reveal') {
                play(false, false);
              }
            }
            resumeAfterReduce = false;
          }
        });

        if (staticOverride) {
          document.documentElement.dataset.motion = 'static';
          pause(false);
          setControlsAvailable(false);
          render(count, false);
          root.dataset.frame = 'static';
          root.dataset.motionState = 'static';
          status.textContent = 'Static frame · complete diagram · playback controls unavailable';
        } else if (reduce.matches || root.dataset.motionMode === 'none') {
          pause(false);
          setControlsAvailable(false);
          render(count, false);
          root.dataset.frame = 'static';
          root.dataset.motionState = reduce.matches ? 'reduced' : 'static';
          status.textContent = reduce.matches
            ? 'Reduced motion · complete static frame · playback controls unavailable'
            : 'Static frame · complete diagram · playback controls unavailable';
        } else if (exactStep !== null) {
          document.documentElement.dataset.motion = 'step';
          pause(false);
          setControlsAvailable(false);
          render(exactStep, false);
          root.dataset.frame = 'step';
          root.dataset.motionState = 'test';
          status.textContent = `Test frame · step ${step} of ${count} · playback controls unavailable`;
        } else if (root.dataset.motionMode === 'reveal') {
          setControlsAvailable(true);
          render(0, false);
          play(false, false);
        } else {
          pause(false);
          setControlsAvailable(true);
          render(0, false);
          status.textContent = `Ready · step 0 of ${count}`;
        }
        root.classList.add('motion-ready');
      });
    })();
  </script>
</body>
</html>
