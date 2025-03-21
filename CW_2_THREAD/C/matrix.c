#include <stdio.h>
#include <stdlib.h>
#include <string.h>  
#include <pthread.h>
#include <math.h>

const int MAX_MATRIX_DIMENSION = 10000;
const int MAX_THREADS_NUMBER = 10000;

// macierze jako zmienne globalne
double **A;
double **B;
double **C;

double sumOfElementsOfC;
double sumOfSquaresOfC;

pthread_mutex_t mutex;

struct arg_struct {
    int position;
    int numberOfOperations;
    int resultColumns;
    int matrixAColumns;
};

void* thread_func(void* arguments) {  
    struct arg_struct args = *(struct arg_struct *)arguments;
    int resultColumns = args.resultColumns;
    int position = args.position;
    int numberOfOperations = args.numberOfOperations;
    int matrixAColumns = args.matrixAColumns;
    free(arguments);

    // znajdź zakresy
    int startRow = position / resultColumns;
    int startColumn = position % resultColumns;
    int endRow = (position + numberOfOperations - 1) / resultColumns;
    int endColumn = (position + numberOfOperations - 1) % resultColumns + 1;

    // oblicz swoją cześć
    double sumOfSums = 0;
    double sumOfSquares = 0;
    for (int i = startRow; i <= endRow; i++) {
        for (int j = (i == startRow ? startColumn : 0); j < (i == endRow ? endColumn : resultColumns); j++) {
            double sum = 0;
            for (int k = 0; k < matrixAColumns; k++) {
                sum += A[i][k] * B[k][j];
            }
            C[i][j] = sum;
            sumOfSums += sum;
            sumOfSquares += sum*sum;
        }
    }

    // dodaj swoje podsumy do zmiennych globalnych - część chroniona mutexem
    int err;
    if ((err = pthread_mutex_lock(&mutex)) != 0) {
        fprintf(stderr, "Błąd przy pthread_mutex_lock: %s\n", strerror(err));
        exit(-1);
    }

    sumOfElementsOfC += sumOfSums;
    sumOfSquaresOfC += sumOfSquares;

    if ((err = pthread_mutex_unlock(&mutex)) != 0) {
        fprintf(stderr, "Błąd przy pthread_mutex_unlock: %s\n", strerror(err));
        exit(-2);
    }

    printf("Wątek zakończył pracę (zakres: [%d,%d] -> [%d,%d])\n", 
        startRow, startColumn, endRow, endColumn - 1);
    return NULL;  
}  

void print_matrix(double **A, int m, int n) {
    int i, j;
    for (i = 0; i < m; i++) {
        for (j = 0; j < n; j++) {
            printf("%.2f ", A[i][j]);
        }
        printf("\n");
    }
}

int main(int argc, char **argv) {  
    // wczytanie argumentów
    if (argc != 4) {
        printf("Poprawne użycie: [liczba wątków] [ścieżka do pliku A] [ścieka do pliku B]/n");
        exit(-1);
    }

    int numberOfThreads = atoi(argv[1]);
    if (numberOfThreads < 1 || numberOfThreads > MAX_THREADS_NUMBER) {
        printf("Liczba wątków musi być z zakresu <1, 10000>");
        exit(-1);
    }

    printf("Liczba wątków: %d\n", numberOfThreads);

    char* matrixAFileName = argv[2];
    char* matrixBFileName = argv[3];

    // otwarcie plików
    FILE *fpa;
    FILE *fpb;
    fpa = fopen(matrixAFileName, "r");
    fpb = fopen(matrixBFileName, "r");
    if (fpa == NULL || fpb == NULL) {
        printf("Błąd przy otwarciu pliku");
        exit(-2);
    }

    // załadowanie wymiarów macierzy z plików
    int ma, mb, na, nb;
    int error;
    if ((error = fscanf(fpa, "%d", &ma)) < 1) {
        printf("Niepoprawny format pliku. %d", error);
        exit(-11);
    }
    if ((error = fscanf(fpa, "%d", &na)) < 1) {
        printf("Niepoprawny format pliku. %d", error);
        exit(-12);
    }
    if ((error = fscanf(fpb, "%d", &mb)) < 1) {
        printf("Niepoprawny format pliku. %d", error);
        exit(-13);
    }
    if ((error = fscanf(fpb, "%d", &nb)) < 1) {
        printf("Niepoprawny format pliku. %d", error);
        exit(-14);
    }
    
    if (ma < 1 || na < 1 || mb < 1 || nb < 1) {
        printf("Złe wymiary macierzy! Wymiary macierzy nie mogą być mniejsze niż 1");
        exit(-3);
    }
    printf("Wymiary A: %dx%d\n", ma, na);
    printf("Wymiary B: %dx%d\n", mb, nb);
    if (na != mb) {
        printf("Złe wymiary macierzy! Liczba kolumn macierzy A powinna byc rowna liczbie wierszy macierzy B");
        exit(-3);
    }
    if (ma > MAX_MATRIX_DIMENSION || na > MAX_MATRIX_DIMENSION 
            || mb > MAX_MATRIX_DIMENSION || nb > MAX_MATRIX_DIMENSION) {
        printf("Złe wymiary macierzy! Żaden wymiar macierzy nie powinien przekraczać 10000");
        exit(-3);
    }
   
    // zaalokowanie miejsca dla macierzy
    A = malloc(ma * sizeof(double *));
    if (A == NULL) {
        printf("Błąd alokacji pamięci dla A");
        exit(-4);
    }
    for (int i = 0; i < ma; i++) {
        A[i] = malloc(na * sizeof(double));
        if (A[i] == NULL) {
            printf("Błąd alokacji pamięci dla A[i]");
            exit(-4);
        }
    }

    B = malloc(mb * sizeof(double *));
    if (B == NULL) {
        printf("Błąd alokacji pamięci dla B");
        exit(-4);
    }
    for (int i = 0; i < mb; i++) {
        B[i] = malloc(nb * sizeof(double));
        if (B[i] == NULL) {
            printf("Błąd alokacji pamięci dla B[i]");
            exit(-4);
        }
    }

    C = malloc(ma * sizeof(double *));
    if (C == NULL) {
        printf("Błąd alokacji pamięci dla C");
        exit(-4);
    }
    for (int i = 0; i < ma; i++) {
        C[i] = malloc(nb * sizeof(double));
        if (C[i] == NULL) {
            printf("Błąd alokacji pamięci dla C[i]");
            exit(-4);
        }
    }
    printf("Wymiary C: %dx%d\n", ma, nb);
    
    // wczytanie A
    double x;
    for (int i = 0; i < ma; i++) {
        for (int j = 0; j < na; j++) {
            if((error = fscanf(fpa, "%lf", &x)) < 1) {
                printf("Niepoprawny format pliku. %d", error);
                exit(-15);
            }
            A[i][j] = x;
        }
    }
    printf("A:\n");
    print_matrix(A, ma, mb);

    // wczytanie B
    for (int i = 0; i < mb; i++) {
        for (int j = 0; j < nb; j++) {
            if((error = fscanf(fpb, "%lf", &x)) < 1) {
                printf("Niepoprawny format pliku. %d", error);
                exit(-16);
            }
            B[i][j] = x;
        }
    }
    printf("B:\n");
    print_matrix(B, mb, nb);

    // podzielenie pracy dla wątków
    pthread_t threads[numberOfThreads];
    pthread_mutex_init(&mutex, NULL);

    sumOfElementsOfC = 0;
    sumOfSquaresOfC = 0;

    int numberOfElementsOfC = ma * nb;
    int operationsPerThread = numberOfElementsOfC / numberOfThreads;
    int rest = numberOfElementsOfC % numberOfThreads;

    int numberOfRunThreads = 0;
    int numberOfOperations = 0;
    int position = 0;
    struct arg_struct *args;

    for (int i = 0; i < numberOfThreads; i++) {
        if (operationsPerThread == 0 && rest == 0) {
            break;
        }
        position += numberOfOperations;
        numberOfOperations = operationsPerThread;
        if (rest > 0) {
            numberOfOperations++;
            rest--;
        }  
        args = malloc(sizeof(struct arg_struct));
        if (args == NULL) {
            printf("Błąd alokacji pamięci dla args");
            exit(-5);
        }
        (*args).position = position;
        (*args).numberOfOperations = numberOfOperations;
        (*args).resultColumns = nb;
        (*args).matrixAColumns = na;

        if (pthread_create(&threads[i], NULL, thread_func, (void*)args) != 0) {
            printf("Błąd przy tworzeniu wątku");
            exit(-5);
        }
        numberOfRunThreads++;
    }

    // zaczekaj na zakonczenie pracy watkow
    for (int i = 0; i < numberOfRunThreads; i++) {
        if (pthread_join(threads[i], NULL) != 0) {
            printf("Błąd przy oczekiwaniu na wątek");
            exit(-6);
        }
    }

    // wypisanie wyniku
    printf("C:\n");
    print_matrix(C, ma, nb);

    printf("Suma elementów: %.2f\n", sumOfElementsOfC);
    double frobeniusNorm = sqrt(sumOfSquaresOfC);
    printf("Norma frobeniusa: %.2f\n", frobeniusNorm);

    //zwolnienie miejsca i zamkniecie plików
    for (int i = 0; i < ma; i++) {
        free(A[i]);
    }
    free(A);

    for (int i = 0; i < mb; i++) {
        free(B[i]);
    }
    free(B);

    for (int i = 0; i < ma; i++) {
        free(C[i]);
    }
    free(C);

    fclose(fpa);
    fclose(fpb);

    pthread_mutex_destroy(&mutex);

    return 0;
}