import {
  db,
  post,
  HttpError,
  requireVerifiedCaller,
  requireModuleSlug,
  countRealLessons,
  lessonsByCourse,
  FieldValue,
} from "@/lib/server/admin";
import { MIN_LESSONS_TO_RATE } from "@/lib/server/ratings";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * POST /api/rate-course/  { module, stars: 1-5, review?: string }
 *
 * One rating per learner per course; rating again replaces it. Only verified
 * accounts that have finished at least MIN_LESSONS_TO_RATE real lessons of
 * the course (counted from their synced progress) can rate it, so the average
 * reflects people who took the course.
 */
export const POST = post(async (req, body) => {
  const caller = await requireVerifiedCaller(req);
  const course = requireModuleSlug(body.module);
  if (!lessonsByCourse().get(course)?.size) throw new HttpError(404, "Unknown course.");

  const stars = body.stars;
  if (!Number.isInteger(stars) || (stars as number) < 1 || (stars as number) > 5) {
    throw new HttpError(400, "Choose between 1 and 5 stars.");
  }
  const review =
    typeof body.review === "string" ? body.review.trim().replace(/\s+/g, " ").slice(0, 500) : "";

  const store = db();
  const progress = await store.doc(`users/${caller.uid}/progress/${course}`).get();
  const done = countRealLessons(course, progress.data()?.completed);
  if (done < MIN_LESSONS_TO_RATE) {
    throw new HttpError(
      412,
      `Finish at least ${MIN_LESSONS_TO_RATE} lessons of this course before rating it.`,
    );
  }

  const ratingRef = store.doc(`ratings/${course}_${caller.uid}`);
  const aggRef = store.doc(`courseRatings/${course}`);

  await store.runTransaction(async (tx) => {
    const [previous, agg] = await Promise.all([tx.get(ratingRef), tx.get(aggRef)]);
    const before = previous.exists ? ((previous.data()?.stars as number) ?? 0) : 0;
    const current = agg.data() ?? { count: 0, sum: 0 };
    tx.set(aggRef, {
      count: (current.count ?? 0) + (previous.exists ? 0 : 1),
      sum: (current.sum ?? 0) - before + (stars as number),
    });
    tx.set(ratingRef, {
      uid: caller.uid,
      course,
      stars,
      review,
      // Shown beside the review; the first name only, so a review never
      // carries someone's full name unasked.
      name: (caller.name || "A learner").split(/\s+/)[0].slice(0, 40),
      at: FieldValue.serverTimestamp(),
    });
  });

  return { ok: true };
});
