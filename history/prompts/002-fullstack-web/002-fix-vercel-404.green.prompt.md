---
id: 2
title: Fix Vercel 404 by adding monorepo configuration
stage: green
date: 2025-12-31
surface: agent
model: claude-opus-4-5-20251101
feature: 002-fullstack-web
branch: master
user: ruser
command: none
labels: ["vercel", "deployment", "monorepo"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - vercel.json
---

## Prompt

on vercel having: 404: NOT_FOUND
Code: NOT_FOUND
ID: dxb1::qttsk-1767127224385-2c23988c0611

## Response snapshot

I've added a `vercel.json` configuration file at the root of the project to correctly handle the monorepo structure.

The issue was likely because Vercel was looking for the Next.js application at the root level, but it's actually located in the `frontend/` directory. The new `vercel.json` explicitly sets the `rootDirectory` to `frontend`, ensuring that Vercel finds the `package.json` and `app/` directory correctly for deployment.

## Outcome

- ✅ Impact: Provided Vercel with the correct directory structure for deployment.
- 📁 Files: Created root `vercel.json`.
- 🧠 Reflection: Monorepos always need explicit root directory configuration for deployment platforms.
