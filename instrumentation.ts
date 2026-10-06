import type { Instrumentation } from "next";

/**
 * Server errors -- a route handler that throws, a page that fails to render --
 * reported through lib/server/report.ts, so they are findable in the Vercel
 * logs under `pythoncentralhub:error` and, if configured, posted to a webhook.
 */
export const onRequestError: Instrumentation.onRequestError = async (
  err,
  request,
  context,
) => {
  const { report } = await import("./lib/server/report");
  await report({
    source: "server",
    message: err instanceof Error ? err.message : String(err),
    stack: err instanceof Error ? err.stack : undefined,
    digest:
      typeof err === "object" && err !== null && "digest" in err
        ? String((err as { digest: unknown }).digest)
        : undefined,
    url: request.path,
    kind: `${context.routeType} ${context.routerKind}`,
  });
};
