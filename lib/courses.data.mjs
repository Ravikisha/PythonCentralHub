/**
 * The course catalogue.
 *
 * Python Central Hub is a set of courses, and each course is one top-level folder of
 * src/content/docs. This file says what each folder is *as a course*: the name
 * a learner would look for, its level, its subject and what it teaches. The
 * lessons themselves, their order and their counts are read from the content
 * tree (lib/courses.ts), never written down here, so the catalogue cannot
 * drift from the course behind it.
 *
 * Plain JavaScript rather than TypeScript because the build scripts read it
 * too: scripts/gen-progress-manifest.mjs takes each course's title from here,
 * which is what the dashboard, the certificates and the verifier show.
 *
 * Adding a course: add its folder under src/content/docs, then an entry here.
 * A folder with no entry still builds and still has lessons; it just is not
 * listed in the catalogue.
 *
 * `code` follows the college convention the level is read from: 100s are
 * where you start, 200s assume a first course, 300s assume several.
 */

/** @typedef {"beginner" | "intermediate" | "advanced"} Level */

/**
 * @typedef {object} CourseInfo
 * @property {string} slug        The content folder's URL segment.
 * @property {string} title       What the course is called everywhere.
 * @property {string} code        Catalogue number; the hundreds digit is the level.
 * @property {Level} level
 * @property {string} subject     One of SUBJECTS, for filtering and colour.
 * @property {string} summary     One sentence, in the learner's terms.
 * @property {string[]} outcomes  What you can do at the end, three or four items.
 * @property {string[]} [after]   Courses worth taking first, by slug.
 * @property {string} [startAt]   Where the course opens, when the first page in
 *                                reading order is not the right first lesson.
 */

/** Subjects, in the order the catalogue's filter lists them. */
export const SUBJECTS = [
  { id: "programming", label: "Programming" },
  { id: "data-ai", label: "Data and AI" },
  { id: "mathematics", label: "Mathematics" },
  { id: "computer-science", label: "Computer science" },
  { id: "web", label: "Web development" },
  { id: "engineering", label: "Software engineering" },
];

/** @type {CourseInfo[]} */
export const COURSES = [
  {
    slug: "tutorials",
    title: "Python Programming",
    code: "PY 101",
    level: "beginner",
    subject: "programming",
    summary:
      "The language from the first print() to classes, files, errors and async code.",
    outcomes: [
      "Write and run Python programs with confidence",
      "Use lists, dictionaries, sets and strings fluently",
      "Structure code with functions, modules and classes",
      "Read tracebacks and fix what they point at",
    ],
    startAt: "/tutorials/introduction/",
  },
  {
    slug: "projects",
    title: "Python Projects",
    code: "PY 150",
    level: "beginner",
    subject: "programming",
    summary:
      "Two hundred small builds, from command-line games to apps that call AI models.",
    outcomes: [
      "Turn an idea into a working program",
      "Practise the language on problems with real edges",
      "Build a portfolio of finished, runnable projects",
    ],
    after: ["tutorials"],
    startAt: "/projects/beginners/asciiartgenerator/",
  },
  {
    slug: "python-automation-and-scripting",
    title: "Automation and Scripting",
    code: "PY 180",
    level: "beginner",
    subject: "programming",
    summary:
      "Let Python do the dull work: files, spreadsheets, the web, email and schedules.",
    outcomes: [
      "Rename, sort and process files in bulk",
      "Scrape web pages and fill in documents",
      "Send email and run jobs on a schedule",
    ],
    after: ["tutorials"],
  },
  {
    slug: "data-analytics",
    title: "Data Analytics with Python",
    code: "DATA 110",
    level: "beginner",
    subject: "data-ai",
    summary:
      "NumPy, pandas, charts, SQL and the statistics you need to trust a result.",
    outcomes: [
      "Load, clean and reshape real datasets",
      "Summarise and chart data with pandas and Matplotlib",
      "Query databases with SQL",
      "Test whether a difference is real",
    ],
    after: ["tutorials"],
  },
  {
    slug: "mathematics-for-machine-learning",
    title: "Mathematics for Machine Learning",
    code: "MATH 120",
    level: "beginner",
    subject: "mathematics",
    summary:
      "Linear algebra, calculus and probability, worked through with code beside every idea.",
    outcomes: [
      "Work with vectors, matrices and their decompositions",
      "Differentiate the functions models are built from",
      "Reason about uncertainty with probability and statistics",
    ],
  },
  {
    slug: "machine-learning",
    title: "Machine Learning",
    code: "ML 210",
    level: "intermediate",
    subject: "data-ai",
    summary:
      "Prepare data, train and evaluate models, and know which one a problem needs.",
    outcomes: [
      "Prepare features and split data honestly",
      "Train regression and classification models with scikit-learn",
      "Evaluate, tune and compare models",
      "Apply the same workflow to text",
    ],
    after: ["data-analytics", "mathematics-for-machine-learning"],
  },
  {
    slug: "deep-learning",
    title: "Deep Learning",
    code: "DL 310",
    level: "advanced",
    subject: "data-ai",
    summary:
      "Neural networks from the perceptron up: training, vision, sequences and transformers.",
    outcomes: [
      "Build and train networks in Keras and PyTorch",
      "Diagnose training with losses, curves and callbacks",
      "Apply convolutional and sequence models",
      "Fine-tune large pretrained models",
    ],
    after: ["machine-learning"],
  },
  {
    slug: "dsa-with-python",
    title: "Data Structures and Algorithms",
    code: "CS 220",
    level: "intermediate",
    subject: "computer-science",
    summary:
      "Arrays to graphs, with visualisations and the interview patterns built on them.",
    outcomes: [
      "Choose the right data structure for a problem",
      "Analyse time and space complexity",
      "Recognise and apply the common problem patterns",
    ],
    after: ["tutorials"],
  },
  {
    slug: "flask-tutorials",
    title: "Web Development with Flask",
    code: "WEB 201",
    level: "intermediate",
    subject: "web",
    summary:
      "Routing, templates, forms, databases, sign-in and APIs, through to deployment.",
    outcomes: [
      "Build a multi-page web app with Flask",
      "Store data and handle forms safely",
      "Add accounts, APIs and background jobs",
      "Deploy it where others can use it",
    ],
    after: ["tutorials"],
  },
  {
    slug: "software-testing-and-quality",
    title: "Software Testing and Quality",
    code: "SE 230",
    level: "intermediate",
    subject: "engineering",
    summary:
      "pytest, API and UI testing, static analysis and the pipelines that run them.",
    outcomes: [
      "Write unit and integration tests with pytest",
      "Test APIs and user interfaces",
      "Catch problems early with static analysis and CI",
    ],
    after: ["tutorials"],
  },
];

/** A course by its folder slug, or undefined for folders that are not courses. */
export function courseInfo(slug) {
  return COURSES.find((c) => c.slug === slug);
}

/**
 * Suggested routes through the catalogue, in the order to take them.
 *
 * These are the prerequisite chains from `after`, written out as the two
 * journeys most learners are on. A path is a sequence, which is why the home
 * page numbers its stops.
 */
export const PATHS = [
  {
    id: "data-ai",
    title: "From first program to deep learning",
    courses: [
      "tutorials",
      "data-analytics",
      "mathematics-for-machine-learning",
      "machine-learning",
      "deep-learning",
    ],
  },
  {
    id: "engineering",
    title: "From first program to shipped software",
    courses: [
      "tutorials",
      "dsa-with-python",
      "software-testing-and-quality",
      "flask-tutorials",
    ],
  },
];
