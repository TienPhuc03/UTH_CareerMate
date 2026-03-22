# Client

Static HTML pages for the CareerMate frontend.

## Structure

- `auth/`: login and signup pages
- `components/`: shared header, footer, and auth helpers
- `page/`: feature pages and dashboards
- `src/`: static assets

## Current auth contract

- Backend auth base URL: `http://127.0.0.1:8000/api/Auth`
- Supported roles: `candidate`, `recruiter`, `admin`
- Legacy `student` values are being phased out and should not be sent by the frontend

## Notes

- Google auth buttons are intentionally disabled until the backend exposes working OAuth routes.
- These pages currently run as static files with Tailwind loaded from CDN.
