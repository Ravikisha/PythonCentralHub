/**
 * Globals published by scripts under public/, not by modules.
 *
 * `toast.js` and the reCAPTCHA snippet are plain scripts loaded into the page,
 * so nothing imports them and TypeScript has no other way to know the shape
 * they attach to `window`. Declared once here because two components use each
 * of them, and two separate `declare global` blocks disagreeing about an
 * optional field is a compile error rather than a warning.
 */
interface PchToast {
  show(options: {
    title: string;
    description?: string;
    variant?: string;
  }): void;
}

interface PchRecaptcha {
  ready(cb: () => void): void;
  execute(siteKey: string, opts: { action: string }): Promise<string>;
}

declare global {
  interface Window {
    toast?: PchToast;
    grecaptcha?: PchRecaptcha;
  }
}

export {};
