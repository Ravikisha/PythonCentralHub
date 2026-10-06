import type { MetadataRoute } from "next";
import { SITE_URL } from "@/lib/site";

/**
 * Everything is crawlable except the signed-in area, which is per-reader and
 * has nothing to index: a crawler reaching /dashboard sees an empty shell
 * waiting for an auth state it will never have.
 */
export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/dashboard/", "/profile/", "/certificates/", "/exam/"],
    },
    sitemap: `${SITE_URL}/sitemap.xml`,
  };
}
