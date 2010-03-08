// Compile with gcc fft.c -lfftw3 -lm -o fft.fftout 
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <fftw3.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
        
int loadIn(char *filename, fftw_complex *fftin, int size);
int compare_phi(const void *a, const void *b);
const double EPSILON = 1E-7;

int main(int argc, char **argv)
{
    char *filename;
    fftw_complex *fftin = NULL;
    fftw_complex *fftout = NULL;
    double *outputs;
    fftw_plan p;
    int N = 1000;
    int i, rc;

    if (argc < 2)
    {
        filename = strdup("in.csv");
    }
    else
    {
        filename = strdup(argv[1]);
    }

    if (argc > 2)
    {
        N = atoi(argv[2]);
    }

    fftin = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * N);
    if (fftin == NULL)
    {
        fprintf(stderr, "Failed to allocate fftin\n");
    }
    fftout = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * N);
    if (fftout == NULL)
    {
        fprintf(stderr, "Failed to allocate fftout\n");
    }
    outputs = (double *)malloc(2*N*sizeof(double));
    if (outputs == NULL)
    {
        fprintf(stderr, "Failed to allocate outputs\n");
    }

    rc = loadIn(filename, fftin, N);

    if (rc != 0)
    {
        fprintf(stderr, "Failed to read fftinput file %s\n", filename);
        free(filename);
        exit(1);
    }
    free(filename);
    filename = NULL;

    p = fftw_plan_dft_1d(N, fftin, fftout, FFTW_FORWARD, FFTW_ESTIMATE);

    fftw_execute(p); // repeat as needed 

    for (i=0; i < 1000; ++i)
    {
        double x,y;
        double z,phi;

        x = __real__ fftout[i];
        y = __imag__ fftout[i];

        z = sqrt(x*x+y*y);
        phi=atan2(y,x);

        outputs[i*2] = z;
        outputs[i*2+1] = phi;

        /** Generate the output */
        //printf("%f+%fi\n", x, y);
        //printf("|%f|(cos(%f)+isin(%f))\n", z, phi, phi);
    }

    qsort(outputs, N, 2*sizeof(double), compare_phi);
    for (i=0; i < 1000; ++i)
    {
        printf("%f, %f\n", outputs[i*2], outputs[i*2+1]);
    }
         
    fftw_destroy_plan(p);
         
    fftw_free(fftin); fftw_free(fftout);
	return 0;
}

int loadIn(char *filename, fftw_complex *fftin, int size)
{
    char buffer[256];
    double number;
    FILE *fp = NULL;
    int i = 0;

    fp = fopen(filename, "r");
    if (fp == NULL)
    {
        return errno;
    }

    fprintf(stderr, "loading inputs...\n");
    while(i < size && !feof(fp))
    {
        fgets(buffer, 256, fp);
        __real__ fftin[i] = strtod(buffer, NULL);
        __imag__ fftin[i] = 0.0;
        i++;
    }

    fclose(fp);
    fprintf(stderr, "%i inputs loaded.\n", i);
    return 0;
}

int compare_phi(const void *a, const void *b)
{
    double aphi = ((double *)a)[1];
    double bphi = ((double *)b)[1];

    // assume they're equal if they're closer than epsilon
    if (abs(aphi - bphi) < EPSILON)
    {
        return 0;
    }

    // a < b
    if (aphi < bphi)
    {
        return -1;
    }

    // a must be greater than b
    return 1;
}

