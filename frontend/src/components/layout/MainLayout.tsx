import { Outlet } from "react-router-dom"
import { Sidebar } from "./Sidebar"

export function MainLayout() {
    return (
        <div className="flex h-screen overflow-hidden bg-[#0f111a]">
            <Sidebar />
            <main className="flex-1 overflow-y-auto overflow-x-hidden">
                <Outlet />
            </main>
        </div>
    )
}
