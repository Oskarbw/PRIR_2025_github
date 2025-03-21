public class Main {
    private static final int MAX_THREAD_NUMBER = 10000;
    public static double sum;
    public static double squaresSum;

    public static void main(String[] args) {
        if (args.length < 3) {
            System.out.println("Program wymaga trzech argumentów: liczbę wątków, ścieżkę do pliku z macierzą A i ścieżkę do pliku z macierzą B");
            System.exit(-1);
        }

        int threadsNumber = 1;
        try {
            threadsNumber = Integer.parseInt(args[0]);
            if (threadsNumber > MAX_THREAD_NUMBER) {
                System.out.println("Liczba wątków nie może przekraczać 10000");
                System.exit(-2);
            }
        } catch (NumberFormatException e) {
            System.out.println("Pierwszy argument musi być liczbą całkowitą");
            System.exit(-3);
        }

        Matrix matrixA = new Matrix(args[1]);
        Matrix matrixB = new Matrix(args[2]);
        Matrix result = matrixA.multiply(matrixB, threadsNumber);
        System.out.println("MATRIX C:");
        result.printMatrix();
        System.out.printf("SUMA ELEMENTÓW MACIERZY WYJŚCIOWEJ: %.2f\nNORMA FROBENIUSA: %.2f", sum, Math.sqrt(squaresSum));

    }
}