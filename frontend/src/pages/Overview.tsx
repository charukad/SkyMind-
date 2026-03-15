export default function Overview() {
    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold tracking-tight mb-6">Executive Overview</h1>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {/* Metric Cards will go here */}
                <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 shadow-sm">
                    <div className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <h3 className="tracking-tight text-sm font-medium text-slate-400">Total Active Flights</h3>
                    </div>
                    <div className="text-2xl font-bold text-slate-100">---</div>
                </div>
            </div>
        </div>
    )
}
