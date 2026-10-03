# Course roadmap

## Relationship to the reference course

Source: [RF Wireless FPGA Design — NYCU EECM30152](https://rf-wireless-fpga-design.github.io/). The reference syllabus has RFSoC design in weeks 1–5, 5G applications in weeks 6–7, communications AI chips in weeks 8–10, proposals in weeks 11–12 and final projects in weeks 13–16. This is a proposed companion sequence, not an official syllabus change.

| Reference weeks | Rubik Pi companion | Student evidence |
| --- | --- | --- |
| 1 | Board readiness, Linux workflow and Wi-Fi access | Board/image inventory and redacted connectivity checklist |
| 2–3 | Host/board numerical OFDM transmitter exploration | Labeled constellation/spectrum and parameter prediction |
| 4–5 | Simulated channel, receiver synchronization and equalization | BER/EVM comparison with assumptions and fixed seed |
| 6 | Wi-Fi vs cellular; network measurement | Latency/loss/throughput report with topology |
| 7 | 5G stack, O-RAN roles and telemetry interfaces | Architecture diagram and labeled trace walk-through |
| 8 | Dataset preparation and CPU ML baseline | Split manifest, leakage check, held-out metrics |
| 9 | Model export and board CPU inference | Output parity check and timed inference log |
| 10 | Optional accelerator qualification and system profiling | Supported-runtime evidence or documented CPU fallback |
| 11–12 | Capstone problem and feasibility proposal | Architecture, bill of materials, risks and acceptance tests |
| 13–14 | Integration and controlled failures | Reproducible demo and recovery evidence |
| 15–16 | Benchmark, peer reproduction and final demo | Results, limitations and reproducibility package |

## Immersive lab pattern

Every lab is a mission: predict → build → observe → break safely → recover → explain. Plan for a 60–90 minute core session and an optional extension; adapt after piloting with students.

- Begin with a concrete system problem, not a list of commands.
- Ask students to predict a measurable result before running the experiment.
- Include an observable checkpoint early, then a parameter sweep or comparison.
- Use isolated test profiles, simulation or temporary files for failure exercises; never disrupt a shared campus network.
- Provide a recovery path and a brief reflection tied to evidence.
- Offer host-only/replay alternatives when boards are unavailable, explicitly labeled as such.

## Prerequisites and equipment

Expected background: wireless/digital communications and computer networks, matching the reference course. Add a short CLI/Python bridge for beginners.

Required for board labs: Rubik Pi 3, vendor-approved power/accessories, supported OS image, development host, authorized network and recovery access. Record exact revisions rather than guessing an image, port, cable or serial setting. Optional RFSoC/SDR/camera equipment must be separately qualified; RF transmission is not part of the default pathway.

## Proposed assessment

| Component | Weight | Evidence |
| --- | --- | --- |
| Lab checkpoints | 40% | Commands, observations, predictions and explanations |
| Troubleshooting and recovery | 20% | Diagnosis tied to evidence and safe recovery |
| Capstone | 30% | Working system, acceptance tests and comparison to baseline |
| Reproducibility and peer review | 10% | Clean setup, source attribution and limitations |

## Completion gates

Each published lab needs prerequisites, exact commands, expected output shapes (not invented measurements), failure/recovery instructions, a rubric, and a validation record identifying hardware, OS, software versions and date. CPU inference is the default. Accelerator labs remain optional until supported by a tested runtime/model/image combination.
