import React from "react";
import {
  Home,
  MessageCircle,
  BarChart3,
  ShieldCheck,
  FileText,
  Menu,
  X,
} from "lucide-react";

interface NavItem {
  id: string;
  label: string;
  icon: React.ElementType;
}

const navItems: NavItem[] = [
  { id: "overview", label: "Overview", icon: Home },
  { id: "ask-skylark", label: "Ask Skylark", icon: MessageCircle },
  { id: "insights", label: "Insights", icon: BarChart3 },
  { id: "data-health", label: "Data Health", icon: ShieldCheck },
  { id: "leadership-update", label: "Leadership Update", icon: FileText },
];

interface SidebarProps {
  activePage?: string;
  onNavigate?: (page: string) => void;
}

export default function Sidebar({ activePage = "overview", onNavigate }: SidebarProps) {
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const handleNav = (id: string) => {
    onNavigate?.(id);
    setMobileOpen(false);
  };

  return (
    <>
      {/* Mobile hamburger */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        className="fixed left-4 top-4 z-50 p-2 rounded-lg hover:bg-white/10 transition-colors md:hidden"
        aria-label="Toggle navigation"
      >
        {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar panel */}
      <aside
        className={`fixed left-0 top-0 bottom-0 w-64 bg-slate-900 border-r border-white/10 z-50 transition-transform
          ${mobileOpen ? "translate-x-0" : "-translate-x-full"} md:translate-x-0`}
      >
        <div className="px-6 py-5 border-b border-white/10">
          <h2 className="text-xl font-bold tracking-tight text-white">SKYLARK</h2>
          <p className="text-xs text-slate-400 mt-1 tracking-wide">Founder Intelligence</p>
        </div>

        <nav className="px-3 py-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNav(item.id)}
                className={`w-full flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors
                  ${active
                    ? "bg-indigo-600/20 text-indigo-400"
                    : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
                  }`}
                aria-label={item.label}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                {item.label}
              </button>
            );
          })}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 px-6 py-4 border-t border-white/10">
          <p className="text-xs text-slate-500">Skylark Drones BI</p>
          <p className="text-xs text-slate-600 mt-0.5">v0.2.0</p>
        </div>
      </aside>
    </>
  );
}