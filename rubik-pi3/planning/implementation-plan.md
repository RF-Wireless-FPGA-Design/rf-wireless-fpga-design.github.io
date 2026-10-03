# Rubik Pi 3 Companion Course Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Turn the category scaffold and existing Wi-Fi notes into a reproducible, mission-based wireless/edge-AI course aligned with EECM30152.

**Architecture:** Markdown-first category indexes link to self-contained labs and evidence requirements. Rubik Pi provides Linux and edge inference; RFSoC-specific hardware workflows remain in the reference course. No website framework or deployment is required for this phase.

**Tech Stack:** Markdown, Linux CLI, NetworkManager where present, Python and a board-compatible CPU inference runtime chosen after discovery; optional qualified acceleration.

---

## Current deliverable

Completed: category structure, navigation, curriculum mapping, reusable lab template and lossless Wi-Fi migration. Not completed: authored/board-tested labs, an interactive website, or runtime qualification. This course now lives under `rubik-pi3/` in the organization's existing `rf-wireless-fpga-design.github.io` repository. Paths in the tasks below are relative to `rubik-pi3/`.

## Task 1: Capture the supported board baseline

**Objective:** Remove hardware and OS assumptions before writing commands.

**Files:** Create `getting-started/board-readiness.md` and `getting-started/validation-record.md`; update `getting-started/README.md`.

1. Copy `templates/lab-template.md` to the lesson path and set status to draft.
2. Record board revision, official image source, OS release, architecture, power/access method and available storage.
3. On the board, capture `cat /etc/os-release`, `uname -m`, `ip -br link` and `command -v nmcli`; redact identifiers as needed.
4. Document a vendor-supported recovery procedure and demonstrate access independently of Wi-Fi.
5. Verify the lesson on the recorded image, then link it from the category index.

**Acceptance:** Another student identifies the board/image and accesses a recovery channel without guessing settings. Never mark validated from development-host output.

## Task 2: Turn Wi-Fi notes into a safe lesson

**Objective:** Preserve the reference while producing a tested classroom procedure.

**Files:** Create `network/wireless-connection/connect-and-verify.md` and `network/wireless-connection/validation-record.md`; update `network/wireless-connection/README.md`.

1. Use `review-notes.md` as the correction checklist; leave the migrated source unchanged unless a separate editorial revision is approved.
2. Author a personal-network workflow using discovered interfaces and interactive password entry.
3. Add separate link, address, route, DNS and HTTPS checks and output interpretation.
4. Add an institution-approved enterprise branch only after obtaining CA/server-domain/EAP requirements.
5. Test reconnect and controlled reboot with recovery access; record failures and fixes.

**Acceptance:** No credential literals or insecure certificate bypass; reproducible personal-network connection. Enterprise branch remains explicitly unvalidated if credentials/settings are unavailable.

## Task 3: Build the network measurement mission

**Files:** Create `network/network-diagnostics/measure-a-link.md`; update its category index.

1. Define an authorized local client/server topology and a baseline hypothesis.
2. Record tool versions and commands for repeated latency/loss/throughput measurements.
3. Add a safe simulated or isolated DNS-failure exercise, with rollback.
4. Have a peer reproduce the measurements and interpret variability.

**Acceptance:** Report distinguishes throughput from PHY link rate, records units and test conditions, and restores access after the exercise.

## Task 4: Author the wireless-to-AI bridge

**Files:** Create `wireless-communications/ofdm-simulation.md` and `ai-and-machine-learning/wireless-ml-baseline.md`; update both category indexes.

1. Define the OFDM model, channel assumptions, units and fixed seed before coding.
2. Specify tests for noiseless round-trip recovery and metric calculations; run them failing before implementing any simulation code.
3. Implement the smallest simulation that passes; record a parameter sweep as simulation, not RF capture.
4. Define train/validation/test separation by capture or scenario to prevent leakage.
5. Compare a simple baseline to the ML model on untouched held-out data.

**Acceptance:** Reproducible outputs, explicit dataset provenance, no train/test contamination, and no claim of RFSoC or over-the-air execution.

## Task 5: Qualify edge deployment

**Files:** Create `edge-ai-deployment/cpu-inference.md` and `edge-ai-deployment/runtime-compatibility.md`; update its category index.

1. Verify a supported runtime against the recorded board/image and cite official installation guidance.
2. Define output-parity tests before adding export/inference code.
3. Run CPU inference and compare predictions with the original model.
4. Record warm-up, sample count, latency distribution, memory and model size.
5. Add an accelerator branch only after successful runtime/model compatibility tests; otherwise document the CPU-only path.

**Acceptance:** Real board measurements and a runnable fallback. Unsupported acceleration is a limitation, not a simulated success.

## Task 6: Integrate architecture and capstone

**Files:** Create `five-g-and-oran/telemetry-walkthrough.md`, `capstone-projects/proposal-template.md` and `capstone-projects/demo-checklist.md`; update their indexes.

1. Draw data/control flows and mark mock, replay and real interfaces distinctly.
2. Define a narrowly scoped proposal and measurable success criteria before implementation.
3. Add a baseline comparison and one controlled failure/recovery test.
4. Run a peer demonstration from clean instructions and record remaining limitations.

**Acceptance:** End-to-end demonstration with genuine provenance; no claim of live E2/A1 compliance from a mock service.

## Task 7: Release review and optional site integration

**Files:** Update `README.md` and `planning/course-roadmap.md`; add validation records beside completed lessons.

1. Check every relative Markdown link resolves and every planned lesson is honestly labeled.
2. Audit new paths for lowercase kebab-case, with `README.md` as the navigation exception.
3. Review commands for secret exposure, networking disruption and hardware assumptions.
4. Pilot a lesson, log actual duration and revise the proposed timing/rubric.
5. Only if requested, integrate with the existing course site's build/navigation; do not create a separate nested Pages site by default.

**Acceptance:** Valid navigation, no secrets, versioned board evidence for released labs, and a clear draft/validated distinction. Future website UI integration remains a separately scoped action; the Markdown course lives in the existing repository.
