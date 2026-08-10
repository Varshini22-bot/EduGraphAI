import { getToken } from "@/utils/token";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://127.0.0.1:8000";

export interface User {
  id?: number;
  name?: string;
  full_name?: string;
  email: string;
  plan?: string;
  is_active?: boolean;
  created_at?: string;
}

// ========================================
// LOGIN
// ========================================

export async function login(data: {
  email: string;
  password: string;
}) {
  const response = await fetch(
    `${API_BASE_URL}/auth/login`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/x-www-form-urlencoded",
      },

      body: new URLSearchParams({
        username: data.email,
        password: data.password,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(
      "Invalid email or password"
    );
  }

  return response.json();
}

// ========================================
// REGISTER
// ========================================

export async function register(data: {
  email: string;
  password: string;
  full_name?: string;
}) {
  const response = await fetch(
    `${API_BASE_URL}/auth/register`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify(data),
    }
  );

  if (!response.ok) {
    throw new Error(
      "Registration failed"
    );
  }

  return response.json();
}

// ========================================
// CURRENT USER
// ========================================

export async function getCurrentUser() {
  const token = getToken();

  if (!token) {
    return null;
  }

  const response = await fetch(
    `${API_BASE_URL}/auth/me`,
    {
      method: "GET",

      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error(
      "Unable to fetch current user"
    );
  }

  const backendUser = await response.json();

  return {
    ...backendUser,

    name:
      backendUser.full_name ||
      backendUser.name ||
      "User",

    plan:
      backendUser.plan ||
      "Free",
  };
}