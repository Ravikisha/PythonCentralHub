"use client";

import { useEffect } from "react";
import { reportError } from "@/lib/report-error";

/**
 * Reports uncaught errors and unhandled promise rejections from the page.
 *
 * Errors from third-party scripts on other origins arrive as a bare "Script
 * error." with nothing to act on, and are skipped.
 */
export function ErrorReporter() {
  useEffect(() => {
    const onError = (event: ErrorEvent) => {
      if (!event.error && /^Script error\.?$/.test(event.message)) return;
      reportError(event.error ?? event.message, "uncaught");
    };
    const onRejection = (event: PromiseRejectionEvent) => {
      reportError(event.reason, "unhandled-rejection");
    };
    window.addEventListener("error", onError);
    window.addEventListener("unhandledrejection", onRejection);
    return () => {
      window.removeEventListener("error", onError);
      window.removeEventListener("unhandledrejection", onRejection);
    };
  }, []);
  return null;
}
