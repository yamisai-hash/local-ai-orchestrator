# Local AI Orchestrator

![status](https://img.shields.io/badge/status-active-brightgreen) ![infra](https://img.shields.io/badge/infra-%240%20local-green) ![platform](https://img.shields.io/badge/platform-Windows%20%2B%20Python-blue) ![self--healing](https://img.shields.io/badge/self--healing-yes-success)

> The platform layer beneath everything else: a **$0-cost, local-first** automation engine that runs independent "lanes" on a schedule (content / video factory / futures), persists to append-only JSON state, and **self-heals** — all on a single machine.

> ℹ️ Single-operator, single-machine. **Cleaned, representative subset** of a larger private system.

![Video factory output](assets/video_factory_output.png)

## Why this exists

The content and trading systems don't run themselves — this runs them. The goal
was **zero ongoing cost**: local LLM (Ollama), local TTS, FFmpeg rendering, and a
plain scheduler, so it can run indefinitely on one machine.

## How it works

```
scheduler (windows/cooldowns/priority) → lanes (content | video factory | futures)
        → append-only JSON state → health_monitor (heartbeat / silent-failure / code-drift)
        → alerts + restart_required back to the scheduler
```

See [`docs/architecture.md`](docs/architecture.md) · [`docs/self_healing.md`](docs/self_healing.md).

## Repository layout

```
src/            scheduler · lane · health_monitor · state_store
docs/           architecture · self_healing
configs/        lanes.example.yaml
observability/  sample_ecosystem_health.json
demo_data/      sample_state.json
examples/       run_scheduler_once.py
assets/         video-factory output + architecture diagram
```

## Quickstart

```bash
pip install -r requirements.txt
python examples/run_scheduler_once.py   # prints which lanes would run this cycle
```

## The interesting part: self-healing

A load-once loop that's edited while running will silently run stale code.
`health_monitor.detect_code_drift` compares each source file's mtime to the loop
start and raises `restart_required` — a check that caught exactly this in
practice (see [`docs/self_healing.md`](docs/self_healing.md)).

## Tech

Python · PyYAML · Ollama (local LLM) · FFmpeg / OpenCV · Windows Task Scheduler · $0 paid infrastructure.

## License

MIT — see [LICENSE](LICENSE).
