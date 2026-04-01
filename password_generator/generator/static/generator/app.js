(() => {
    const themeToggle = document.getElementById('themeToggle');
    const particleField = document.getElementById('particleField');
    const presetDropdown = document.getElementById('presetDropdown');
    const presetTrigger = document.getElementById('presetTrigger');
    const presetMenu = document.getElementById('presetMenu');
    const presetValue = document.getElementById('presetValue');
    const presetLabel = document.getElementById('presetLabel');
    const presetHint = document.getElementById('presetHint');
    const modeRadios = document.querySelectorAll('input[name="mode"]');
    const passwordControls = document.getElementById('passwordControls');
    const passphraseControls = document.getElementById('passphraseControls');
    const lengthInput = document.getElementById('length');
    const lengthValue = document.getElementById('lengthValue');
    const wordCountInput = document.getElementById('word_count');
    const wordCountValue = document.getElementById('wordCountValue');
    const result = document.getElementById('result');
    const copyBtn = document.getElementById('copyBtn');
    const card = document.getElementById('interactive-card');

    const setupParticleShield = () => {
        if (!particleField) {
            return;
        }

        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        const isMobile = window.innerWidth < 700;
        const particleCount = isMobile ? 22 : 42;

        particleField.innerHTML = '';

        for (let i = 0; i < particleCount; i += 1) {
            const dot = document.createElement('span');
            dot.className = 'particle';
            dot.style.left = `${Math.random() * 100}%`;
            dot.style.top = `${Math.random() * 100}%`;
            dot.style.setProperty('--size', `${Math.random() * 3 + 1.6}px`);
            dot.style.setProperty('--alpha', `${Math.random() * 0.5 + 0.2}`);
            dot.style.setProperty('--duration', `${Math.random() * 14 + 10}s`);
            dot.style.setProperty('--delay', `${Math.random() * -18}s`);
            dot.style.setProperty('--drift-x', `${Math.random() * 36 - 18}px`);
            if (prefersReducedMotion) {
                dot.style.animation = 'none';
            }
            particleField.appendChild(dot);
        }

        if (prefersReducedMotion) {
            return;
        }

        let rafId = null;
        let nextX = 0;
        let nextY = 0;

        const applyParallax = () => {
            particleField.style.transform = `translate3d(${nextX}px, ${nextY}px, 0)`;
            rafId = null;
        };

        window.addEventListener('mousemove', (event) => {
            const offsetX = (event.clientX / window.innerWidth - 0.5) * 10;
            const offsetY = (event.clientY / window.innerHeight - 0.5) * 10;
            nextX = offsetX;
            nextY = offsetY;
            if (!rafId) {
                rafId = requestAnimationFrame(applyParallax);
            }
        });

        window.addEventListener('mouseleave', () => {
            nextX = 0;
            nextY = 0;
            if (!rafId) {
                rafId = requestAnimationFrame(applyParallax);
            }
        });
    };

    setupParticleShield();

    const syncThemeButton = () => {
        if (!themeToggle) {
            return;
        }
        const isLight = document.body.getAttribute('data-theme') === 'light';
        themeToggle.textContent = isLight ? '☀️ Light' : '🌙 Dark';
    };

    const applyModeVisibility = () => {
        const selected = document.querySelector('input[name="mode"]:checked');
        if (!selected) {
            return;
        }
        const isPassphrase = selected.value === 'passphrase';
        if (passwordControls) {
            passwordControls.classList.toggle('hidden', isPassphrase);
        }
        if (passphraseControls) {
            passphraseControls.classList.toggle('hidden', !isPassphrase);
        }
    };

    modeRadios.forEach((radio) => radio.addEventListener('change', applyModeVisibility));
    applyModeVisibility();

    if (presetDropdown && presetTrigger && presetMenu && presetValue && presetLabel) {
        const presetOptions = presetMenu.querySelectorAll('.preset-option');

        const closePresetMenu = () => {
            presetDropdown.classList.remove('is-open');
            presetTrigger.setAttribute('aria-expanded', 'false');
        };

        presetTrigger.addEventListener('click', () => {
            const nextState = !presetDropdown.classList.contains('is-open');
            presetDropdown.classList.toggle('is-open', nextState);
            presetTrigger.setAttribute('aria-expanded', nextState ? 'true' : 'false');
        });

        presetOptions.forEach((option) => {
            option.addEventListener('click', () => {
                const value = option.dataset.value;
                const label = option.dataset.label;
                const description = option.dataset.description;
                if (!value || !label) {
                    return;
                }

                presetValue.value = value;
                presetLabel.textContent = label;
                if (presetHint && description) {
                    presetHint.textContent = description;
                }

                presetOptions.forEach((item) => item.classList.remove('active'));
                option.classList.add('active');
                closePresetMenu();
            });
        });

        document.addEventListener('click', (event) => {
            if (!presetDropdown.contains(event.target)) {
                closePresetMenu();
            }
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                closePresetMenu();
            }
        });
    }

    if (themeToggle) {
        const savedTheme = localStorage.getItem('pg-theme');
        if (savedTheme) {
            document.body.setAttribute('data-theme', savedTheme);
        }
        syncThemeButton();
        themeToggle.addEventListener('click', () => {
            const current = document.body.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
            if (current === 'dark') {
                document.body.removeAttribute('data-theme');
            } else {
                document.body.setAttribute('data-theme', current);
            }
            localStorage.setItem('pg-theme', current);
            syncThemeButton();
        });
    }

    if (lengthInput && lengthValue) {
        const syncLength = () => {
            lengthValue.textContent = lengthInput.value;
        };
        syncLength();
        lengthInput.addEventListener('input', syncLength);
    }

    if (wordCountInput && wordCountValue) {
        const syncWords = () => {
            wordCountValue.textContent = wordCountInput.value;
        };
        syncWords();
        wordCountInput.addEventListener('input', syncWords);
    }

    if (copyBtn && result) {
        copyBtn.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(result.textContent.trim());
                const original = copyBtn.textContent;
                copyBtn.textContent = 'Copied!';
                setTimeout(() => {
                    copyBtn.textContent = original;
                }, 1200);
            } catch (error) {
                copyBtn.textContent = 'Copy failed';
                setTimeout(() => {
                    copyBtn.textContent = 'Copy';
                }, 1200);
            }
        });
    }

    if (card) {
        card.addEventListener('mousemove', (event) => {
            const rect = card.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            const rotateY = ((x / rect.width) - 0.5) * 8;
            const rotateX = ((y / rect.height) - 0.5) * -8;
            card.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(900px) rotateX(0deg) rotateY(0deg)';
        });
    }
})();
