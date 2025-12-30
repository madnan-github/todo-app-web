"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { TagInput } from "./tag-input";
import { useTags } from "@/hooks/useTags";
import type { Task, Tag } from "@/types";

interface TaskFormProps {
  onSubmit: (data: {
    title: string;
    description?: string;
    priority: "high" | "medium" | "low";
    tag_ids?: number[];
  }) => Promise<void>;
  isLoading?: boolean;
  initialData?: Partial<Task>;
}

export function TaskForm({ onSubmit, isLoading = false, initialData }: TaskFormProps) {
  const [title, setTitle] = useState(initialData?.title || "");
  const [description, setDescription] = useState(initialData?.description || "");
  const [priority, setPriority] = useState<"high" | "medium" | "low">(
    (initialData?.priority as "high" | "medium" | "low") || "medium"
  );
  const [selectedTags, setSelectedTags] = useState<Tag[]>([]);

  const { tags, fetchTags, createTag, isLoading: isTagsLoading } = useTags();

  // Load available tags on mount
  useEffect(() => {
    fetchTags({ per_page: 100 });
  }, [fetchTags]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    await onSubmit({
      title,
      description: description || undefined,
      priority,
      tag_ids: selectedTags.length > 0 ? selectedTags.map((t) => t.id) : undefined,
    });

    // Reset form if not editing
    if (!initialData) {
      setTitle("");
      setDescription("");
      setPriority("medium");
      setSelectedTags([]);
    }
  };

  const handleCreateTag = async (name: string): Promise<Tag> => {
    return createTag(name);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Input
          placeholder="What needs to be done?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full"
          disabled={isLoading}
          maxLength={200}
        />
        {title.length > 180 && (
          <p className="mt-1 text-xs text-gray-500">{title.length}/200 characters</p>
        )}
      </div>

      <div>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Description (optional)"
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder:text-gray-400"
          rows={2}
          maxLength={1000}
          disabled={isLoading}
        />
      </div>

      <div className="flex items-center gap-4">
        <div className="flex-1">
          <Select
            value={priority}
            onChange={(e) => setPriority(e.target.value as "high" | "medium" | "low")}
            options={[
              { value: "high", label: "High" },
              { value: "medium", label: "Medium" },
              { value: "low", label: "Low" },
            ]}
            disabled={isLoading}
          />
        </div>

        <Button type="submit" disabled={isLoading || !title.trim()} className="mt-5">
          {isLoading ? "Adding..." : initialData ? "Update Task" : "Add Task"}
        </Button>
      </div>

      {/* T128: Tag input */}
      <TagInput
        selectedTags={selectedTags}
        onTagsChange={setSelectedTags}
        availableTags={tags}
        onCreateTag={handleCreateTag}
        isLoading={isTagsLoading}
      />
    </form>
  );
}
