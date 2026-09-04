import { DashboardSidebar } from "@/components/dashboard-sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="mx-auto flex max-w-6xl gap-8 px-6 py-10">
      <aside className="w-56 shrink-0 border-r border-line">
        <DashboardSidebar />
      </aside>
      <div className="flex-1">{children}</div>
    </div>
  );
}
