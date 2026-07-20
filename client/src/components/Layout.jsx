// Layout.jsx — shared application layout and navigation
//
// wraps routed pages in the common Sprout interface
// will contain the navigation bar and React Router Outlet
//
// responsibilities:
//   - display shared navigation
//   - provide the page layout used after authentication
//   - render the active child route
//   - support responsive desktop and mobile navigation

import { Outlet } from "react-router-dom";
import NavBar from "./Navbar";

export default function Layout() {
  return (
    <div className="app-layout">
      <NavBar />

      <main className="app-content">
        <Outlet />
      </main>
    </div>
  );
}