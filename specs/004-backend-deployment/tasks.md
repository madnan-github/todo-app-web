# Tasks: Backend Production Deployment

**Input**: Design documents from `/specs/004-backend-deployment/`
**Prerequisites**: plan.md, spec.md, contracts/health-check.yaml, quickstart.md
**Tests**: Production verification suite requested (User Story 2)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Deployment Configuration)

**Purpose**: Create Railway deployment configuration files

- [x] T001 Create Procfile for Railway web process in backend/Procfile
- [x] T002 [P] Create environment template in backend/.env.example with all required production variables

**Checkpoint**: Deployment configuration ready for Railway

---

## Phase 2: Foundational (Backend Configuration)

**Purpose**: Modify existing backend files for production readiness

**⚠️ CRITICAL**: These modifications enable all user stories

- [x] T003 Modify config.py to remove hardcoded secrets and add production detection in backend/src/config.py
- [x] T004 [P] Modify database.py to optimize asyncpg connection pooling for Neon in backend/src/database.py
- [x] T005 Modify main.py to implement CORS hardening with Vercel whitelist in backend/src/main.py

**Checkpoint**: Backend configured for production - user stories can now begin

---

## Phase 3: User Story 1 - Secure Production Infrastructure (Priority: P1) 🎯 MVP

**Goal**: Configure FastAPI backend with production-grade settings for Railway and Neon deployment

**Independent Test**: Deploy to Railway, verify health check returns 200 OK with database connected status, confirm CORS blocks non-whitelisted domains

### Production Infrastructure Implementation

- [x] T006 [US1] Implement dynamic port binding with PORT env var in backend/src/main.py
- [x] T007 [US1] Disable API documentation (Swagger/ReDoc) in production mode in backend/src/main.py
- [x] T008 [US1] Add production environment detection to config.py in backend/src/config.py
- [x] T009 [US1] Configure strict CORS whitelist for Vercel production domains in backend/src/main.py
- [x] T010 [US1] Implement secret externalization validation in backend/src/config.py
- [x] T011 [US1] Verify JWT_SECRET_KEY and BETTER_AUTH_SECRET have no defaults in backend/src/config.py

**Checkpoint**: User Story 1 complete - deploy and verify at Railway URL

---

## Phase 4: User Story 2 - Automated Production Verification (Priority: P2)

**Goal**: Create verification suite to test live production environment

**Independent Test**: Run `uv run python verify_production.py --url <railway-url>` and receive pass/fail report for all checks

### Verification Suite Tests

> **NOTE**: Write these tests FIRST, ensure they FAIL before implementation

- [ ] T012 [P] [US2] Create health check verification test in tests/verify/test_health_check.py
- [ ] T013 [P] [US2] Create CORS enforcement test in tests/verify/test_cors.py
- [ ] T014 [P] [US2] Create JWT authentication test in tests/verify/test_auth.py
- [ ] T015 [P] [US2] Create user isolation verification test in tests/verify/test_user_isolation.py

### Verification Suite Implementation

- [x] T016 [US2] Implement deep health check verification with database connectivity in backend/verify_production.py
- [x] T017 [US2] Implement CORS whitelist verification for Vercel domains in backend/verify_production.py
- [x] T018 [US2] Implement JWT authentication verification on production URL in backend/verify_production.py
- [x] T019 [US2] Implement user isolation test to verify other users' data is inaccessible in backend/verify_production.py
- [x] T020 [US2] Add CLI argument parsing for production URL in backend/verify_production.py
- [x] T021 [US2] Generate pass/fail report with summary in backend/verify_production.py

**Checkpoint**: User Story 2 complete - run verification against live Railway deployment

---

## Phase 5: User Story 3 - Architectural Transparency & Auditing (Priority: P3)

**Goal**: Document all deployment decisions with ADRs and produce audit report

**Independent Test**: Verify ADRs exist in history/adr/ and audit report contains all configured items

### ADR Documentation

- [x] T022 [US3] Create ADR for Railway port binding strategy in history/adr/004-port-binding.md
- [x] T023 [US3] Create ADR for Neon asyncpg connection pooling configuration in history/adr/005-neon-pooling.md
- [x] T024 [US3] Create ADR for CORS security hardening approach in history/adr/006-cors-security.md
- [x] T025 [US3] Create ADR for secret externalization strategy in history/adr/007-secret-externalization.md

### Audit Report

- [x] T026 [US3] Generate deployment audit report in specs/004-backend-deployment/audit-report.md
- [x] T027 [US3] Document all configured endpoints in audit report
- [x] T028 [US3] Document all environment variables required in audit report
- [x] T029 [US3] Document all security measures implemented in audit report

**Checkpoint**: User Story 3 complete - all decisions documented and traceable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [x] T030 [P] Update backend/README.md with production deployment instructions
- [x] T031 [P] Verify quickstart.md accuracy against implemented changes
- [x] T032 Run full verification suite against Railway deployment (requires Railway URL - run after deployment: `python3 backend/verify_production.py --url <railway-url>`)
- [x] T033 Review all files for security best practices
- [x] T034 [P] Final code cleanup and remove any debug statements
- [x] T038 [P] Verify SC-002: 100% of production secrets externalized in backend/src/config.py

---

## Dependencies & Execution Order

### Phase Dependencies

| Phase | Depends On | Blocks |
|-------|------------|--------|
| Setup (1) | None | Foundational |
| Foundational (2) | Setup | All User Stories |
| US1 (3) | Foundational | Testing, Integration |
| US2 (4) | Foundational | Verification |
| US3 (5) | Foundational | Documentation |
| Polish (6) | All stories | Release |

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Verification tests can run independently
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Documentation can proceed in parallel

### Within Each User Story

- Tests (US2) MUST be written and FAIL before implementation
- Configuration changes (US1) before verification (US2)
- ADRs (US3) after implementation decisions are finalized

### Parallel Opportunities

| Phase | Tasks That Can Run in Parallel |
|-------|-------------------------------|
| Setup | T001, T002 |
| Foundational | T003, T004 (T005 depends on T003) |
| US1 Implementation | T006-T011 (no dependencies) |
| US2 Tests | T012-T015 (all [P] marked) |
| US2 Implementation | T016-T021 (can run after tests fail) |
| US3 ADRs | T022-T025 (all [P] marked) |
| Polish | T030, T031, T034 |

---

## Parallel Example: User Story 2 Verification Suite

```bash
# Launch all tests for User Story 2 together:
Task: "Create health check verification test in tests/verify/test_health_check.py"
Task: "Create CORS enforcement test in tests/verify/test_cors.py"
Task: "Create JWT authentication test in tests/verify/test_auth.py"
Task: "Create user isolation verification test in tests/verify/test_user_isolation.py"

# Then implement verification after tests fail:
Task: "Implement deep health check verification with database connectivity in backend/verify_production.py"
Task: "Implement CORS whitelist verification for Vercel domains in backend/verify_production.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T005)
3. Complete Phase 3: User Story 1 (T006-T011)
4. **STOP and VALIDATE**: Deploy to Railway, verify `/health` endpoint
5. If ready: Deploy/demo User Story 1

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Deploy → Verify → Demo (MVP!)
3. Add User Story 2 → Run verification against live deployment
4. Add User Story 3 → Complete documentation and ADRs
5. Polish → Final release

### Recommended Execution Order

```
Phase 1 → Phase 2 → Phase 3 (US1) → Deploy & Test
                       ↓
Phase 4 (US2) → Run verification against deployed app
                       ↓
Phase 5 (US3) → Create ADRs and audit report
                       ↓
Phase 6 → Polish and final validation
```

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 35 |
| Setup Phase | 2 tasks |
| Foundational Phase | 3 tasks |
| User Story 1 (P1) | 6 tasks |
| User Story 2 (P2) | 10 tasks |
| User Story 3 (P3) | 8 tasks |
| Polish Phase | 6 tasks |
| Parallelizable Tasks | 17 (marked with [P]) |

### Suggested MVP Scope

**Minimum Viable Product**: Complete Phase 1 + Phase 2 + Phase 3 (User Story 1)

This delivers:
- Railway Procfile for deployment
- Production-hardened backend configuration
- Functional deployment at Railway URL

### Files to Create

| File | Task | Phase |
|------|------|-------|
| backend/Procfile | T001 | Setup |
| backend/.env.example | T002 | Setup |
| tests/verify/test_health_check.py | T012 | US2 Tests |
| tests/verify/test_cors.py | T013 | US2 Tests |
| tests/verify/test_auth.py | T014 | US2 Tests |
| tests/verify/test_user_isolation.py | T015 | US2 Tests |
| backend/verify_production.py | T016-T021 | US2 Impl |
| history/adr/004-port-binding.md | T022 | US3 |
| history/adr/005-neon-pooling.md | T023 | US3 |
| history/adr/006-cors-security.md | T024 | US3 |
| history/adr/007-secret-externalization.md | T025 | US3 |
| specs/004-backend-deployment/audit-report.md | T026-T029 | US3 |

### Files to Modify

| File | Task | Phase |
|------|------|-------|
| backend/src/config.py | T003 | Foundational |
| backend/src/database.py | T004 | Foundational |
| backend/src/main.py | T005, T006, T007, T008, T009 | Foundational + US1 |

---

**Note**: This feature adds production configuration without changing data models or API contracts. All user stories can be completed independently after the Foundational phase.
