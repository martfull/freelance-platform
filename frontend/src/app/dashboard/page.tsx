"use client";

import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui/Button";

export default function DashboardPage() {
  const router = useRouter();
  const { user, logout, isLoading } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
          <span className="font-semibold text-gray-900">Freelance Platform</span>
          <Button variant="ghost" onClick={handleLogout} isLoading={isLoading}>
            Вийти
          </Button>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-4 py-10">
        <div className="bg-white rounded-2xl border border-gray-200 p-8">
          <h1 className="text-xl font-bold text-gray-900 mb-4">Дашборд</h1>
          {user ? (
            <div className="space-y-2 text-sm text-gray-600">
              <p><span className="font-medium text-gray-800">Email:</span> {user.email}</p>
              <p><span className="font-medium text-gray-800">Роль:</span> {user.system_role}</p>
              <p><span className="font-medium text-gray-800">ID:</span> {user.id}</p>
            </div>
          ) : (
            <p className="text-gray-400 text-sm">Завантаження...</p>
          )}
        </div>
      </div>
    </main>
  );
}
