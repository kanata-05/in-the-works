#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <gmp.h>
#include <time.h>

void compute_pi(char *pi_str, int max_time, double *elapsed_seconds) {
    time_t start_time = time(NULL);
    int k = 0; // term counter
    mpf_set_default_prec(1000000);

    mpf_t sum, pi, term, multiplier;
    mpf_inits(sum, pi, term, multiplier, NULL);
    mpf_set_ui(sum, 0);
    mpf_set_ui(multiplier, 1);  // starts as 1

    // get C = 426880 * sqrt(10005)
    mpf_t C;
    mpf_init(C);
    mpf_set_ui(C, 10005);
    mpf_sqrt(C, C);
    mpf_mul_ui(C, C, 426880);

    // term[k] = (-1)^k * (6k)!/( (3k)! * (k!)^3 ) * (13591409 + 545140134*k) / (640320^(3k))
    mpz_t a, b, c, d, e, f, g;
    mpz_inits(a, b, c, d, e, f, g, NULL);

    while (max_time == -1 || difftime(time(NULL), start_time) < max_time) {
        
        mpz_fac_ui(a, 6 * k);           // a = (6k)!
        mpz_fac_ui(b, 3 * k);           // b = (3k)!
        mpz_fac_ui(c, k);               // c = k!
        mpz_pow_ui(d, c, 3);            // d = (k!)^3

        // e = 640320^(3k)
        if (k == 0)
            mpz_set_ui(e, 1);
        else
            mpz_ui_pow_ui(e, 640320, 3 * k);

        // f = (6k)! / (k!)^3
        mpz_fdiv_q(f, a, d);
        // f * (13591409 + 545140134*k)
        unsigned long term_const = 13591409 + 545140134 * k;
        mpz_mul_ui(f, f, term_const);
        if (k % 2 == 1)
            mpz_neg(f, f);

        // g = (3k)! * e
        mpz_mul(g, b, e);

        
        mpf_t num, den;
        mpf_inits(num, den, NULL);
        mpf_set_z(num, f);
        mpf_set_z(den, g);
        mpf_div(term, num, den);
        mpf_clear(num);
        mpf_clear(den);

        mpf_mul(term, term, multiplier);
        mpf_add(sum, sum, term);

        // multiplier_next = multiplier * ( -640320^3 / 24 )
        mpf_t temp;
        mpf_init(temp);
        mpf_set_ui(temp, 640320);
        mpf_pow_ui(temp, temp, 3); // temp = 640320^3
        mpf_div_ui(temp, temp, 24);
        mpf_neg(temp, temp);
        mpf_mul(multiplier, multiplier, temp);
        mpf_clear(temp);

        k++;  // next term
    }

    // pi = C / sum.
    mpf_div(pi, C, sum);

    gmp_sprintf(pi_str, "%.*Ff", 1000, pi);

    *elapsed_seconds = difftime(time(NULL), start_time);

    mpf_clears(sum, pi, term, multiplier, C, NULL);
    mpz_clears(a, b, c, d, e, f, g, NULL);
}

void find_in_pi(const char *pi_str, const char *sequence, double elapsed) {
    char *position = strstr(pi_str, sequence);
    if (position) {
        int decimal_place = (int)(position - pi_str) - 1;
        printf("Sequence found! decimal place: %d time took: %.0f seconds\n", decimal_place, elapsed);
    } else {
        printf("Sequence not found in computed digits of Pi.\n");
    }
}

int main(int argc, char *argv[]) {
    int max_time = -1; // -t left unspecified
    char *sequence = NULL;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-t") == 0 && i + 1 < argc) {
            max_time = atoi(argv[i + 1]);
            i++;
        } else if (strcmp(argv[i], "-s") == 0 && i + 1 < argc) {
            sequence = argv[i + 1];
            i++;
        }
    }

    if (!sequence) {
        printf("Usage: %s [-t <number_of_seconds>] -s <string_of_numbers>\n", argv[0]);
        return 1;
    }

    if (max_time == -1) {
        printf("Warning: Argument -t has not been specified, the program will run until it has found the specified string.\n");
        printf("YOUR SYSTEM MAY CRASH.\n");
        printf("Are you sure you understand what you're doing? (y/n): ");
        char response;
        scanf(" %c", &response);
        if (response != 'y' && response != 'Y') {
            printf("Aborting.\n");
            return 1;
        }
    }
    char *pi_str = malloc(2000000);
    if (!pi_str) {
        fprintf(stderr, "Memory allocation failed.\n");
        return 1;
    }

    double elapsed;
    compute_pi(pi_str, max_time, &elapsed);
    find_in_pi(pi_str, sequence, elapsed);

    free(pi_str);
    return 0;
}

