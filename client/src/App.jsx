// App.jsx — top-level route configuration
//
// defines the page routes available in the React application
//
// planned routes:
//   /             → landing page
//   /auth         → signup and login
//   /onboarding   → financial onboarding
//   /room         → main room
//   /hub          → profile and progress overview
//   /roadmap      → level roadmap
//   /quests       → daily and weekly quests
//   /friend       → friend roll
//
// responsibilities:
//   - configure React Router
//   - connect routes to page components
//   - apply the shared layout to protected pages
//   - later support protected-route behavior

import Login from "./pages/Login";

export default function App() {
  return <Login />;
}

