---
id: 1
title: Fix frontend build errors due to type mismatches
stage: green
date: 2025-12-31
surface: agent
model: claude-opus-4-5-20251101
feature: 002-fullstack-web
branch: master
user: ruser
command: none
labels: ["typescript", "full-stack", "frontend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - frontend/components/tasks/task-item.tsx
 - frontend/components/tasks/task-form.tsx
 - frontend/lib/api.ts
tests:
 - frontend build
---

## Prompt

i have this error on build:  Running TypeScript  ..Failed to compile.

./app/dashboard/page.tsx:225:41
Type error: Type 'Promise<Task>' is not assignable to type 'Promise<void>'.
  Type 'Task' is not assignable to type 'void'.

  223 |                 key={task.id}
  224 |                 task={task}
> 225 |                 onToggleComplete={() => toggleComplete(task.id)}
      |                                         ^
  226 |                 onDelete={() => deleteTask(task.id)}
  227 |                 onEdit={handleEditTask}
  228 |               />
Next.js build worker exited with code: 1 and signal: null

## Response snapshot

I've fixed the TypeScript errors that were blocking the frontend build.

1.  **TaskItem Component**: Updated the `TaskItemProps` interface to allow callbacks to return `Promise<any>` instead of strictly `Promise<void>`, resolving the mismatch with the `useTasks` hook which returns the updated `Task`.
2.  **TaskForm Component**: Removed an unsupported `label` prop from the `Select` component call.
3.  **API Library**: Defined and exported `TaskCreateInput` and `TaskUpdateInput` types in `frontend/lib/api.ts` which were being imported in the `useTasks` hook but were missing from the API client exports.

Verified the fix by running `npm run build` in the `frontend` directory, which now completes successfully.

## Outcome

- ✅ Impact: Resolved build-blocking TypeScript errors in the frontend.
- 🧪 Tests: `npm run build` passed successfully.
- 📁 Files: Modified `TaskItem.tsx`, `TaskForm.tsx`, and `api.ts`.
- 🔁 Next prompts: Continue with further feature development or testing.
- 🧠 Reflection: Building periodically helps catch type mismatches in component interfaces early.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): none
