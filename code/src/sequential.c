#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#include "bat.h"
#include "bat_utils.h"

#define N_BATS     30
#define MAX_ITERS  10000

#define F_MIN      0.0
#define F_MAX      1.0

#define A0         1.0    // initial loudness
#define R0         1.0    // initial pulse rate
#define V0         0.0

#define ALPHA      0.97
#define GAMMA      0.1

#define Ub         5
#define Lb         -5

// ------- FONCTION SNAPSHOT ------------------------------------
void save_snapshot(const char *filename, Bat bats[]) {
    FILE *fp = fopen(filename, "w");
    if (!fp) {
        perror("fopen snapshot");
        return;
    }

    for (int i = 0; i < N_BATS; i++) {
        for (int d = 0; d < dimension; d++) {
            fprintf(fp, (d == 0) ? "%f" : ",%f", bats[i].x_i[d]);
        }
        fprintf(fp, "\n");
    }

    fclose(fp);
}

// -----------------------------------------------------------------





double compute_A_mean(Bat bats[]) {
    double sum = 0.0;
    for (int k = 0; k < N_BATS; k++) sum += bats[k].A_i;
    return sum / N_BATS;
}

// Initialize the bat population and find an initial best bat
void initialize_bats(Bat bats[], Bat *best_bat) {
    // simple choice: start positions uniformly in [-1, 1]
    for (int i = 0; i < N_BATS; i++) {

        // x_i and v_i
        for (int d = 0; d < dimension; d++) {
            bats[i].x_i[d] = uniform_random(-5.0, 5.0); // N(0,1)
            bats[i].v_i[d] = V0;
        }


        // frequency, loudness, pulse rate
        bats[i].f_i = F_MIN;      // will be updated later in the loop
        bats[i].A_i = A0;
        bats[i].r_i = R0;

        // evaluate f(x_i)
        bats[i].f_value = objective_function(bats[i].x_i);
    }

    // find initial best bat (here: maximize f_value, since exp(-(x^2+y^2)))
    int best_index = 0;
    for (int i = 1; i < N_BATS; i++) {
        if (bats[i].f_value > bats[best_index].f_value) {
            best_index = i;
        }
    }

    *best_bat = bats[best_index];  // copy best bat
}

void update_bat(Bat bats[], Bat *best_bat, int i, int t) {
    
    // 1. Update frequency
    double beta = uniform_random(0.0, 1.0);
    bats[i].f_i = F_MIN + (F_MAX - F_MIN) * beta;

    // 2. Update velocity (towards best solution)
    for (int d = 0; d < dimension; d++) {
        bats[i].v_i[d] += (best_bat->x_i[d] - bats[i].x_i[d] ) * bats[i].f_i;
    }

    // 3. Update position
    for (int d = 0; d < dimension; d++) {
        bats[i].x_i[d] += bats[i].v_i[d];

        // apply bounds
        if (bats[i].x_i[d] < Lb) bats[i].x_i[d] = Lb;
        if (bats[i].x_i[d] > Ub) bats[i].x_i[d] = Ub;
    }


    double candidate_x[dimension];

    // start from current position
    for (int d = 0; d < dimension; d++) {
        candidate_x[d] = bats[i].x_i[d];
    }

    // évalue la solution globale
    double Fnew = objective_function(candidate_x);  // F_global

    double rand_pulse = uniform_random(0.0, 1.0);
    if (rand_pulse > bats[i].r_i) {

        double local_x[dimension];

        double A_mean = compute_A_mean(bats);

        // local random walk around global best
        for (int d = 0; d < dimension; d++) {
            double eps = normal_random(0.0, 1.0);       // randn(1,d)
            local_x[d] = best_bat->x_i[d] + 0.1 * eps * A_mean;

            // borne la nouvelle solution 
            if (local_x[d] < Lb) local_x[d] = Lb;
            if (local_x[d] > Ub) local_x[d] = Ub;
        }
        // évalue la solution locale
        double F_local = objective_function(local_x);

        // si la locale est meilleure, elle devient la candidate
        if (F_local > Fnew) {   // on MAXIMISES
            for (int d = 0; d < dimension; d++) {
                candidate_x[d] = local_x[d];
            }
            Fnew = F_local;
        }
    }

    // ----- Acceptance by loudness (for this bat) -----
    double rand_loud = uniform_random(0.0, 1.0);

    if ((Fnew > bats[i].f_value) && (rand_loud < bats[i].A_i)) {
        // accept candidate as new position of bat i
        for (int d = 0; d < dimension; d++) {
            bats[i].x_i[d] = candidate_x[d];
        }
        bats[i].f_value = Fnew;

        // update A_i and r_i using alpha, gamma (Yang)
        bats[i].A_i *= ALPHA;                       // A_i^{t+1} = alpha * A_i^t
        bats[i].r_i = R0 * (1.0 - exp(-GAMMA * t)); // r_i^{t+1} = r0 * (1 - e^{-gamma t})

        if (Fnew > best_bat->f_value) {
            *best_bat = bats[i]; // ou copie explicite coordonnée par coordonnée
        }
    }


}


int main(void) {
    srand((unsigned int) time(NULL));

    Bat bats[N_BATS];
    Bat best_bat;

    initialize_bats(bats, &best_bat);

    for (int t = 0; t < MAX_ITERS; t++) {

        for (int i = 0; i < N_BATS; i++) {
            update_bat(bats, &best_bat, i, t);
        }

        /* snapshots aux itérations choisies */
        if (t == 0) {
            save_snapshot("snapshot_t000.csv", bats);
        } else if (t == 2500) {
            save_snapshot("snapshot_t250.csv", bats);
        } else if (t == 5000) {
            save_snapshot("snapshot_t500.csv", bats);
        } else if (t == 7500) {
            save_snapshot("snapshot_t750.csv", bats);
        }


        // afficher toutes les 100 itérations
        if (t % 100 == 0) {
            printf("[Iteration %d] Best f_value = %f  Position = (", t, best_bat.f_value);
            for (int d = 0; d < dimension; d++) {
                printf("%s%f", (d == 0 ? "" : ", "), best_bat.x_i[d]);
            }
            printf(")\n");
        }
    }


    printf("Final best f_value = %f\n", best_bat.f_value);
    printf("Final position = (");
    for (int d = 0; d < dimension; d++) {
        printf("%s%f", (d == 0 ? "" : ", "), best_bat.x_i[d]);
    }
    printf(")\n");

    return 0;
}
