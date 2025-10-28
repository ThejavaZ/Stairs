import { Link, useLocation } from "react-router-dom";
import { Home, Video, FileText, Settings } from "lucide-react";

const Sidebar = () => {
  const location = useLocation();
  const { pathname } = location;

  return (
    <aside className="w-64 flex-shrink-0 bg-blue-950 text-white p-4 hidden lg:block">
      <div className="mb-8">
        <Link to="/">
          <h2 className="text-2xl font-bold">
            <img className="w-40" src="/logo.png" alt="stairs" />
          </h2>
        </Link>
      </div>
      <nav>
        <ul className="flex flex-col gap-1.5">
          <li>
            <Link
              to="/"
              className={`group relative flex items-center gap-2.5 rounded-md py-2 px-4 font-medium duration-300 ease-in-out hover:bg-blue-900 ${
                pathname === "/" && "bg-blue-900"
              }`}
            >
              <Home /> Dashboard
            </Link>
          </li>
          <li>
            <Link
              to="/cameras"
              className={`group relative flex items-center gap-2.5 rounded-md py-2 px-4 font-medium duration-300 ease-in-out hover:bg-blue-900 ${
                pathname.includes("cameras") && "bg-blue-900"
              }`}
            >
              <Video /> Cámaras
            </Link>
          </li>
          <li>
            <Link
              to="/reports"
              className={`group relative flex items-center gap-2.5 rounded-md py-2 px-4 font-medium duration-300 ease-in-out hover:bg-blue-900 ${
                pathname.includes("reports") && "bg-blue-900"
              }`}
            >
              <FileText /> Reportes
            </Link>
          </li>
          <li>
            <Link
              to="/settings"
              className={`group relative flex items-center gap-2.5 rounded-md py-2 px-4 font-medium duration-300 ease-in-out hover:bg-blue-900 ${
                pathname.includes("settings") && "bg-blue-900"
              }`}
            >
              <Settings /> Configuración
            </Link>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
