import { useEffect, useState } from "react";
import { Route, Routes } from "react-router-dom";

import { api } from "./api/client";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import AntoinePage from "./pages/AntoinePage";
import DashboardPage from "./pages/DashboardPage";
import GraphsPage from "./pages/GraphsPage";
import ModelsPage from "./pages/ModelsPage";
import MoleculesPage from "./pages/MoleculesPage";
import VlePage from "./pages/VlePage";
import VolumePage from "./pages/VolumePage";

export default function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [components, setComponents] = useState([]);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  async function reloadComponents() {
    const data = await api("/components");
    setComponents(data);
  }

  useEffect(() => {
    reloadComponents().catch((error) => {
      console.error(error);
    });
  }, []);

  return (
    <div className="min-h-screen">
      <div className="mx-auto grid min-h-screen max-w-[1600px] gap-6 p-4 xl:grid-cols-[290px_minmax(0,1fr)]">
        <Sidebar darkMode={darkMode} onToggleDarkMode={() => setDarkMode((value) => !value)} />
        <main className="space-y-6">
          <Topbar />
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/antoine" element={<AntoinePage components={components} />} />
            <Route path="/models" element={<ModelsPage components={components} />} />
            <Route path="/vle" element={<VlePage components={components} />} />
            <Route path="/volume" element={<VolumePage />} />
            <Route path="/graphs" element={<GraphsPage components={components} />} />
            <Route path="/molecules" element={<MoleculesPage components={components} reloadComponents={reloadComponents} />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

