import type { Metadata } from "next";
import { AdminPanel } from "./AdminPanel";
import "./admin.css";

/**
 * /admin -- totals and recent messages for whoever runs the site. Access is
 * checked by /api/admin-stats/ against ADMIN_EMAILS; the page itself is
 * public markup with nothing in it.
 */
export const metadata: Metadata = {
  title: "Admin",
  robots: { index: false, follow: false },
};

export default function AdminPage() {
  return (
    <>
      <h1 className="pch-auth__title">Admin</h1>
      <AdminPanel />
    </>
  );
}
