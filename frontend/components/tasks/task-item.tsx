"use client";

import { memo, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { formatDate, getPriorityColor } from "@/lib/utils";
import type { Task } from "@/types";

// T175: React.memo to prevent unnecessary re-renders
export const TaskItem = memo(function TaskItem({
  task,
  onToggleComplete,
  onDelete,
  onEdit,
}: TaskItemProps) {
  const [isToggling, setIsToggling] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleToggle = async () => {
    if (isToggling) return;
    setIsToggling(true);
    try {
      await onToggleComplete(task.id);
    } finally {
      setIsToggling(false);
    }
  };

  const handleDelete = async () => {
    if (isDeleting) return;
    if (!confirm("Are you sure you want to delete this task?")) return;
    setIsDeleting(true);
    try {
      await onDelete(task.id);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <Card className={task.completed ? "opacity-60" : ""}>
      <CardContent className="flex items-center gap-4 py-4">
        <input
          type="checkbox"
          checked={task.completed}
          onChange={handleToggle}
          disabled={isToggling}
          className="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          aria-label={`Mark task "${task.title}" as ${task.completed ? "incomplete" : "complete"}`}
        />
        <div className="flex-1 min-w-0">
          <p
            className={`font-medium text-gray-900 dark:text-white truncate ${
              task.completed ? "line-through text-gray-500" : ""
            }`}
          >
            {task.title}
          </p>
          {task.description && (
            <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
              {task.description}
            </p>
          )}
          <div className="mt-2 flex items-center gap-2 flex-wrap">
            <Badge className={getPriorityColor(task.priority)}>
              {task.priority}
            </Badge>
            {task.tags && task.tags.length > 0 && (
              <div className="flex gap-1 flex-wrap" role="list" aria-label="Task tags">
                {task.tags.map((tag) => (
                  <Badge key={tag.id} variant="outline" className="text-xs" role="listitem">
                    {tag.name}
                  </Badge>
                ))}
              </div>
            )}
            <span className="text-xs text-gray-400">
              {formatDate(task.created_at)}
            </span>
          </div>
        </div>
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onEdit(task)}
            className="text-gray-600 hover:text-gray-700 hover:bg-gray-100"
            title="Edit task"
            aria-label={`Edit task "${task.title}"`}
          >
            <svg
              className="h-4 w-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleDelete}
            disabled={isDeleting}
            className="text-red-600 hover:text-red-700 hover:bg-red-50"
            title="Delete task"
            aria-label={`Delete task "${task.title}"`}
          >
            <svg
              className="h-4 w-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
});

interface TaskItemProps {
  task: Task;
  onToggleComplete: (taskId: number) => Promise<any>;
  onDelete: (taskId: number) => Promise<any>;
  onEdit: (task: Task) => void;
}
