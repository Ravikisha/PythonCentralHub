import type { Metadata } from "next";
import { PublicProfile } from "./PublicProfile";
import "./public-profile.css";

/**
 * /u/?id=<uid> -- a learner's public profile, for those who opted in to the
 * leaderboard. One static page; the learner is chosen by the query string so
 * no profile is ever prerendered or indexed.
 */
export const metadata: Metadata = {
  title: "Learner profile",
  robots: { index: false, follow: false },
};

export default function PublicProfilePage() {
  return <PublicProfile />;
}
