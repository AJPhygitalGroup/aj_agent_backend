'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Rocket, CheckCircle, BarChart3, ExternalLink } from 'lucide-react'

const navItems = [
  { href: '/', label: 'Campaigns', icon: Rocket },
  { href: '/approvals', label: 'Approvals', icon: CheckCircle },
  { href: '/analytics', label: 'Analytics', icon: BarChart3 },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="fixed left-0 top-0 h-screen w-60 bg-white border-r border-gray-200 flex flex-col">
      {/* Brand */}
      <div className="p-6 border-b border-gray-100">
        <h1 className="text-xl font-bold gradient-text">A&J Content Engine</h1>
        <p className="text-xs text-gray-400 mt-1">Automate. Grow. Dominate.</p>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-brand-blue/10 text-brand-blue'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-100">
        <a
          href="https://www.ajphygitalgroup.com"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 text-xs text-gray-400 hover:text-brand-blue transition-colors"
        >
          <ExternalLink className="w-3 h-3" />
          ajphygitalgroup.com
        </a>
      </div>
    </aside>
  )
}
