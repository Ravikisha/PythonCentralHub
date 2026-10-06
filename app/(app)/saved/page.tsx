import type { Metadata } from "next";
import { Saved } from "./Saved";
import "./saved.css";

/**
 * /saved -- bookmarks and private notes, grouped by course.
 */
export const metadata: Metadata = {
  title: "Saved lessons and notes",
  robots: { index: false, follow: true },
};

export default function SavedPage() {
  return (
    <>
      <h1 className="pch-auth__title">Saved</h1>
      <p className="pch-auth__intro">
        Your bookmarks and private notes. They live in this browser, and in your
        account too when you are signed in.
      </p>
      <Saved />
    </>
  );
}
