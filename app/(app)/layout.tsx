import { Header } from "@/components/docs/Header";
import { Footer } from "@/components/docs/Footer";
import "@/components/docs/docs.css";
import "@/components/docs/chrome.css";
import "@/src/styles/certificates.css";
import "@/components/auth/app.css";
import "@/components/auth/dash.css";
import "@/components/auth/profile.css";
/* Buttons, subject colours and the meter, shared with the course pages. */
import "@/components/courses/courses.css";
import "@/components/auth/assess.css";

/**
 * The signed-in area: sign-in, the dashboard, the profile, certificates, the
 * leaderboard and the exams.
 *
 * One column, not three. These pages are about the reader rather than about
 * the course, so the contents sidebar would be answering a question nobody is
 * asking here -- the header keeps search and the account menu within reach and
 * the page gets the full width.
 */
export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Header />
      <main className="app">{children}</main>
      <Footer />
    </>
  );
}
