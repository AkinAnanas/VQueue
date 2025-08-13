import type { JSX } from "react";
import { createContext, useContext, useState, useEffect } from "react";
import { jwtDecode } from "jwt-decode";
import { baseUrl } from "../config";

interface Credentials {
  email: string;
  password: string;
}

interface UserDetails {
  email: string;
  password: string;
  name: string;
  location: string;
}

interface AuthContextType {
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  login: (credentials: Credentials) => any;
  logout: () => void;
  register: (user: UserDetails) => void;
  refresh: () => any;
  error: string | null;
  loading: boolean;
}

export const AuthContext = createContext<AuthContextType>({
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  login: (_: Credentials) => [null, null],
  logout: () => {},
  register: (_: UserDetails) => {},
  refresh: async () => [null, null],
  error: null,
  loading: false,
});

export function AuthProvider({ children }: { children: JSX.Element[] }) {
  const [accessToken, setAccessToken] = useState(
    localStorage.getItem("access_token")
  );
  const [refreshToken, setRefreshToken] = useState(
    localStorage.getItem("refresh_token")
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const isAuthenticated = !!accessToken;

  async function login({
    email,
    password,
  }: {
    email: string;
    password: string;
  }) {
    setLoading(true);
    setError(null);

    const params = { email, password };

    try {
      const response = await fetch(`${baseUrl}/auth/provider/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Login failed");
      }

      const access_token = data?.body?.access_token;
      const refresh_token = data?.body?.refresh_token;

      if (!access_token || !refresh_token) {
        throw new Error("Missing access or refresh token in response");
      }

      localStorage.setItem("access_token", access_token);
      localStorage.setItem("refresh_token", refresh_token);
      setAccessToken(access_token);
      setRefreshToken(refresh_token);
      return [access_token, refresh_token];
    } catch (err: any) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  async function logout() {
    setLoading(true);
    setError(null);

    const token = localStorage.getItem("access_token");

    try {
      const response = await fetch(`${baseUrl}/auth/provider/logout`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify({}),
      });

      // If token is invalid or expired, treat it as a successful logout
      if (response.status === 401 || response.status === 403) {
        console.warn("Token was already invalid or expired.");
      } else if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Logout failed");
      } else {
        await response.json();
        console.log("Logged out successfully");
      }
    } catch (err: any) {
      // Only show error if it's unexpected
      if (err.message !== "Logout failed") {
        console.error("Logout error:", err.message);
      }
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      setAccessToken(null);
      setRefreshToken(null);
      setLoading(false);
    }
  }

  async function register({
    email,
    password,
    name,
    location,
  }: {
    email: string;
    password: string;
    name: string;
    location: string;
  }) {
    setLoading(true);
    setError(null);

    const params = { email, password, name, location };

    try {
      const response = await fetch(`${baseUrl}/auth/provider/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(`${data.detail}`);
      }

      await response.json();
    } catch (err: any) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  async function refresh() {
    setLoading(true);
    setError(null);

    const token = localStorage.getItem("refresh_token");

    try {
      const response = await fetch(`${baseUrl}/auth/refresh`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ refresh_token: token }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Token refresh failed");
      }

      const new_access_token = data?.body?.access_token;
      const new_refresh_token = data?.body?.refresh_token;

      if (!new_access_token || !new_refresh_token) {
        throw new Error("Missing access or refresh token in response");
      }

      localStorage.setItem("access_token", new_access_token);
      localStorage.setItem("refresh_token", new_refresh_token);
      setAccessToken(new_access_token);
      setRefreshToken(new_refresh_token);
      return [new_access_token, new_refresh_token];
    } catch (err: any) {
      setError(err.message || "Unknown error");
      logout();
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (accessToken) {
      const { exp } = jwtDecode(accessToken);
      const timeout = exp!! * 1000 - Date.now();
      setTimeout(() => logout(), timeout);
    }
  }, [accessToken]);

  return (
    <AuthContext.Provider
      value={{
        login,
        logout,
        register,
        refresh,
        accessToken,
        refreshToken,
        isAuthenticated,
        error,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
