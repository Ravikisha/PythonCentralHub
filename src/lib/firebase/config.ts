/**
 * Firebase web app configuration.
 *
 * These values are public by design. Firebase ships them in every client
 * bundle; access control comes from Firestore security rules and the Auth
 * "Authorized domains" list, not from keeping the API key secret.
 *
 * The committed defaults keep local dev, previews and forks-of-the-repo
 * working with zero setup. Every field can be overridden with a
 * `PUBLIC_FIREBASE_*` env var (see .env.example), so pointing the site at a
 * different Firebase project never means editing source.
 */
const env = import.meta.env;

export const firebaseConfig = {
  apiKey: env.PUBLIC_FIREBASE_API_KEY || "AIzaSyC9JRAi_fsezHf8PN-8A4tSoZYJmThEiAk",
  authDomain: env.PUBLIC_FIREBASE_AUTH_DOMAIN || "pythoncentralhub.firebaseapp.com",
  databaseURL:
    env.PUBLIC_FIREBASE_DATABASE_URL ||
    "https://pythoncentralhub-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: env.PUBLIC_FIREBASE_PROJECT_ID || "pythoncentralhub",
  storageBucket: env.PUBLIC_FIREBASE_STORAGE_BUCKET || "pythoncentralhub.firebasestorage.app",
  messagingSenderId: env.PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "479368830014",
  appId: env.PUBLIC_FIREBASE_APP_ID || "1:479368830014:web:87a5f98745df11c788056f",
  measurementId: env.PUBLIC_FIREBASE_MEASUREMENT_ID || "G-58ZCKY0YPD",
};
