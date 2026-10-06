/**
 * Firebase web app configuration.
 *
 * These values are public by design. Firebase ships them in every client
 * bundle; access control comes from Firestore security rules and the Auth
 * "Authorized domains" list, not from keeping the API key secret.
 *
 * The committed defaults keep local dev, previews and forks-of-the-repo
 * working with zero setup. Every field can be overridden with a
 * `NEXT_PUBLIC_FIREBASE_*` env var (see .env.example), so pointing the site at
 * a different Firebase project never means editing source.
 *
 * Next inlines `process.env.NEXT_PUBLIC_*` at build time, and only when it is
 * written as a direct member access -- which is why each one is spelled out
 * below rather than read from a loop or a destructured object.
 */

export const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "AIzaSyC9JRAi_fsezHf8PN-8A4tSoZYJmThEiAk",
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "pythoncentralhub.firebaseapp.com",
  databaseURL:
    process.env.NEXT_PUBLIC_FIREBASE_DATABASE_URL ||
    "https://pythoncentralhub-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "pythoncentralhub",
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "pythoncentralhub.firebasestorage.app",
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "479368830014",
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || "1:479368830014:web:87a5f98745df11c788056f",
  measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID || "G-58ZCKY0YPD",
};
