import { useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { Home, Video, FileText, Settings, X } from "lucide-react";

interface MobileSidebarProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

const MobileSidebar: React.FC<MobileSidebarProps> = ({ sidebarOpen, setSidebarOpen }) => {
  const trigger = useRef<HTMLButtonElement>(null);
  const sidebar = useRef<HTMLElement>(null);

  // close on click outside
  useEffect(() => {
    const clickHandler = ({ target }: MouseEvent) => {
      if (!sidebar.current || !trigger.current) return;
      if (
        !sidebarOpen ||
        sidebar.current.contains(target as Node) ||
        trigger.current.contains(target as Node)
      )
        return;
      setSidebarOpen(false);
    };
    document.addEventListener("click", clickHandler);
    return () => document.removeEventListener("click", clickHandler);
  });

  return (
    <div className={`lg:hidden`}>
      {/* Background overlay */}
      <div
        className={`fixed inset-0 bg-slate-900 bg-opacity-30 z-40 ${
          sidebarOpen ? "" : "hidden"
        }`}
        onClick={() => setSidebarOpen(false)}
      ></div>

      <aside
        ref={sidebar}
        className={`fixed left-0 top-0 z-50 flex h-screen w-64 flex-col overflow-y-hidden bg-blue-950 text-white duration-300 ease-in-out ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between gap-2 px-6 py-5.5">
          <Link to="/">
            <h2 className="text-2xl font-bold">
              <img src="/logo.png" alt="stairs" />
            </h2>
          </Link>
          <button
            ref={trigger}
            onClick={() => setSidebarOpen(false)}
            className="text-slate-400 hover:text-slate-200"
          >
            <X size={24} />
          </button>
        </div>
        <nav className="flex-1 px-4 py-4">
          <ul className="flex flex-col gap-1.5">
            <li>
              <Link
                to="/"
                onClick={() => setSidebarOpen(false)}
                className="flex items-center gap-2.5 rounded-md py-2 px-4 font-medium hover:bg-blue-900"
              >
                <Home /> Dashboard
              </Link>
            </li>
            <li>
              <Link
                to="/cameras"
                onClick={() => setSidebarOpen(false)}
                className="flex items-center gap-2.5 rounded-md py-2 px-4 font-medium hover:bg-blue-900"
              >
                <Video /> Cámaras
              </Link>
            </li>
            <li>
              <Link
                to="/reports"
                onClick={() => setSidebarOpen(false)}
                className="flex items-center gap-2.5 rounded-md py-2 px-4 font-medium hover:bg-blue-900"
              >
                <FileText /> Reportes
              </Link>
            </li>
            <li>
              <Link
                to="/settings"
                onClick={() => setSidebarOpen(false)}
                className="flex items-center gap-2.5 rounded-md py-2 px-4 font-medium hover:bg-blue-900"
              >
                <Settings /> Configuración
              </Link>
            </li>
          </ul>
        </nav>
      </aside>
    </div>
  );
};

export default MobileSidebar;
