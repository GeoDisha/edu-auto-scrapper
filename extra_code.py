# ------------------------- POPUP HANDLING -------------------------
async def close_popups(page):
    X_BUTTON_SELECTORS = [
        # existing
        "button[aria-label*='close']",
        "button[aria-label*='dismiss']",
        "button:has-text('×')",
        "button:has-text('✕')",
        "div[role='button']:has-text('×')",
        "[class*='close']",
        "[id*='close']",
        ".close-btn",
        ".modal-close",
        "[data-bs-dismiss='modal']",

        # 🔹 ADDED (no behavior change)
        "a[aria-label*='close']",
        "a:has-text('×')",
        "span[aria-label*='close']",
        "i[aria-label*='close']",
        "svg[aria-label*='close']",
    ]

    CLOSE_TEXTS = [
        # existing
        "close", "dismiss", "no thanks", "not now",
        "skip", "cancel", "maybe later",

        # 🔹 ADDED
        "no thank you",
        "decline",
        "reject",
    ]

    CLOSE_SELECTORS = [
        # existing
        "button:has-text('Close')",
        "button:has-text('CLOSE')",
        "button:has-text('Dismiss')",
        "[role='button']:has-text('Close')",
        "[role='button']:has-text('Dismiss')",

        # 🔹 ADDED
        "a:has-text('Close')",
        "a:has-text('Cancel')",
        "span:has-text('close')",
        "i:has-text('close')",
    ]

    ACCEPT_TEXTS = [
        # existing
        "accept", "agree", "i agree", "accept all",
        "got it", "continue", "ok", "okay", "allow",
    ]

    ACCEPT_SELECTORS = [
        # existing
        "button:has-text('Accept')",
        "button:has-text('AGREE')",
        "button:has-text('OK')",
        "button:has-text('Got it')",
        "[id*='cookie'] button",
        "[class*='cookie'] button",
    ]

    for _ in range(4):
        clicked_something = False

        # ------------------ X / ICON CLOSE ------------------
        for sel in X_BUTTON_SELECTORS:
            locator = page.locator(sel)
            if await locator.count() > 0:
                for i in range(await locator.count()):
                    try:
                        elem = locator.nth(i)
                        if await elem.is_visible() and await elem.is_enabled():
                            await elem.click(timeout=1500)
                            clicked_something = True
                            await page.wait_for_timeout(500)
                    except Exception:
                        pass

        if clicked_something:
            continue

        # ------------------ TEXT CLOSE (selectors) ------------------
        for sel in CLOSE_SELECTORS:
            locator = page.locator(sel)
            if await locator.count() > 0:
                for i in range(await locator.count()):
                    try:
                        elem = locator.nth(i)
                        if await elem.is_visible() and await elem.is_enabled():
                            await elem.click(timeout=1500)
                            clicked_something = True
                            await page.wait_for_timeout(500)
                    except Exception:
                        pass

        # ------------------ TEXT CLOSE (get_by_text) ------------------
        for txt in CLOSE_TEXTS:
            locator = page.get_by_text(txt, exact=False)
            if await locator.count() > 0:
                for i in range(await locator.count()):
                    try:
                        elem = locator.nth(i)
                        if await elem.is_visible() and await elem.is_enabled():
                            await elem.click(timeout=1500)
                            clicked_something = True
                            await page.wait_for_timeout(500)
                    except Exception:
                        pass

        if clicked_something:
            continue

        # ------------------ ACCEPT / CONSENT ------------------
        for sel in ACCEPT_SELECTORS:
            locator = page.locator(sel)
            if await locator.count() > 0:
                for i in range(await locator.count()):
                    try:
                        elem = locator.nth(i)
                        if await elem.is_visible() and await elem.is_enabled():
                            await elem.click(timeout=1500)
                            clicked_something = True
                            await page.wait_for_timeout(500)
                    except Exception:
                        pass

        for txt in ACCEPT_TEXTS:
            locator = page.get_by_text(txt, exact=False)
            if await locator.count() > 0:
                for i in range(await locator.count()):
                    try:
                        elem = locator.nth(i)
                        if await elem.is_visible() and await elem.is_enabled():
                            await elem.click(timeout=1500)
                            clicked_something = True
                            await page.wait_for_timeout(500)
                    except Exception:
                        pass

        # 🔹 ADDED: ESC fallback (does not change flow)
        try:
            await page.keyboard.press("Escape")
        except Exception:
            pass

        # 🔹 ADDED: overlay cleanup (safe)
        try:
            await page.evaluate("""
                () => {
                    document.querySelectorAll(
                        '.modal-backdrop, .overlay, .popup-overlay, [class*="overlay"]'
                    ).forEach(el => el.remove());
                }
            """)
        except Exception:
            pass

        if not clicked_something:
            break


# ------------------------- OPPORTUNISTIC POPUP GUARD -------------------------
async def opportunistic_close_popups(page):
    """
    Lightweight, repeatable popup closer.
    Safe to call many times.
    Does NOT block execution.
    """

    selectors = [
        # existing
        "button[aria-label*='close' i]",
        "button[aria-label*='dismiss' i]",
        "[data-bs-dismiss='modal']",
        ".modal-close",
        ".close-btn",
        "[class*='close']",

        # 🔹 ADDED
        "a[aria-label*='close' i]",
        "a:has-text('×')",
        "span[aria-label*='close' i]",
        "i[aria-label*='close' i]",
        "svg[aria-label*='close' i]",

        # Cookie / consent
        "button:has-text('Accept')",
        "button:has-text('AGREE')",
        "button:has-text('OK')",
        "button:has-text('Got it')",
        "button:has-text('Allow')",

        # Generic dialog buttons
        "[role='dialog'] button",
    ]

    for sel in selectors:
        try:
            loc = page.locator(sel)
            if await loc.count() > 0:
                for i in range(await loc.count()):
                    btn = loc.nth(i)
                    if await btn.is_visible():
                        await btn.click(timeout=500)
                        await page.wait_for_timeout(150)
        except Exception:
            pass

