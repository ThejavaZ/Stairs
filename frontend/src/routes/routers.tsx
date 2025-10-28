import { Routes, Route } from "react-router-dom";
import Home from "../views/home";
import Cameras from "../views/cameras";
import Reports from "../views/reports";
import Settings from "../views/settings";

export const Routers = () => {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/cameras" element={<Cameras />} />
      <Route path="/reports" element={<Reports />} />
      <Route path="/settings" element={<Settings />} />
    </Routes>
  );
};