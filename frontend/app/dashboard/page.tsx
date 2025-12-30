"use client";

import { useEffect, useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";
import { useTasks } from "@/hooks/useTasks";
import { useTags } from "@/hooks/useTags";
import { useTaskFilters } from "@/hooks/useTaskFilters";
import { TaskSearch } from "@/components/tasks/task-search";
import { TaskFilter } from "@/components/tasks/task-filter";
import { TaskSort } from "@/components/tasks/task-sort";
import { TaskForm } from "@/components/tasks/task-form";
import { TaskItem } from "@/components/tasks/task-item";
import type { Task } from "@/types";

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading, signOut } = useAuth();
  const {
    tasks,
    isLoading: tasksLoading,
    fetchTasks,
    createTask,
    toggleComplete,
    deleteTask,
  } = useTasks();
  const { tags, fetchTags } = useTags();
  const {
    search,
    setSearch,
    status,
    setStatus,
    priorities,
    setPriorities,
    tags: selectedTagIds,
    setTags,
    sortBy,
    sortOrder,
    setSortBy,
    setSortOrder,
    clearFilters,
    activeFilterCount,
  } = useTaskFilters();

  const [isCreating, setIsCreating] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  // Redirection when not logged in
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/");
    }
  }, [authLoading, isAuthenticated, router]);

  // Load data on mount
  useEffect(() => {
    if (isAuthenticated) {
      fetchTasks();
      fetchTags();
    }
  }, [isAuthenticated, fetchTasks, fetchTags]);

  // Refetch when filters change (T139, T153)
  const handleFilterChange = useCallback(() => {
    const params: Record<string, any> = {};

    // Status filter
    if (status === "active") params.completed = false;
    if (status === "completed") params.completed = true;

    // Priority filter (T147 - comma-separated for multiple)
    if (priorities.length > 0) params.priority = priorities.join(",");

    // Tag filter (T148 - comma-separated for multiple)
    if (selectedTagIds.length > 0) params.tag_ids = selectedTagIds.join(",");

    // Search (T134)
    if (search) params.search = search;

    // Sort (T158, T159)
    params.sort_by = sortBy;
    params.sort_order = sortOrder;

    fetchTasks(params);
  }, [status, priorities, selectedTagIds, search, sortBy, sortOrder, fetchTasks]);

  // Trigger filter change when any filter updates
  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      handleFilterChange();
    }
  }, [status, priorities, selectedTagIds, search, sortBy, sortOrder, authLoading, isAuthenticated, handleFilterChange]);

  // Task CRUD handlers
  const handleCreateTask = async (data: {
    title: string;
    description?: string;
    priority: "high" | "medium" | "low";
    tag_ids?: number[];
  }) => {
    setIsCreating(true);
    try {
      await createTask(data);
    } finally {
      setIsCreating(false);
    }
  };

  const handleEditTask = (task: Task) => {
    setEditingTask(task);
  };

  const handleSaveTask = async (taskId: number, data: Partial<Task>) => {
    await fetchTasks(); // Refresh after update
  };

  // Authentication check
  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 dark:bg-gray-800 dark:border-gray-700">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white font-bold">
              T
            </div>
            <span className="text-xl font-bold text-gray-900 dark:text-white">
              TaskFlow
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {user?.name || user?.email}
            </span>
            <Button variant="outline" size="sm" onClick={() => signOut()}>
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Create Task Form */}
        <Card className="mb-8">
          <CardContent className="pt-6">
            <TaskForm
              onSubmit={handleCreateTask}
              isLoading={isCreating}
            />
          </CardContent>
        </Card>

        {/* Search and Filter Bar */}
        <div className="mb-6 space-y-4">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            {/* Search input (T136, T137) */}
            <TaskSearch
              value={search}
              onChange={setSearch}
              onSearch={handleFilterChange}
            />

            {/* Sort controls (T163, T164, T165) */}
            <TaskSort
              sortBy={sortBy}
              sortOrder={sortOrder}
              onSortChange={setSortBy}
              onOrderChange={setSortOrder}
              isLoading={tasksLoading}
            />
          </div>

          {/* Filter controls (T149-T156) */}
          <TaskFilter
            statusFilter={status}
            onStatusChange={setStatus}
            selectedPriorities={priorities}
            onPriorityChange={setPriorities}
            selectedTags={selectedTagIds}
            onTagChange={setTags}
            availableTags={tags}
            onClearFilters={clearFilters}
            isLoading={tasksLoading}
          />
        </div>

        {/* Task List */}
        {tasksLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : tasks.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-gray-500 dark:text-gray-400">
                {activeFilterCount > 0
                  ? "No tasks match your filters"
                  : search
                  ? "No tasks match your search"
                  : "No tasks yet. Create your first task above!"}
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {tasks.map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                onToggleComplete={() => toggleComplete(task.id)}
                onDelete={() => deleteTask(task.id)}
                onEdit={handleEditTask}
              />
            ))}
          </div>
        )}

        {/* Task Count */}
        <div className="mt-6 text-sm text-gray-500 dark:text-gray-400">
          {tasks.filter((t) => !t.completed).length} tasks remaining
        </div>
      </main>

      {/* Edit Modal */}
      {editingTask && (
        <TaskEditModal
          task={editingTask}
          isOpen={!!editingTask}
          onClose={() => setEditingTask(null)}
          onSave={handleSaveTask}
          availableTags={tags}
        />
      )}
    </div>
  );
}

// Import TaskEditModal at the bottom to avoid circular dependency
import { TaskEditModal } from "@/components/tasks/task-edit-modal";
