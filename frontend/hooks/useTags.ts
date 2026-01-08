"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { api, type Tag } from "@/lib/api";

export function useTags() {
  const [tags, setTags] = useState<Tag[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTags = useCallback(
    async (params?: { search?: string; page?: number; per_page?: number }) => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await api.getTags(params);
        setTags(response.tags);
        return response;
      } catch (err: any) {
        // Silently handle 401 (authentication) errors - user is not logged in
        if (err.statusCode === 401) {
          setTags([]);
          return { tags: [], total: 0, page: 1, per_page: 100 };
        }
        setError(err.message || "Failed to fetch tags");
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  // T126: Debounced autocomplete for tag search
  const useTagAutocomplete = () => {
    const [suggestions, setSuggestions] = useState<string[]>([]);
    const [isSearching, setIsSearching] = useState(false);
    const debounceRef = useRef<NodeJS.Timeout | null>(null);

    const search = useCallback(async (query: string) => {
      // Clear previous debounce
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }

      if (!query.trim()) {
        setSuggestions([]);
        return;
      }

      // Debounce API call (300ms delay)
      debounceRef.current = setTimeout(async () => {
        setIsSearching(true);
        try {
          const response = await api.getTagsAutocomplete(query);
          setSuggestions(response.suggestions);
        } catch (err) {
          setSuggestions([]);
        } finally {
          setIsSearching(false);
        }
      }, 300);
    }, []);

    useEffect(() => {
      return () => {
        if (debounceRef.current) {
          clearTimeout(debounceRef.current);
        }
      };
    }, []);

    return { suggestions, isSearching, search };
  };

  const createTag = useCallback(async (name: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const tag = await api.createTag(name);
      setTags((prev) => [...prev, tag]);
      return tag;
    } catch (err: any) {
      setError(err.message || "Failed to create tag");
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deleteTag = useCallback(async (tagId: number) => {
    setIsLoading(true);
    setError(null);
    try {
      await api.deleteTag(tagId);
      setTags((prev) => prev.filter((t) => t.id !== tagId));
    } catch (err: any) {
      setError(err.message || "Failed to delete tag");
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    tags,
    setTags,
    isLoading,
    error,
    fetchTags,
    createTag,
    deleteTag,
    useTagAutocomplete,
  };
}
