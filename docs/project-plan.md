# Project Plan

## Phase 0 — Repository Foundation

- [x] Create GitHub repository
- [x] Add README, license, ignore rules, and environment template
- [x] Add architecture and project plan
- [x] Add minimal Python dependencies

## Phase 1 — Reliability Core

- [ ] Define a small sample data source
- [ ] Define reliability checks
- [ ] Create a normalized reliability finding model
- [ ] Add unit tests
- [ ] Keep the first implementation runnable locally

## Phase 2 — AWS Foundation

- [ ] Select the minimum AWS services required for the first end-to-end flow
- [ ] Define IAM boundaries
- [ ] Add AWS configuration and clients
- [ ] Document the deployment path

## Phase 3 — First Agent

- [ ] Implement the reliability detection agent
- [ ] Introduce managed model inference where useful
- [ ] Add structured agent input/output
- [ ] Test failure and fallback behavior

## Phase 4 — Multi-Agent Investigation

- [ ] Add root-cause analysis agent
- [ ] Add recommendation/explanation agent
- [ ] Define orchestration and handoff contracts
- [ ] Preserve evidence across agent steps

## Phase 5 — Observability & Reliability

- [ ] Add structured logging
- [ ] Track agent execution and outcomes
- [ ] Add error handling and retries where appropriate
- [ ] Add evaluation cases for representative data failures

## Phase 6 — Portfolio Polish

- [ ] Add architecture diagram
- [ ] Add example end-to-end run
- [ ] Add deployment instructions
- [ ] Add screenshots or execution evidence
- [ ] Document trade-offs and lessons learned

## Scope Guardrails

This project should remain compact enough to explain in an interview. New AWS services or agents should be added only when they demonstrate a meaningful architectural capability.
