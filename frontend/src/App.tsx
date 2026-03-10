import { Routes, Route, NavLink, useLocation } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import Dashboard from "./pages/Dashboard";
import ZoneDetail from "./pages/ZoneDetail";
import Settings from "./pages/Settings";

export default function App() {
  const location = useLocation();

  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: "var(--surface)",
            color: "var(--text)",
            border: "1px solid var(--border)",
          },
          success: { duration: 3000 },
          error: { duration: 5000 },
        }}
      />
      <nav>
        <div className="container">
          <h1>
            <span aria-hidden="true">⚓</span> Marine Forecast
          </h1>
          <div className="nav-links">
            <NavLink to="/" end>
              Dashboard
            </NavLink>
            <NavLink to="/settings">Settings</NavLink>
          </div>
        </div>
      </nav>
      <main className="container">
        <div key={location.pathname} className="page-transition">
          <Routes location={location}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/zone/:zoneId" element={<ZoneDetail />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </div>
      </main>
    </>
  );
}
