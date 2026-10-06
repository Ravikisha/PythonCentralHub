import type { Timestamp } from "firebase-admin/firestore";
import { db, requireModuleSlug, HttpError } from "@/lib/server/admin";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * GET /api/course-ratings/?course=<slug>
 *
 * The course's average and count, and its latest written reviews. Public and
 * cached briefly at the CDN; a new rating shows up within a few minutes.
 */
export async function GET(req: Request): Promise<Response> {
  let course: string;
  try {
    course = requireModuleSlug(new URL(req.url).searchParams.get("course"));
  } catch (err) {
    return Response.json({ error: (err as Error).message }, { status: 400 });
  }

  try {
    const store = db();
    const [agg, latest] = await Promise.all([
      store.doc(`courseRatings/${course}`).get(),
      store.collection("ratings").where("course", "==", course).orderBy("at", "desc").limit(20).get(),
    ]);
    const { count = 0, sum = 0 } = (agg.data() ?? {}) as { count?: number; sum?: number };
    const reviews = latest.docs
      .map((d) => d.data())
      .filter((r) => typeof r.review === "string" && r.review.length > 0)
      .slice(0, 6)
      .map((r) => ({
        name: r.name as string,
        stars: r.stars as number,
        review: r.review as string,
        at: (r.at as Timestamp | undefined)?.toMillis?.() ?? null,
      }));

    return Response.json(
      { count, average: count ? Math.round((sum / count) * 10) / 10 : null, reviews },
      { headers: { "Cache-Control": "public, s-maxage=300, stale-while-revalidate=3600" } },
    );
  } catch (err) {
    // Not configured yet (no service account): no ratings rather than an error.
    if (err instanceof HttpError && err.code === "server/not-configured") {
      return Response.json({ count: 0, average: null, reviews: [] });
    }
    console.error(err);
    return Response.json({ error: "Could not load ratings." }, { status: 500 });
  }
}
