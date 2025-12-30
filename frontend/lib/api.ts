class APIError extends Error {
  constructor(
    message: string,
    public statusCode: number = 500,
    public code?: string
  ) {
    super(message);
    this.name = "APIError";
  }
}

class APIClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
      credentials: "include",
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.detail || `HTTP error! status: ${response.status}`,
        response.status,
        errorData.error_code
      );
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // Auth endpoints
  async signUp(email: string, password: string, name?: string) {
    return this.request<BetterAuthResponse>("/api/v1/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password, name }),
    });
  }

  async signIn(email: string, password: string) {
    return this.request<BetterAuthResponse>("/api/v1/auth/signin", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  async getSession() {
    return this.request<BetterAuthResponse>("/api/v1/auth/session");
  }

  async signOut() {
    return this.request<{ success: boolean }>("/api/v1/auth/signout", {
      method: "POST",
    });
  }

  // Task endpoints
  async getTasks(params?: {
    completed?: boolean;
    priority?: string;
    tag_id?: number;
    search?: string;
    sort_by?: string;
    sort_order?: string;
    page?: number;
    per_page?: number;
  }) {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value));
        }
      });
    }
    const query = searchParams.toString();
    return this.request<{ tasks: Task[]; total: number; page: number; per_page: number }>(
      `/api/v1/tasks${query ? `?${query}` : ""}`
    );
  }

  async getTask(taskId: number) {
    return this.request<Task>(`/api/v1/tasks/${taskId}`);
  }

  async createTask(data: {
    title: string;
    description?: string;
    priority: "high" | "medium" | "low";
    tag_ids?: number[];
  }) {
    return this.request<Task>("/api/v1/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateTask(taskId: number, data: Partial<Task>) {
    return this.request<Task>(`/api/v1/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteTask(taskId: number) {
    return this.request<void>(`/api/v1/tasks/${taskId}`, {
      method: "DELETE",
    });
  }

  async toggleComplete(taskId: number) {
    return this.request<Task>(`/api/v1/tasks/${taskId}/complete`, {
      method: "PATCH",
    });
  }

  // Tag endpoints
  async getTags(params?: { search?: string; page?: number; per_page?: number }) {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value));
        }
      });
    }
    const query = searchParams.toString();
    return this.request<{ tags: Tag[]; total: number; page: number; per_page: number }>(
      `/api/v1/tags${query ? `?${query}` : ""}`
    );
  }

  async getTagAutocomplete(q: string, limit: number = 10) {
    return this.request<{ suggestions: string[] }>(
      `/api/v1/tags/autocomplete?q=${encodeURIComponent(q)}&limit=${limit}`
    );
  }

  // Alias for getTagAutocomplete (used by useTags hook)
  async getTagsAutocomplete(q: string, limit: number = 10) {
    return this.getTagAutocomplete(q, limit);
  }

  async createTag(name: string) {
    return this.request<Tag>("/api/v1/tags", {
      method: "POST",
      body: JSON.stringify({ name }),
    });
  }

  async deleteTag(tagId: number) {
    return this.request<void>(`/api/v1/tags/${tagId}`, {
      method: "DELETE",
    });
  }
}

export const api = new APIClient();

// Type definitions
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  priority: "high" | "medium" | "low";
  created_at: string;
  updated_at: string;
  tags: Tag[];
}

export type TaskCreateInput = {
  title: string;
  description?: string;
  priority: "high" | "medium" | "low";
  tag_ids?: number[];
};

export type TaskUpdateInput = Partial<TaskCreateInput> & {
  completed?: boolean;
};

export interface Tag {
  id: number;
  user_id: string;
  name: string;
}

export interface BetterAuthResponse {
  user: {
    id: string;
    email: string;
    name: string | null;
  };
  session: {
    token: string;
    expiresAt: string;
  };
}
