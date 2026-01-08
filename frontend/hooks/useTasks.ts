"use client";

import { useState, useCallback } from "react";
import { api, type Task, type TaskCreateInput, type TaskUpdateInput } from "@/lib/api";

export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(
    async (params?: {
      completed?: boolean;
      priority?: string;
      tag_id?: number;
      tag_ids?: string;  // comma-separated for multiple tags
      search?: string;
      sort_by?: "created_at" | "updated_at" | "title" | "priority";
      sort_order?: "asc" | "desc";
      page?: number;
      per_page?: number;
    }) => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await api.getTasks(params);
        setTasks(response.tasks);
        return response;
      } catch (err: any) {
        // Silently handle 401 (authentication) errors - user is not logged in
        if (err.statusCode === 401) {
          setTasks([]);
          return { tasks: [], total: 0, page: 1, per_page: 20 };
        }
        setError(err.message || "Failed to fetch tasks");
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const createTask = useCallback(
    async (data: TaskCreateInput) => {
      setIsLoading(true);
      setError(null);
      try {
        const task = await api.createTask(data);
        setTasks((prev) => [task, ...prev]);
        return task;
      } catch (err: any) {
        setError(err.message || "Failed to create task");
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const updateTask = useCallback(
    async (taskId: number, data: TaskUpdateInput) => {
      setIsLoading(true);
      setError(null);
      try {
        const task = await api.updateTask(taskId, data);
        setTasks((prev) =>
          prev.map((t) => (t.id === taskId ? task : t))
        );
        return task;
      } catch (err: any) {
        setError(err.message || "Failed to update task");
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const deleteTask = useCallback(async (taskId: number) => {
    setIsLoading(true);
    setError(null);
    try {
      await api.deleteTask(taskId);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
    } catch (err: any) {
      setError(err.message || "Failed to delete task");
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const toggleComplete = useCallback(
    async (taskId: number) => {
      setIsLoading(true);
      setError(null);
      try {
        const task = await api.toggleComplete(taskId);
        setTasks((prev) =>
          prev.map((t) => (t.id === taskId ? task : t))
        );
        return task;
      } catch (err: any) {
        setError(err.message || "Failed to toggle task");
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return {
    tasks,
    setTasks,
    isLoading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleComplete,
  };
}
