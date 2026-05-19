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

const schema = z
  .object({
    email: z.string().email("Невірний формат email"),
    password: z.string().min(8, "Мінімум 8 символів"),
    confirmPassword: z.string().min(1, "Підтвердіть пароль"),
  })
  .refine((d) => d.password === d.confirmPassword, {
    message: "Паролі не співпадають",
    path: ["confirmPassword"],
  });

type FormData = z.infer<typeof schema>;

export function RegisterForm() {
  const router = useRouter();
  const { register: registerUser, login, isLoading } = useAuthStore();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormData) => {
    setServerError(null);
    try {
      await registerUser({ email: data.email, password: data.password });
      await login({ email: data.email, password: data.password });
      router.push("/dashboard");
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      setServerError(
        status === 409
          ? "Цей email вже зареєстрований"
          : "Щось пішло не так. Спробуйте ще раз."
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
        placeholder="Мінімум 8 символів"
        error={errors.password?.message}
        {...register("password")}
      />
      <Input
        label="Підтвердження паролю"
        type="password"
        placeholder="Повторіть пароль"
        error={errors.confirmPassword?.message}
        {...register("confirmPassword")}
      />

      {serverError && (
        <p className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600 border border-red-200">
          {serverError}
        </p>
      )}

      <Button type="submit" isLoading={isLoading} className="w-full mt-1">
        Створити акаунт
      </Button>

      <p className="text-center text-sm text-gray-500">
        Вже є акаунт?{" "}
        <Link href="/login" className="text-indigo-600 hover:underline font-medium">
          Увійти
        </Link>
      </p>
    </form>
  );
}
