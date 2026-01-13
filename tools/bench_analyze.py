#!/usr/bin/env python3
"""Parse BENCH lines and compute speedup/efficiency + plots.

Usage:
  python3 tools/bench_analyze.py --input code/bench_results.txt --outdir bench_out

The program expects lines like:
  BENCH version=openmp n_bats=2000 iters=2000 procs=1 threads=4 time_s=3.890662

Key ideas / conventions used by this script:

- `p` (parallelism level):
    - OpenMP: `p = threads`
    - MPI: `p = procs`
    - sequential: `p = 1`

- Strong scaling (fixed problem size):
    - Problem size is (n_bats, iters)
    - Baseline time is sequential time T1 for the *same* (n_bats, iters)
    - Speedup: S(p) = T1 / Tp
    - Efficiency: E(p) = S(p) / p

    In addition to the sequential baseline, we also compute a *self baseline*
    for each parallel version:
        T_self1 = Tp at p=1 for the same version (MPI with 1 rank, OpenMP with 1 thread)
    This avoids misleading results when sequential and parallel programs have
    different overheads.

- Weak scaling (problem size grows with p):
    - In our benchmarks we typically set n_bats = base_n_bats * p
    - Baseline time is the p=1 run at the smallest n_bats for that iters
    - Weak “efficiency” is usually defined as how close time stays constant,
        so we use:
            E_w(p) = T_base / Tp
        (no division by p)

Plotting notes:
- We generate *combined* comparison plots (sequential vs OpenMP vs MPI) to keep
    the number of figures small.
- We skip plots with only 1 point (they are not informative).
- Efficiency can be slightly > 1 vs the sequential baseline due to noise and
    because sequential vs MPI/OpenMP have different overheads. The self-baseline
    plots are usually the safest to discuss in the report.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from dataclasses import dataclass
from typing import Iterable, List, Dict, Tuple, Optional

BENCH_RE = re.compile(
    r"^BENCH\s+"
    r"version=(?P<version>\S+)\s+"
    r"n_bats=(?P<n_bats>\d+)\s+"
    r"iters=(?P<iters>\d+)\s+"
    r"procs=(?P<procs>\d+)\s+"
    r"threads=(?P<threads>\d+)\s+"
    r"time_s=(?P<time_s>[0-9.]+)\s*$"
)


@dataclass(frozen=True)
class BenchRow:
    version: str
    n_bats: int
    iters: int
    procs: int
    threads: int
    time_s: float

    @property
    def p(self) -> int:
        """Return the parallelism level p for this record."""
        if self.version == "openmp":
            return self.threads
        if self.version == "mpi":
            return self.procs
        return 1


def parse_lines(lines: Iterable[str]) -> List[BenchRow]:
    """Extract BENCH lines from a text stream.

    Any non-matching lines are ignored, so you can pass full stdout/stderr logs.
    """
    rows: List[BenchRow] = []
    for line in lines:
        line = line.strip()
        m = BENCH_RE.match(line)
        if not m:
            continue
        rows.append(
            BenchRow(
                version=m.group("version"),
                n_bats=int(m.group("n_bats")),
                iters=int(m.group("iters")),
                procs=int(m.group("procs")),
                threads=int(m.group("threads")),
                time_s=float(m.group("time_s")),
            )
        )
    return rows


def group_key(row: BenchRow) -> Tuple[str, int, int]:
    """Group key for strong scaling: version + (n_bats, iters)."""
    return (row.version, row.n_bats, row.iters)


def find_baseline(rows: List[BenchRow], n_bats: int, iters: int) -> float:
    """Strong-scaling baseline: sequential time with the same (n_bats, iters).

    If multiple runs exist, we use the minimum time as a simple noise-reduction
    strategy.
    """
    candidates = [r for r in rows if r.version == "sequential" and r.n_bats == n_bats and r.iters == iters]
    if not candidates:
        raise SystemExit(f"Missing sequential baseline for n_bats={n_bats} iters={iters}")
    # Choose min time if multiple repeats
    return min(r.time_s for r in candidates)


def find_self_baseline(rows: List[BenchRow], version: str, n_bats: int, iters: int) -> Optional[float]:
    """Self baseline for a version: Tp at p=1 for the same (n_bats, iters)."""
    candidates = [r for r in rows if r.version == version and r.n_bats == n_bats and r.iters == iters and r.p == 1]
    if not candidates:
        return None
    return min(r.time_s for r in candidates)


def _strong_metrics(rows: List[BenchRow]) -> List[Dict[str, object]]:
    """Strong scaling: fixed (n_bats, iters), baseline is sequential with same size."""
    out: List[Dict[str, object]] = []

    # Detect strong-scaling datasets.
    #
    # In weak scaling, n_bats changes with p, so you often get only one point per
    # (n_bats, iters). If we plotted those as strong scaling, we'd create lots of
    # useless single-point PNGs.
    strong_keys: set[Tuple[str, int, int]] = set()
    by_key: Dict[Tuple[str, int, int], set[int]] = {}
    for r in rows:
        if r.version == "sequential":
            continue
        k = (r.version, r.n_bats, r.iters)
        by_key.setdefault(k, set()).add(r.p)
    for k, ps in by_key.items():
        if len(ps) >= 2:
            strong_keys.add(k)

    sizes = sorted({(r.n_bats, r.iters) for r in rows})
    # Only keep sizes that actually have a sequential baseline
    baselines: Dict[Tuple[int, int], float] = {}
    for (n, it) in sizes:
        try:
            baselines[(n, it)] = find_baseline(rows, n, it)
        except SystemExit:
            continue

    for r in rows:
        if r.version != "sequential":
            k = (r.version, r.n_bats, r.iters)
            if k not in strong_keys:
                continue

        key = (r.n_bats, r.iters)
        if key not in baselines:
            continue

        t_seq1 = baselines[key]
        t_self1 = find_self_baseline(rows, r.version, r.n_bats, r.iters)
        if t_self1 is None:
            # If a version doesn't have p=1 data, we cannot compute self-baseline metrics.
            t_self1 = t_seq1

        p = r.p
        speedup_seq = t_seq1 / r.time_s if r.time_s > 0 else 0.0
        eff_seq = speedup_seq / p if p > 0 else 0.0
        speedup_self = t_self1 / r.time_s if r.time_s > 0 else 0.0
        eff_self = speedup_self / p if p > 0 else 0.0

        # Backward-compatible aliases: treat speedup/efficiency as self-baseline.
        speedup = speedup_self
        eff = eff_self
        out.append(
            {
                "mode": "strong",
                "version": r.version,
                "n_bats": r.n_bats,
                "iters": r.iters,
                "procs": r.procs,
                "threads": r.threads,
                "p": p,
                "time_s": r.time_s,
                "baseline_n_bats": r.n_bats,
                "T_base_s": t_seq1,
                "T_seq1_s": t_seq1,
                "T_self1_s": t_self1,
                "speedup": speedup,
                "efficiency": eff,
                "speedup_seq": speedup_seq,
                "efficiency_seq": eff_seq,
                "speedup_self": speedup_self,
                "efficiency_self": eff_self,
            }
        )
    return out


def _weak_baseline(rows: List[BenchRow], iters: int, version: str) -> Optional[BenchRow]:
    """Weak scaling baseline: prefer sequential p=1; fallback to same-version p=1."""
    # Prefer sequential baseline (p=1)
    seq = [r for r in rows if r.iters == iters and r.version == "sequential" and r.p == 1]
    if seq:
        # choose smallest problem size as baseline (usually base per worker)
        return min(seq, key=lambda r: r.n_bats)

    same = [r for r in rows if r.iters == iters and r.version == version and r.p == 1]
    if same:
        return min(same, key=lambda r: r.n_bats)

    return None


def _weak_metrics(rows: List[BenchRow]) -> List[Dict[str, object]]:
    """Weak scaling: n_bats grows with p; baseline is p=1 at smallest n_bats for that iters.

        We compute weak scaling “efficiency” (how close time stays constant) as:

            E_w(p) = T_base / T_p

        where T_base is the p=1 baseline time at the base problem size.
    """
    out: List[Dict[str, object]] = []

    iters_set = sorted({r.iters for r in rows})
    for iters in iters_set:
        for version in sorted({r.version for r in rows}):
            if version == "sequential":
                continue

            baseline_seq = _weak_baseline(rows, iters, version)
            baseline_self = _weak_baseline(rows, iters, version)
            # For self baseline, prefer p=1 run of the same version.
            same = [r for r in rows if r.iters == iters and r.version == version and r.p == 1]
            if same:
                baseline_self = min(same, key=lambda r: r.n_bats)

            baseline = baseline_seq
            if baseline is None:
                continue

            t_base_seq = baseline.time_s
            base_n = baseline.n_bats
            t_base_self = baseline_self.time_s if baseline_self is not None else t_base_seq

            candidates = [r for r in rows if r.iters == iters and r.version == version]
            for r in candidates:
                p = r.p
                weak_eff_seq = t_base_seq / r.time_s if r.time_s > 0 else 0.0
                weak_eff_self = t_base_self / r.time_s if r.time_s > 0 else 0.0

                # For weak scaling, we store the usual constant-time metric into both
                # speedup_* and efficiency_* for convenience.
                out.append(
                    {
                        "mode": "weak",
                        "version": r.version,
                        "n_bats": r.n_bats,
                        "iters": r.iters,
                        "procs": r.procs,
                        "threads": r.threads,
                        "p": p,
                        "time_s": r.time_s,
                        "baseline_n_bats": base_n,
                        "T_base_s": t_base_seq,
                        "T_seq1_s": t_base_seq,
                        "T_self1_s": t_base_self,
                        "speedup": weak_eff_self,
                        "efficiency": weak_eff_self,
                        "speedup_seq": weak_eff_seq,
                        "efficiency_seq": weak_eff_seq,
                        "speedup_self": weak_eff_self,
                        "efficiency_self": weak_eff_self,
                    }
                )

            # Also include the baseline row itself (useful for plotting)
            out.append(
                {
                    "mode": "weak",
                    "version": baseline.version,
                    "n_bats": baseline.n_bats,
                    "iters": baseline.iters,
                    "procs": baseline.procs,
                    "threads": baseline.threads,
                    "p": 1,
                    "time_s": baseline.time_s,
                    "baseline_n_bats": base_n,
                    "T_base_s": t_base_seq,
                    "T_seq1_s": t_base_seq,
                    "T_self1_s": t_base_self,
                    "speedup": 1.0,
                    "efficiency": 1.0,
                    "speedup_seq": 1.0,
                    "efficiency_seq": 1.0,
                    "speedup_self": 1.0,
                    "efficiency_self": 1.0,
                }
            )

    # Deduplicate identical dicts (baseline might be added multiple times)
    uniq: Dict[Tuple, Dict[str, object]] = {}
    for m in out:
        key = (
            m["mode"],
            m["version"],
            m["n_bats"],
            m["iters"],
            m["procs"],
            m["threads"],
        )
        uniq[key] = m
    return list(uniq.values())


def compute_metrics(rows: List[BenchRow]) -> List[Dict[str, object]]:
    """Compute both strong and weak scaling metrics (written to one CSV)."""
    strong = _strong_metrics(rows)
    weak = _weak_metrics(rows)
    return strong + weak


def try_plot(metrics: List[Dict[str, object]], outdir: str) -> None:
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except Exception:
        print("matplotlib not available; skipping plots. Install with: pip install matplotlib")
        return

    def _series(ms: List[Dict[str, object]], ykey: str) -> Tuple[List[int], List[float]]:
        ms = sorted(ms, key=lambda x: int(x["p"]))
        xs = [int(x["p"]) for x in ms]
        ys = [float(x[ykey]) for x in ms]
        return xs, ys

    def plot_compare_strong(n_bats: int, iters: int, ms: List[Dict[str, object]]) -> None:
        # Split by version
        seq = [m for m in ms if m["version"] == "sequential"]
        omp = [m for m in ms if m["version"] == "openmp"]
        mpi = [m for m in ms if m["version"] == "mpi"]

        # Need at least 2 points among parallel series to be meaningful
        if len({int(m["p"]) for m in omp + mpi}) < 2:
            return

        t_seq1 = float(seq[0]["T_seq1_s"]) if seq else float(ms[0].get("T_seq1_s", 0.0))
        title_tag = f"nbats{n_bats}_it{iters}"

        # Time
        plt.figure()
        if omp:
            x, y = _series(omp, "time_s")
            plt.plot(x, y, marker="o", label="OpenMP")
        if mpi:
            x, y = _series(mpi, "time_s")
            plt.plot(x, y, marker="o", label="MPI")
        if t_seq1 > 0:
            plt.axhline(t_seq1, linestyle="--", linewidth=1.0, label="Sequential (p=1)")
        plt.xlabel("p (threads or MPI processes)")
        plt.ylabel("Execution time (s)")
        plt.title(f"Strong scaling time: {title_tag}")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.savefig(os.path.join(outdir, f"compare_strong_time_{title_tag}.png"), dpi=150, bbox_inches="tight")
        plt.close()

        def _plot_speed_eff(ykey: str, ylabel: str, filename: str, ideal: str) -> None:
            plt.figure()
            if omp:
                x, y = _series(omp, ykey)
                plt.plot(x, y, marker="o", label="OpenMP")
            if mpi:
                x, y = _series(mpi, ykey)
                plt.plot(x, y, marker="o", label="MPI")
            # Ideal line (strong scaling)
            x_ideal = sorted({int(m["p"]) for m in omp + mpi})
            if x_ideal:
                if ideal == "p":
                    plt.plot(x_ideal, x_ideal, linestyle="--", label="ideal")
                elif ideal == "1":
                    plt.plot(x_ideal, [1.0 for _ in x_ideal], linestyle="--", label="ideal")
            plt.xlabel("p (threads or MPI processes)")
            plt.ylabel(ylabel)
            plt.title(f"Strong scaling {ylabel.lower()}: {title_tag}")
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.savefig(os.path.join(outdir, filename), dpi=150, bbox_inches="tight")
            plt.close()

        # vs sequential baseline
        _plot_speed_eff("speedup_seq", "Speedup (vs sequential)", f"compare_strong_speedup_vs_seq_{title_tag}.png", ideal="p")
        _plot_speed_eff("efficiency_seq", "Efficiency (vs sequential)", f"compare_strong_efficiency_vs_seq_{title_tag}.png", ideal="1")

        # vs self baseline
        _plot_speed_eff("speedup_self", "Speedup (vs self p=1)", f"compare_strong_speedup_vs_self_{title_tag}.png", ideal="p")
        _plot_speed_eff("efficiency_self", "Efficiency (vs self p=1)", f"compare_strong_efficiency_vs_self_{title_tag}.png", ideal="1")

    def plot_compare_weak(base_n: int, iters: int, ms: List[Dict[str, object]]) -> None:
        omp = [m for m in ms if m["version"] == "openmp"]
        mpi = [m for m in ms if m["version"] == "mpi"]

        if len({int(m["p"]) for m in omp + mpi}) < 2:
            return

        t_base_seq = float(ms[0].get("T_seq1_s", ms[0].get("T_base_s", 0.0)))
        title_tag = f"base{base_n}_it{iters}"

        # Time (ideal is constant time at baseline)
        plt.figure()
        if omp:
            x, y = _series(omp, "time_s")
            plt.plot(x, y, marker="o", label="OpenMP")
        if mpi:
            x, y = _series(mpi, "time_s")
            plt.plot(x, y, marker="o", label="MPI")
        if t_base_seq > 0:
            plt.axhline(t_base_seq, linestyle="--", linewidth=1.0, label="ideal (constant time)")
        plt.xlabel("p (threads or MPI processes)")
        plt.ylabel("Execution time (s)")
        plt.title(f"Weak scaling time: {title_tag} (n_bats = base * p)")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.savefig(os.path.join(outdir, f"compare_weak_time_{title_tag}.png"), dpi=150, bbox_inches="tight")
        plt.close()

        def _plot_eff(ykey: str, ylabel: str, filename: str) -> None:
            plt.figure()
            if omp:
                x, y = _series(omp, ykey)
                plt.plot(x, y, marker="o", label="OpenMP")
            if mpi:
                x, y = _series(mpi, ykey)
                plt.plot(x, y, marker="o", label="MPI")
            x_ideal = sorted({int(m["p"]) for m in omp + mpi})
            if x_ideal:
                plt.plot(x_ideal, [1.0 for _ in x_ideal], linestyle="--", label="ideal")
            plt.xlabel("p (threads or MPI processes)")
            plt.ylabel(ylabel)
            plt.title(f"Weak scaling efficiency: {title_tag}")
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.savefig(os.path.join(outdir, filename), dpi=150, bbox_inches="tight")
            plt.close()

        _plot_eff("efficiency_seq", "Weak efficiency (vs sequential p=1)", f"compare_weak_efficiency_vs_seq_{title_tag}.png")
        _plot_eff("efficiency_self", "Weak efficiency (vs self p=1)", f"compare_weak_efficiency_vs_self_{title_tag}.png")

    # Build comparison groups
    strong_groups: Dict[Tuple[int, int], List[Dict[str, object]]] = {}
    weak_groups: Dict[Tuple[int, int], List[Dict[str, object]]] = {}

    for m in metrics:
        mode = str(m.get("mode", "strong"))
        if mode == "strong":
            key = (int(m["n_bats"]), int(m["iters"]))
            strong_groups.setdefault(key, []).append(m)
        else:
            key = (int(m.get("baseline_n_bats", m["n_bats"])), int(m["iters"]))
            weak_groups.setdefault(key, []).append(m)

    for (n_bats, iters), ms in sorted(strong_groups.items()):
        plot_compare_strong(n_bats, iters, ms)

    for (base_n, iters), ms in sorted(weak_groups.items()):
        plot_compare_weak(base_n, iters, ms)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Input text file containing program output with BENCH lines")
    ap.add_argument("--outdir", default="bench_out", help="Output directory (CSV + PNG plots)")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    with open(args.input, "r", encoding="utf-8") as f:
        rows = parse_lines(f)

    if not rows:
        raise SystemExit("No BENCH lines found in input.")

    metrics = compute_metrics(rows)

    # Write CSV
    csv_path = os.path.join(args.outdir, "bench_metrics.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "mode",
                "version",
                "n_bats",
                "iters",
                "procs",
                "threads",
                "p",
                "time_s",
                "baseline_n_bats",
                "T_base_s",
                "T_seq1_s",
                "T_self1_s",
                "speedup",
                "efficiency",
                "speedup_seq",
                "efficiency_seq",
                "speedup_self",
                "efficiency_self",
            ],
        )
        w.writeheader()
        for m in metrics:
            w.writerow(m)

    print(f"Wrote {csv_path}")

    # Plots
    try_plot(metrics, args.outdir)


if __name__ == "__main__":
    main()
