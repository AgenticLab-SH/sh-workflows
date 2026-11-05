# 해커톤 시작 Skill

43개 중 먼저 safe-workroom-bootstrap으로 범위/최초 기록을 확인하고 hackathon-task-driver를 읽고, 현재 과제에 필요한 아래 Skill 1~2개만 추가로 선택합니다. 기존 35개 Skill은 보존했습니다.

| Skill | 용도 |
| --- | --- |
| [safe-workroom-bootstrap](../.agents/skills/safe-workroom-bootstrap/SKILL.md) | VS Code 과제 루트 확인 → Clone 전 원본 기록 → 단일 격리 폴더 → 보고 3000/실서비스 3001 |
| [hackathon-task-driver](../.agents/skills/hackathon-task-driver/SKILL.md) | 제공 IDE에서 요구 파악·최소 구현·허용된 증거·제출 준비를 연결 |
| [reference-submission-review](../.agents/skills/reference-submission-review/SKILL.md) | 공개 참고 키트와 필수 제출 파일의 경계·미리보기 확인 |
| [stakeholder-agent-questioning](../.agents/skills/stakeholder-agent-questioning/SKILL.md) | 구체 질문에만 답하는 담당자에게 애매·경계·예외를 한 사실짜리 질문으로 묻고 복사용 멘트·원장 관리 |
| [role-separated-design](../.agents/skills/role-separated-design/SKILL.md) | 이용자/운영자 등 역할별 화면·데이터·권한·흐름 분리 |
| [optimization-modeling](../.agents/skills/optimization-modeling/SKILL.md) | 데이터 정제→정식화→기준선→개선→소규모 정확해 비교 |
| [explainable-workbench](../.agents/skills/explainable-workbench/SKILL.md) | 여러 Codex의 누적 작업 보고, 설계 대안·의사결정·검증 근거와 로컬 두 탭 대시보드 |
| [cost-aware-execution](../.agents/skills/cost-aware-execution/SKILL.md) | 필수 검증을 지키면서 토큰·호출·재시도 비용을 줄이고 기록 |

오버라이드 지침(작업 방식 고정)은 Skill이 아니라 [운영서](OVERRIDE_INSTRUCTIONS.md)와 템플릿으로 제공합니다.

# Skills index

Select one or two relevant skills; current host rules take priority.

| Skill | Purpose |
| --- | --- |
| accessibility-ux-review | Audit a small product UI for a clear user journey, labels, keyboard navigation, feedback, contrast, and error states. |
| agent-orchestration | Plan bounded multi-agent collaboration with one write owner and independent read-only reviews; use only when the runtime and policy explicitly enable subagents. |
| arithmetic-sanity-check | Recompute quantities, percentages, boundary conditions, and units from supplied facts; use when numeric correctness matters. |
| backend-api | Design small backend services and APIs with clear request schemas, validation, errors, and reproducible smoke tests. |
| bilingual-localization | Translate and localize Korean-English product copy, instructions, UI strings, and technical writing while preserving facts, constraints, and terminology. |
| business-correspondence | Write customer support replies, incident updates, status requests, and escalation messages with evidence, empathy, ownership, and precise next steps. |
| chart-and-report-design | Create evidence-backed data tables, charts, and short reports from validated numeric sources, clearly labeling units and uncertainty. |
| codex-build-loop | Direct a coding agent through inspect-plan-implement-run-test-fix-verify loops; use for unfamiliar repositories and AI-assisted engineering. |
| cost-aware-execution | Keep token, call, retry and run-time cost low during agent-assisted work without cutting required checks; use when cost may be evaluated even if usage is unlimited. |
| data-analysis | Analyze small datasets with grounded aggregations and reproducible reasoning; use for business metrics, comparisons, descriptive statistics, and decision support. |
| data-profiling | Profile CSV and JSON data for schema, duplicates, missingness, type errors, and unit consistency before analytics or automation. |
| explainable-workbench | Maintain a local append-only explanation and evidence history across agent workers, with a read-only reports/results viewer. |
| debugging-verification | Reproduce and fix code, data, or workflow failures with minimal patches and regression testing; use when outputs conflict with requirements. |
| decision-analysis | Compare technical or business options with a transparent decision matrix, explicit tradeoffs, and measurable acceptance criteria. |
| document-rule-reconciliation | Compare multiple versions of rules or documents and detect precedence conflicts; use for application review, policy comparison, and consistency checks. |
| documentation-handoff | Create concise README files, setup guides, release notes, and engineering handoffs grounded in observed behavior and known limits. |
| english-speaking | Coach English speaking for brief technical explanations, interviews, and presentations with short utterances, vocabulary scaffolding, and timed practice. |
| english-writing | Draft and revise English professional emails, reports, project updates, and short explanations for non-native speakers with accurate nuance and natural tone. |
| frontend-mvp | Build responsive accessible frontend MVPs for a narrowly specified workflow; use when an interactive web UI is truly required. |
| goal-driven-iteration | Use explicit goals, acceptance checks, constraints, and stop conditions during iterative engineering; use with or without a supported goal command. |
| korean-speaking | Coach structured Korean spoken responses, presentations, briefings, and explanations with timed scripts and follow-up questions. |
| korean-writing | Draft and edit clear Korean professional writing, proposals, explanations, reports, and emails for specified readers, preserving factual meaning and tone. |
| manual-preview-validation | Verify a web application developed in a restricted or browser-hosted IDE when the coding agent cannot inspect or control the preview window. Use for server startup, port and bind troubleshooting, HTTP smoke checks, and candidate-operated visual acceptance tests. |
| optimization-modeling | Turn messy tabular data into a stated optimization problem, compare algorithm candidates from a simple baseline to small exact checks, and verify constraints and objective values. |
| project-time-budget | Plan and manage time-boxed engineering work with explicit checkpoints and submission buffer without assuming an official scoring model. |
| prompt-engineering | Design and improve precise AI prompts for unfamiliar tasks; use for goal clarification, constrained outputs, iteration, and verifiable prompts. |
| requirements-discovery | Turn ambiguous stakeholder requests into scoped, testable requirements; use before implementation when success criteria or business rules are unclear. |
| reference-submission-review | Identify reference toolkit and synthetic files separately from required task artifacts before submission. |
| research-evidence | Research unfamiliar domains and compare evidence quality; use for source synthesis, fact checking, uncertainty tracking, and reference-grounded notes. |
| role-separated-design | Design, build and verify separate screens, data views, permissions and state flows when a task has two or more user roles. |
| safe-workroom-bootstrap | Confirm a strict project root before Clone, preserve initial metadata in one local folder and run a 3000 report UI next to an independent 3001 task service. |
| saved-file-reconciliation | Diagnose disagreement between a browser editor, terminal, and coding agent after files are edited or saved. Use when a file does not appear, an external-change warning appears, an unsaved buffer is suspected, or an agent's edit seems missing. |
| security-privacy-review | Review software and documents for data exposure, permission errors, insecure defaults, prompt injection, and accidental outbound transfers. |
| short-answer-defense | Practice evidence-based short written defenses of an AI-assisted deliverable under timed, no-AI conditions; use for architecture and verification Q&A. |
| stakeholder-agent-questioning | Turn every ambiguity, edge case and document-data gap into specific single-fact questions for a stakeholder who answers only concrete questions. |
| stakeholder-interview | Interview a simulated or real business stakeholder to clarify goals, competing priorities, constraints, and success metrics without leading questions. |
| structured-extraction | Extract fields, tables, rules, entities, and deadlines from provided unstructured documents without inventing missing information. |
| system-design-explanation | Explain an implemented architecture, data flow, tradeoffs, risks, and dependencies to technical and nontechnical audiences. |
| test-design | Design normal, boundary, negative, security, and regression tests from explicit acceptance criteria for software or data workflows. |
| web-ide-terminal-bridge | Inspect a browser-hosted development workspace from an authorized terminal when a coding agent cannot see the editor UI. Use for web IDEs, terminal-only agents, unclear project roots, file discovery, and read-only environment verification before making changes. |
| work-breakdown | Decompose a complex task into dependency-aware deliverables and small checkpoints; use for time-boxed projects, parallel planning, and scope reduction. |
| workflow-automation | Automate repeatable file and data workflows with bounded local scripts and explicit approvals, without browser/computer-use automation. |
