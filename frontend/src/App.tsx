import { Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import ZoneDetail from "./pages/ZoneDetail";
import Settings from "./pages/Settings";

export default function App() {
  return (
    <>
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
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/zone/:zoneId" element={<ZoneDetail />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </>
  );
}
