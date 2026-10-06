import type { Firestore } from "firebase-admin/firestore";

/**
 * Course ratings, server-side only.
 *
 *   ratings/{course}_{uid}     { uid, course, stars, review, name, at }
 *   courseRatings/{course}     { count, sum }   -- the running aggregate
 *
 * Both collections are closed to the browser by the rules' default deny:
 * ratings are written by app/api/rate-course after checking the learner has
 * studied the course, and read back through app/api/course-ratings.
 */

/** Lessons of a course a learner must have finished before rating it. */
export const MIN_LESSONS_TO_RATE = 3;

/** Remove every rating by `uid` and take it out of each course's aggregate. */
export async function deleteRatingsBy(store: Firestore, uid: string): Promise<void> {
  const mine = await store.collection("ratings").where("uid", "==", uid).get();
  for (const doc of mine.docs) {
    const { course, stars } = doc.data() as { course: string; stars: number };
    const aggRef = store.doc(`courseRatings/${course}`);
    await store.runTransaction(async (tx) => {
      const agg = (await tx.get(aggRef)).data() ?? { count: 0, sum: 0 };
      tx.set(aggRef, {
        count: Math.max(0, (agg.count ?? 0) - 1),
        sum: Math.max(0, (agg.sum ?? 0) - stars),
      });
      tx.delete(doc.ref);
    });
  }
}
