import { Search, HelpCircle, Info } from 'lucide-react';

interface HeaderProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

const Header: React.FC<HeaderProps> = ({ sidebarOpen, setSidebarOpen }) => {
  return (
    <header className="sticky top-0 bg-blue-950 z-30">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 -mb-px">

          {/* Header: Left side */}
          <div className="flex">
            {/* Hamburger button */}
            <button
              className="text-slate-400 hover:text-slate-500 lg:hidden"
              aria-controls="sidebar"
              aria-expanded={sidebarOpen}
              onClick={(e) => { e.stopPropagation(); setSidebarOpen(!sidebarOpen); }}
            >
              <span className="sr-only">Open sidebar</span>
              <svg className="w-6 h-6 fill-current" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <rect x="4" y="5" width="16" height="2" />
                <rect x="4" y="11" width="16" height="2" />
                <rect x="4" y="17" width="16" height="2" />
              </svg>
            </button>
          </div>

          {/* Header: Center */}
          <div className="flex-1 flex justify-center px-4">
            <div className="relative w-full max-w-md">
                <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                    <Search className="h-5 w-5 text-gray-400" />
                </span>
                <input 
                    type="text" 
                    placeholder="Búsqueda global..." 
                    className="w-full pl-10 pr-4 py-2 rounded-lg bg-blue-900 text-white border border-transparent focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
            </div>
          </div>

          {/* Header: Right side */}
          <div className="flex items-center space-x-3">
            <button className="p-2 text-slate-400 hover:text-slate-200 rounded-full">
                <HelpCircle />
            </button>
            <button className="p-2 text-slate-400 hover:text-slate-200 rounded-full">
                <Info />
            </button>
            {/* You can add user profile/avatar here */}
          </div>

        </div>
      </div>
    </header>
  );
};

export default Header;