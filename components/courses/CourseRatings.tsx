"use client";

import { useEffect, useState } from "react";
import { Star } from "lucide-react";
import { useSession } from "@/components/auth/useSession";

interface Ratings {
  count: number;
  average: number | null;
  reviews: { name: string; stars: number; review: string; at: number | null }[];
}

function Stars({ value, size = 16 }: { value: number; size?: number }) {
  return (
    <span className="ratings__stars" aria-hidden="true">
      {[1, 2, 3, 4, 5].map((n) => (
        <Star
          key={n}
          width={size}
          height={size}
          fill={n <= Math.round(value) ? "currentColor" : "none"}
        />
      ))}
    </span>
  );
}

/**
 * The course's rating and latest reviews, and a form to add one's own.
 *
 * Ratings go through /api/rate-course, which accepts them only from verified
 * learners who have finished a few lessons of the course. The form syncs the
 * learner's local progress first, so lessons done on this device count.
 */
export function CourseRatings({ slug, title }: { slug: string; title: string }) {
  const session = useSession();
  const [data, setData] = useState<Ratings | null>(null);
  const [stars, setStars] = useState(0);
  const [review, setReview] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<{ text: string; ok: boolean } | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch(`/api/course-ratings/?course=${encodeURIComponent(slug)}`)
      .then((res) => (res.ok ? res.json() : null))
      .then((json: Ratings | null) => {
        if (!cancelled) setData(json ?? { count: 0, average: null, reviews: [] });
      })
      .catch(() => {
        if (!cancelled) setData({ count: 0, average: null, reviews: [] });
      });
    return () => {
      cancelled = true;
    };
  }, [slug]);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!stars) {
      setMessage({ text: "Choose a number of stars.", ok: false });
      return;
    }
    setBusy(true);
    setMessage(null);
    try {
      const { resync } = await import("@/src/lib/progress/sync");
      await resync();
      const { callApi } = await import("@/src/lib/firebase/client");
      await callApi("rate-course", { module: slug, stars, review });
      setMessage({ text: "Thanks. Your rating will appear within a few minutes.", ok: true });
    } catch (err) {
      setMessage({ text: (err as Error).message || "Could not save your rating.", ok: false });
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="ratings" aria-labelledby="ratings-title">
      <h2 id="ratings-title">What learners say</h2>

      {data === null ? null : data.count ? (
        <p className="ratings__summary">
          <Stars value={data.average ?? 0} size={18} />
          <strong>{data.average?.toFixed(1)}</strong> out of 5 from {data.count}{" "}
          {data.count === 1 ? "rating" : "ratings"}
        </p>
      ) : (
        <p className="ratings__summary">No ratings yet. Finish a few lessons and be the first.</p>
      )}

      {data?.reviews.length ? (
        <ul className="ratings__reviews">
          {data.reviews.map((r, i) => (
            <li key={i}>
              <Stars value={r.stars} />
              <p>{r.review}</p>
              <span className="ratings__who">{r.name}</span>
            </li>
          ))}
        </ul>
      ) : null}

      {session.state === "signed-in" ? (
        <form className="ratings__form" onSubmit={submit}>
          <fieldset>
            <legend>Rate {title}</legend>
            <div className="ratings__pick" role="radiogroup" aria-label="Stars">
              {[1, 2, 3, 4, 5].map((n) => (
                <button
                  key={n}
                  type="button"
                  role="radio"
                  aria-checked={stars === n}
                  aria-label={`${n} ${n === 1 ? "star" : "stars"}`}
                  onClick={() => setStars(n)}
                  className="ratings__pick-star"
                  data-on={n <= stars}
                >
                  <Star width={24} height={24} fill={n <= stars ? "currentColor" : "none"} />
                </button>
              ))}
            </div>
            <label className="ratings__label" htmlFor="rating-review">
              A sentence for other learners (optional)
            </label>
            <textarea
              id="rating-review"
              maxLength={500}
              rows={3}
              value={review}
              onChange={(e) => setReview(e.target.value)}
            />
            <button type="submit" className="button" disabled={busy}>
              {busy ? "Saving…" : "Submit rating"}
            </button>
            {message ? (
              <p className={message.ok ? "ratings__ok" : "ratings__error"} role="status">
                {message.text}
              </p>
            ) : null}
          </fieldset>
        </form>
      ) : null}
    </section>
  );
}
