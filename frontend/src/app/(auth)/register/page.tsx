import { RegisterForm } from "@/components/auth/RegisterForm";

export const metadata = { title: "Реєстрація — Freelance Platform" };

export default function RegisterPage() {
  return (
    <main className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
          <div className="mb-8 text-center">
            <h1 className="text-2xl font-bold text-gray-900">Реєстрація</h1>
            <p className="mt-1 text-sm text-gray-500">
              Створіть новий акаунт
            </p>
          </div>
          <RegisterForm />
        </div>
      </div>
    </main>
  );
}
