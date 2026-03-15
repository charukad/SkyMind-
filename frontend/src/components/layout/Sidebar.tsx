import { Link, useLocation } from "react-router-dom"
import {
    LayoutDashboard,
    Map,
    List,
    Settings,
    Bell
} from "lucide-react"
import { cn } from "../../lib/utils"

export function Sidebar() {
    const location = useLocation()

    const links = [
        { href: "/", label: "Overview", icon: LayoutDashboard },
        { href: "/map", label: "Global Map", icon: Map },
        { href: "/flights", label: "Active Flights", icon: List },
        { href: "/alerts", label: "Alert Center", icon: Bell },
        { href: "/settings", label: "Settings", icon: Settings },
    ]

    return (
        <div className="flex h-screen w-64 flex-col border-r border-[#1e293b] bg-[#0b0d14] px-3 py-4">
            <div className="mb-8 flex items-center px-2">
                <h1 className="text-2xl font-bold tracking-tight text-blue-400">
                    Sky<span className="text-slate-100">Mind</span>
                </h1>
            </div>

            <nav className="flex-1 space-y-1">
                {links.map((link) => {
                    const Icon = link.icon
                    const isActive = location.pathname === link.href

                    return (
                        <Link
                            key={link.href}
                            to={link.href}
                            className={cn(
                                "group flex items-center rounded-md px-3 py-2.5 text-sm font-medium transition-colors",
                                isActive
                                    ? "bg-blue-600/10 text-blue-400"
                                    : "text-slate-400 hover:bg-[#1e293b] hover:text-slate-200"
                            )}
                        >
                            <Icon
                                className={cn(
                                    "mr-3 h-5 w-5 flex-shrink-0 transition-colors",
                                    isActive ? "text-blue-400" : "text-slate-500 group-hover:text-slate-300"
                                )}
                                aria-hidden="true"
                            />
                            {link.label}
                        </Link>
                    )
                })}
            </nav>

            <div className="mt-auto px-3">
                <div className="flex items-center gap-3 rounded-lg bg-[#1e293b]/50 p-3">
                    <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-sm font-bold text-white">
                        DC
                    </div>
                    <div className="flex flex-col">
                        <span className="text-sm font-medium text-slate-200">Director</span>
                        <span className="text-xs text-slate-500">Global Ops</span>
                    </div>
                </div>
            </div>
        </div>
    )
}
