import type { Metadata } from "next";
import { CourseCatalog } from "@/components/courses/CourseCatalog";
import { catalogCards } from "@/components/courses/catalog-data";
import { SUBJECTS } from "@/lib/courses";

export const metadata: Metadata = {
  title: "All courses",
  description:
    "Every Python Central Hub course: programming, data analytics, machine learning, deep learning, mathematics, algorithms, web development and testing.",
  alternates: { canonical: "/courses/" },
};

export default function CoursesPage() {
  const cards = catalogCards();

  return (
    <div className="courses-index">
      <h1 className="courses-index__title">All courses</h1>
      <p className="courses-index__lede">
        {cards.length} courses, all free and self-paced. Pick one to see its
        syllabus, or start its first lesson straight from the card.
      </p>
      <CourseCatalog courses={cards} subjects={SUBJECTS} />
    </div>
  );
}
