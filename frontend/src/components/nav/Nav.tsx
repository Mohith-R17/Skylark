import React from "react";
{/* Lucide icons will be used for navigation items */}

type NavLink = {
  href: string;
  label: string;
  icon?: React.ElementType;
};

const NavLinks: NavLink[] = [
  { href: "#overview", label: "Overview" },
  { href: "#ask-skylark", label: "Ask Skylark" },
  { href: "#insights", label: "Insights" },
  { href: "#data-health", label: "Data Health" },
  { href: "#leadership-update", label: "Leadership Update" },
];

export default function Nav() {
  return (
    <div className="flex items-center gap-2">
      {NavLinks.map((link) => (
        <a
          key={link.label}
          href={link.href}
          className="text-sm font-medium hover:text-primary transition-colors"
        >
          {link.label}
        </a>
      ))}
    </div>
  );
}

export type { NavLink };