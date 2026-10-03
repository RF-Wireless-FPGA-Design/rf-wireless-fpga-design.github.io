# Rubik Pi 3 — Wireless and Edge-AI Lab Course

A hands-on companion to [NYCU RF Wireless FPGA Design — EECM30152](https://rf-wireless-fpga-design.github.io/), not a replacement for its RFSoC/Vivado/Vitis labs.

## Start here

1. Read the [course roadmap](planning/course-roadmap.md) and [development plan](planning/implementation-plan.md).
2. Complete the planned [board-readiness checkpoint](getting-started/README.md).
3. Use the existing [Wi-Fi guide](network/wireless-connection/wifi-setup.md), after reading its [review notes](network/wireless-connection/review-notes.md).
4. Follow the pathway below; submit evidence at every checkpoint.

## Learning pathway

| Order | Category | Outcome | Status |
| --- | --- | --- | --- |
| 1 | [Getting started](getting-started/README.md) | Identify board/image, establish recovery access | Planned |
| 2 | [Linux and development](linux-and-development/README.md) | Reproducible CLI/Python workflow | Planned |
| 3 | [Network](network/README.md) | Connect, measure and troubleshoot a link | Existing Wi-Fi guide; other labs planned |
| 4 | [Wireless communications](wireless-communications/README.md) | Relate OFDM concepts to measured/simulated data | Planned |
| 5 | [AI and machine learning](ai-and-machine-learning/README.md) | Train a baseline and evaluate it on held-out data | Planned |
| 6 | [Edge AI deployment](edge-ai-deployment/README.md) | Benchmark CPU inference; optionally qualify acceleration | Planned |
| 7 | [5G and O-RAN](five-g-and-oran/README.md) | Explain architecture and prototype a telemetry application | Planned |
| 8 | [Capstone projects](capstone-projects/README.md) | Demonstrate an evidence-backed end-to-end system | Planned |

## Scope and conventions

- Rubik Pi 3 is the Linux/edge-compute companion in this course. Do not imply that it executes FPGA bitstreams, replaces RFSoC converters, or provides a cellular base station by itself.
- New directories and lesson filenames use lowercase `kebab-case`, with no spaces. `README.md` is the conventional navigation-file exception. The existing parent directory is unchanged to avoid breaking external paths.
- Each category has its own backlog. Create lesson files only when authored; planned filenames are not claims of completed labs.
- Use the [lab template](templates/lab-template.md) for missions, predictions, measurements, failure recovery and reflections.
- Tag results as board-measured, host-measured, simulated, or replayed. Never describe generated traces as measurements.
- Hardware/image, peripheral compatibility and accelerator support must be checked on the actual board. No board validation has been performed by this scaffold.

## Existing material migration

`wifi_wireless_network_installation_on_the_rubik_pi_3.md` → `network/wireless-connection/wifi-setup.md`.

The original guide is preserved without content edits. Read its companion review notes before using it as a classroom procedure.
