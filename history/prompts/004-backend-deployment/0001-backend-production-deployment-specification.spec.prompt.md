---
id: 0001
title: Backend Production Deployment Specification
stage: spec
date: 2025-12-31
surface: agent
model: claude-opus-4-5-20251101
feature: 004-backend-deployment
branch: 004-backend-deployment
user: madnan-github
command: /sp.specify
labels: ["deployment", "railway", "neon", "fastapi", "production"]
links:
  spec: specs/004-backend-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-backend-deployment/spec.md
  - specs/004-backend-deployment/checklists/requirements.md
tests:
  - none
---

## Prompt

"Direct the backend-deployment-agent to architect a production-ready deployment for the FastAPI backend on Railway and Neon. The
  execution must strictly utilize the following skills: railway_deployment_setup for root Procfile and dynamic port binding logic;
  neon_production_setup to implement asyncpg connection pooling optimized for serverless database architecture; and fastapi_production_config
  for security hardening (CORS, secret externalization, and production-only health endpoints). Post-deployment, the agent must generate a
  comprehensive automated test plan to verify the live environment. This include: 1) Performing deep-health checks on the live Railway endpoint
  to confirm Neon connectivity, 2) Validating JWT authentication and user isolation on the production URL, and 3) Verifying that CORS headers
  correctly allow the Vercel production domain. All configurations must be documented in a final audit report with linkable ADRs for every
  significant architectural decision."

  ---
  Key Enhancements in this Prompt:

  1. Full Lifecycle Coverage: Moves beyond just settings to include live environment verification.
  2. Deep-Health Verification: Explicitly requires testing the "Deep" health check (database connectivity) on the actual live URL, not just a
  local mock.
  3. Cross-Origin Validation: Ensures the production frontend domain (Vercel) is explicitly tested for CORS compliance.
  4. JWT Production Audit: Forces a check on secure token handling and user data isolation in a real production context.
  5. Artifact Traceability: Demands a final audit report and ADR links, ensuring the deployment is documented according to our highest SDD
  standards.

## Response snapshot

Generated a comprehensive feature specification (`specs/004-backend-deployment/spec.md`) and a quality checklist (`specs/004-backend-deployment/checklists/requirements.md`) for the backend production deployment. The spec defines user stories for secure infrastructure, automated live verification, and architectural transparency, along with functional requirements and measurable success criteria.

## Outcome

- ✅ Impact: Established a clear roadmap for production deployment and automated verification.
- 🧪 Tests: No active tests run during specification.
- 📁 Files: Created spec.md and requirements checklist.
- 🔁 Next prompts: /sp.plan
- 🧠 Reflection: The prompt successfully integrated agent context and specialized skills into the SDD workflow.

## Evaluation notes (flywheel)

- Failure modes observed: Initial directory naming used 005 instead of 004; corrected on user feedback.
- Graders run and results (PASS/FAIL): PASS (Spec quality checklist completed).
- Prompt variant (if applicable): Polished deployment lifecycle version.
- Next experiment (smallest change to try): Add specific test runner details to the next prompt.
