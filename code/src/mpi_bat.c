#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <mpi.h>

#include "bat.h"
#include "bat_utils.h"

#define N_BATS     30
#define MAX_ITERS  10000

int main(int argc, char *argv[]) {

    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    /* Simple assumption */
    if (N_BATS % size != 0) {
        if (rank == 0) {
            printf("N_BATS must be divisible by number of processes\n");
        }
        MPI_Finalize();
        return 0;
    }

    int local_n = N_BATS / size;

    Bat *all_bats = NULL;
    Bat local_bats[local_n];

    Bat local_best, global_best;

    srand(time(NULL) + rank * 100);

    /* ---------- Initialization ---------- */
    if (rank == 0) {
        all_bats = malloc(N_BATS * sizeof(Bat));
        initialize_bats(all_bats, &global_best);
    }

    MPI_Scatter(
        all_bats,
        local_n * sizeof(Bat),
        MPI_BYTE,
        local_bats,
        local_n * sizeof(Bat),
        MPI_BYTE,
        0,
        MPI_COMM_WORLD
    );

    /* ---------- Main loop ---------- */
    for (int t = 0; t < MAX_ITERS; t++) {

        /* Update local bats */
        for (int i = 0; i < local_n; i++) {
            update_bat(local_bats, &global_best, i, t);
        }

        /* Find local best */
        local_best = local_bats[0];
        for (int i = 1; i < local_n; i++) {
            if (local_bats[i].f_value > local_best.f_value) {
                local_best = local_bats[i];
            }
        }

        /* ---------- Global best using Allreduce ---------- */
        struct {
            double value;
            int rank;
        } local_data, global_data;

        local_data.value = local_best.f_value;
        local_data.rank  = rank;

        MPI_Allreduce(
            &local_data,
            &global_data,
            1,
            MPI_DOUBLE_INT,
            MPI_MAXLOC,
            MPI_COMM_WORLD
        );

        /* Broadcast the best bat */
        if (rank == global_data.rank) {
            global_best = local_best;
        }

        MPI_Bcast(
            &global_best,
            sizeof(Bat),
            MPI_BYTE,
            global_data.rank,
            MPI_COMM_WORLD
        );

        if (rank == 0 && t % 1000 == 0) {
            printf("[Iter %d] Global best = %f\n", t, global_best.f_value);
        }
    }

    if (rank == 0) {
        printf("\nFinal best f_value = %f\n", global_best.f_value);
        printf("Final position = (");
        for (int d = 0; d < dimension; d++) {
            printf("%s%f", d == 0 ? "" : ", ", global_best.x_i[d]);
        }
        printf(")\n");
        free(all_bats);
    }

    MPI_Finalize();
    return 0;
}
