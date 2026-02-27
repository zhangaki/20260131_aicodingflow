---
title: "Website Performance Tools: Lighthouse, WebPageTest & Core Web Vitals"
description: Free toolkit + 30-minute checklist to improve Core Web Vitals (LCP, INP, CLS). Compare Lighthouse vs PageSpeed vs WebPageTest and fix the first screen.
---

Users bounce when the first screen takes too long to render or shifts while loading. You don’t need a perfect score—you need a measurable improvement to **LCP**, **INP**, and **CLS**.

Do this first (10 minutes):
1) **Measure** with Lighthouse / PageSpeed Insights (what’s slow + which metric is failing).
2) **Locate the blocker** in WebPageTest (waterfall + filmstrip: CSS/JS, fonts, images, TTFB).
3) **Ship one fix today** and re-test (then add a performance budget to prevent regressions).

## A 30-minute “Fix the first screen” checklist

Run through this once, then re-test. It’s designed to improve perceived speed (what users feel) and usually shows up in **LCP/INP** quickly.

### 1) Stop shipping oversized images

- Convert hero and above-the-fold images to **AVIF/WebP**.
- Serve responsive sizes (`srcset`) so mobile isn’t downloading desktop.
- Add explicit `width`/`height` to prevent layout shifts (helps **CLS**).
- Use `loading="lazy"` only for below-the-fold images (don’t lazy-load the LCP image).

### 2) Make fonts non-blocking

- Use `font-display: swap`.
- Self-host critical fonts where possible.
- Preload only the 1–2 font files you actually need for the first screen.
- Prefer `preconnect` to font origins (only if you can’t self-host).

### 3) Delay non-critical JavaScript

- Add `defer` to non-critical scripts.
- Move analytics and chat widgets behind user interaction or a timer.
- If a script doesn’t affect the first screen, it shouldn’t block it.

### 4) Improve TTFB before you micro-optimize

If **TTFB** is consistently high, front-end tweaks won’t fully fix the “slow” feeling.

- Enable caching at the CDN/edge for HTML where safe.
- Add server-side caching for expensive routes.
- Reduce cold starts (keep-alive, avoid heavy middleware on every request).
- If you’re on a serverless platform, profile which requests are slow and why.

## Tool stack (what each one is for)

Use these in order so you don’t chase noise.

### Lighthouse (Chrome DevTools)

- Best for quick, repeatable lab checks while you iterate.
- Use it to confirm you didn’t regress **LCP/CLS** after a change.

### PageSpeed Insights (PSI)

- Same Lighthouse lab data, plus real-user field data (CrUX) when available.
- Use it to answer: “Is this slow for real users, or just my test run?”

### WebPageTest

- Best for finding the *cause* of slowness: waterfalls, filmstrips, and render-blocking resources.
- Use it to see which request or asset is delaying first paint / LCP.

## Next step: pick one metric to win

- **Bad LCP**: fix the LCP element (hero image, critical CSS, render blockers).
- **Bad CLS**: add sizes for images/embeds, reserve space for fonts, avoid late-injected UI.
- **Bad INP**: reduce main-thread JS, split bundles, defer third-party scripts.
