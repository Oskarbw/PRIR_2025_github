import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.NoSuchElementException;
import java.util.Scanner;

public class Matrix {
    private final int MAX_MATRIX_DIMENSION = 10000;
    private double[][] values;
    private int rows;
    private int columns;

    public Matrix(String filename) {
        readMatrixFromFile(filename);
    }

    private Matrix(int rows, int columns) {
        this.rows = rows;
        this.columns = columns;
        values = new double[rows][columns];
    }

    public int getRows() {
        return rows;
    }

    public int getColumns() {
        return columns;
    }

    public double[][] getValues() {
        return values;
    }

    public void printMatrix() {
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < columns; j++) {
                System.out.printf("%.2f   ", values[i][j]);
            }
            System.out.println();
        }
    }

    public Matrix multiply(Matrix matrixB, int threadsNumber) {
        validateMatrixMultiplication(matrixB);
        Matrix result = new Matrix(rows, matrixB.columns);
        ArrayList<Thread> threads = new ArrayList<Thread>();

        int resultMatrixElementsNumber = rows * matrixB.columns;
        int operationsPerThread = resultMatrixElementsNumber / threadsNumber;
        int rest = resultMatrixElementsNumber % threadsNumber;
        int operationsNumber = 0;
        int position = 0;

        for (int i = 0; i < threadsNumber; i++) {
            if (operationsPerThread == 0 && rest == 0) {
                break;
            }
            position += operationsNumber;
            operationsNumber = operationsPerThread;
            if (rest > 0) {
                operationsNumber++;
                rest--;
            }
            threads.add(new Thread(new MatrixMultiplier(this, matrixB, result, operationsNumber, position))); 
            threads.get(i).start();
        }

        waitTilAllThreadsFinish(threads);
        return result;
    }

    private void readMatrixFromFile(String filename) {
        try {
            Scanner scanner = new Scanner(new File(filename));
            rows = scanner.nextInt();
            columns = scanner.nextInt();
            validateMatrixSize();
            values = new double[rows][columns];
            for (int i = 0; i < rows; i++) {
                for (int j = 0; j < columns; j++) {
                    values[i][j] = Double.parseDouble(scanner.next());
                }
            }
            scanner.close();
        } catch (FileNotFoundException e) {
            System.out.println("Nie znaleziono pliku " + filename);
            System.exit(-2);
        } catch (NoSuchElementException | NumberFormatException e) {
            System.out.println("Nieprawidłowy format pliku " + filename);
            System.exit(-3);
        }
    }

    private void validateMatrixSize() {
        if (rows <= 0 || columns <= 0) {
            System.out.println("Macierz musi mieć co najmniej jeden wiersz i jedną kolumnę");
            System.exit(-4);
        }
        if (rows > MAX_MATRIX_DIMENSION || columns > MAX_MATRIX_DIMENSION) {
            System.out.println("Żaden z wymiarów macierzy nie może przekraczać 10000");
            System.exit(-5);
        }
    }

    private void validateMatrixMultiplication(Matrix matrixB) {
        if (columns != matrixB.rows) {
            System.out.println("Liczba kolumn pierwszej macierzy musi być równa liczbie wierszy drugiej macierzy");
            System.exit(-6);
        }
    }

    private void waitTilAllThreadsFinish(ArrayList<Thread> threads) {
        for (Thread thread : threads) {
            try {
                thread.join();
            } catch (InterruptedException e) {
                System.out.println("Wątek został przerwany");
                System.exit(-7);
            }
        }
    }
}
