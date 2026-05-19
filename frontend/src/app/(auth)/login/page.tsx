import { LoginForm } from "@/components/auth/LoginForm";

export const metadata = { title: "Вхід — Freelance Platform" };

export default function LoginPage() {
  return (
    <main className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
          <div className="mb-8 text-center">
            <h1 className="text-2xl font-bold text-gray-900">Вхід</h1>
            <p className="mt-1 text-sm text-gray-500">
              Увійдіть у свій акаунт
            </p>
          </div>
          <LoginForm />
        </div>
      </div>
    </main>
  );
}
