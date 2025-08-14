import { createContext, useContext } from "react";
import { baseUrl } from "../config";
import { useState } from "react";
import type { JSX } from "react";

export interface QueueInfo {
  code?: string;
  name: string;
  is_open: boolean;
  max_block_capacity: number;
  max_party_capacity: number;
  size: number;
  wait_time_estimate: string;
  manual_dispatch: boolean;
  description: string;
  image_url: string;
  service_provider_id?: number;
}

interface SearchParams {
  search?: string;
  limit: number;
  offset: number;
  token: string;
}

interface QueueContextType {
  loading: boolean;
  error: string | null;
  fetchQueues: (params: SearchParams) => Promise<QueueInfo[]>;
  getQueue: (params: {
    code: string;
    token: string;
  }) => Promise<QueueInfo | null>;
  createQueue: (params: { info: QueueInfo; token: string }) => void;
}

export const QueueContext = createContext<QueueContextType>({
  loading: false,
  error: null,
  fetchQueues: async (_: SearchParams) => {
    return [];
  },
  getQueue: async (_: { code: string; token: string }) => {
    return null;
  },
  createQueue: async (_: { info: QueueInfo; token: string }) => {},
});

export function QueueProvider({ children }: { children: JSX.Element }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function fetchQueues({
    search,
    limit = 50,
    offset = 0,
    token,
  }: {
    search?: string;
    limit: number;
    offset: number;
    token: string;
  }) {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        limit: limit.toString(), // optional, defaults to 50
        offset: offset.toString(), // optional, defaults to 0
      });

      if (search) {
        params.append("search", search);
      }

      const response = await fetch(`${baseUrl}/queues/?${params.toString()}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch queues");
      }

      console.log(response);
      const data = await response.json();
      return data.body as QueueInfo[];
    } catch (err: any) {
      setError(err.message || "Unknown error");
      return [];
    } finally {
      setLoading(false);
    }
  }

  async function getQueue({
    code,
    token,
  }: {
    code: string;
    token: string;
  }): Promise<QueueInfo | null> {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${baseUrl}/queues/${code}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.status === 404) {
        return null;
      }

      if (!response.ok) {
        throw new Error("Failed to fetch queue");
      }

      const data = await response.json();
      return data as QueueInfo;
    } catch (err: any) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
      return null;
    }
  }

  async function createQueue(params: { info: QueueInfo; token: string }) {
    setLoading(true);
    setError(null);
    const body = JSON.stringify(params.info);

    try {
      const response = await fetch(`${baseUrl}/queue/create`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${params.token}`,
        },
        body: body,
      });

      if (!response.ok) {
        throw new Error("Failed to create queue: " + body);
      }
    } catch (err: any) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <QueueContext.Provider
      value={{ loading, error, fetchQueues, getQueue, createQueue }}
    >
      {children}
    </QueueContext.Provider>
  );
}

export function useQueues() {
  return useContext(QueueContext);
}
