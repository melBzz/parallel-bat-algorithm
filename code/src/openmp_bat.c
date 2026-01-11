#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <omp.h>

#include "bat.h"
#include "bat_utils.h"

#define N_BATS     30
#define MAX_ITERS  10000

int main(void) {

    srand((unsigned int) time(NULL));

    Bat bats[N_BATS];
    Bat best_bat;

    initialize_bats(bats, &best_bat);

    for (int t = 0; t < MAX_ITERS; t++) {

        Bat iter_best;
        iter_best = best_bat;

        #pragma omp parallel
        {
            Bat thread_best = iter_best;

            #pragma omp for
            for (int i = 0; i < N_BATS; i++) {
                update_bat(bats, &iter_best, i, t);

                if (bats[i].f_value > thread_best.f_value) {
                    thread_best = bats[i];
                }
            }

            #pragma omp critical
            {
                if (thread_best.f_value > iter_best.f_value) {
                    iter_best = thread_best;
                }
            }
        }

        best_bat = iter_best;

        if (t % 100 == 0) {
            printf("[Iter %d] Best f_value = %f\n", t, best_bat.f_value);
        }
    }

    printf("\nFinal best f_value = %f\n", best_bat.f_value);
    printf("Final position = (");
    for (int d = 0; d < dimension; d++) {
        printf("%s%f", (d == 0 ? "" : ", "), best_bat.x_i[d]);
    }
    printf(")\n");

    return 0;
}
