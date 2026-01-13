#include <math.h>
#include <stdint.h>

#include "bat_rng.h"

/* SplitMix32 for seeding (good diffusion for nearby stream ids). */
static uint32_t splitmix32(uint32_t x) {
    x += 0x9E3779B9u;
    x = (x ^ (x >> 16)) * 0x85EBCA6Bu;
    x = (x ^ (x >> 13)) * 0xC2B2AE35u;
    return x ^ (x >> 16);
}

/* Xorshift32 core RNG (fast; state must be non-zero). */
static inline uint32_t xorshift32(uint32_t *state) {
    uint32_t x = *state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    *state = x;
    return x;
}

uint32_t bat_rng_init(uint32_t seed, uint32_t stream_id) {
    /* Mix seed and stream id, then ensure non-zero state. */
    uint32_t s = splitmix32(seed ^ (stream_id * 0xA511E9B3u));
    if (s == 0) {
        s = 0x6D2B79F5u;
    }
    return s;
}

double bat_rng_uniform01(uint32_t *state) {
    /* Return u in (0,1): avoids log(0) in Box-Muller and avoids 1.0. */
    uint32_t r = xorshift32(state);
    return ((double)r + 1.0) / ((double)UINT32_MAX + 2.0);
}

double bat_rng_uniform(uint32_t *state, double a, double b) {
    return a + (b - a) * bat_rng_uniform01(state);
}

double bat_rng_normal(uint32_t *state, double mean, double stddev) {
    /* Box-Muller using two independent uniforms in (0,1). */
    double u1 = bat_rng_uniform01(state);
    double u2 = bat_rng_uniform01(state);

    double z0 = sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
    return mean + stddev * z0;
}
