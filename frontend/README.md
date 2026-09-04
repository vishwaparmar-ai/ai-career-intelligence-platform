# CareerIQ — frontend (Day 8: Next.js + UI)

Static skeleton for the AI Career Intelligence Platform. No API calls yet —
the login/signup forms only `console.log` their values, and dashboard
sections show empty states. Real wiring starts Day 11 (auth) onward.

## Run it

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Then open http://localhost:3000.

## What's here

```
app/
  layout.tsx          root layout: fonts, header, footer
  page.tsx            landing page
  login/page.tsx       login form (client component)
  signup/page.tsx      signup form (client component)
  dashboard/
    layout.tsx          nested layout: sidebar shell
    page.tsx             overview page with empty-state cards
components/
  dashboard-sidebar.tsx  sidebar nav with active-link highlighting
  ui/field.tsx           labeled input used by both auth forms
  ui/button.tsx          primary/ghost button
lib/utils.ts             cn() classname helper
```

## Notes for next sessions

- `NEXT_PUBLIC_API_URL` is read but unused until Day 11 (auth) and Day 12+
  (resume upload) wire real `fetch` calls to FastAPI.
- Sidebar links point to `/dashboard/resume`, `/dashboard/job`,
  `/dashboard/roadmap`, `/dashboard/interview` — those routes don't exist
  yet and will 404 until later days build them.
- Design tokens (colors, fonts) live in `tailwind.config.ts` — reuse
  `match` / `signal` / `gap` colors for matched/partial/missing skill
  states everywhere in the app, not just the landing page mockup.
