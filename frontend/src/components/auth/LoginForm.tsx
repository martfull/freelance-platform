"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

const schema = z.object({
  email: z.string().email("Невірний формат email"),
  password: z.string().min(1, "Введіть пароль"),
});

type FormData = z.infer<typeof schema>;

export function LoginForm() {
  const router = useRouter();
  const { login, isLoading } = useAuthStore();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormData) => {
    setServerError(null);
    try {
      await login(data);
      router.push("/dashboard");
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      setServerError(
        status === 401 ? "Невірний email або пароль" : "Щось пішло не так. Спробуйте ще раз."
      );
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-5">
      <Input
        label="Email"
        type="email"
        placeholder="you@example.com"
        error={errors.email?.message}
        {...register("email")}
      />
      <Input
        label="Пароль"
        type="password"
        placeholder="••••••••"
        error={errors.password?.message}
        {...register("password")}
      />

      {serverError && (
        <p className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600 border border-red-200">
          {serverError}
        </p>
      )}

      <Button type="submit" isLoading={isLoading} className="w-full mt-1">
        Увійти
      </Button>

      <p className="text-center text-sm text-gray-500">
        Немає акаунту?{" "}
        <Link href="/register" className="text-indigo-600 hover:underline font-medium">
          Зареєструватись
        </Link>
      </p>
    </form>
  );
}
