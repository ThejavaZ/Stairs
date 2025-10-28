import { useState } from "react";
import Header from "../components/header";
import Footer from "../components/footer";
import { Routers } from "../routes/routers";
import Sidebar from "../components/sidebar";
import MobileSidebar from "../components/MobileSidebar";

export const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden bg-slate-100">
      {/* --- Static Sidebar for Desktop --- */}
      <Sidebar />
      
      {/* --- Mobile Sidebar (Drawer) --- */}
      <MobileSidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

      {/* --- Content Area --- */}
      <div className="relative flex flex-1 flex-col overflow-y-auto overflow-x-hidden">
        
        {/* Header */}
        <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

        {/* Main Content */}
        <main className="flex-1 p-6">
          <Routers />
        </main>

        <Footer />
      </div>
    </div>
  );
};