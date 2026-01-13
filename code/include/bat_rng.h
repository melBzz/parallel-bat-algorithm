#ifndef BAT_RNG_H
#define BAT_RNG_H

#include <stdint.h>

/*
 * Small deterministic RNG utilities.
 *
 * Why this exists:
 * - The original code used C's rand(), which is shared global state.
 * - In OpenMP, calling rand() from multiple threads is undefined behavior and
 *   makes both correctness and benchmarking unreliable.
 * - By storing an RNG state per bat, each bat generates its own random numbers
 *   deterministically, independent of thread/process scheduling.
 */

/* Initialize a per-bat RNG state from a global seed + an index (e.g., bat id). */
uint32_t bat_rng_init(uint32_t seed, uint32_t stream_id);

/* Uniform random in (0,1) (never returns exactly 0 or 1). */
double bat_rng_uniform01(uint32_t *state);

/* Uniform random in [a,b]. */
double bat_rng_uniform(uint32_t *state, double a, double b);

/* Gaussian random using Box-Muller. */
double bat_rng_normal(uint32_t *state, double mean, double stddev);

#endif
