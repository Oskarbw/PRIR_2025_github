public class Main {
    public static double sum;
    public static double squaresSum;

    public static void main(String[] args) {
        if (args.length < 3) {
            System.out.println("Program wymaga trzech argumentów: liczbę wątków, nazwę pliku z macierzą A i nazwę pliku z macierzą B");
            System.exit(1);
        }

        int threadsNumber = 1;
        try {
            threadsNumber = Integer.parseInt(args[0]);
        } catch (NumberFormatException e) {
            System.out.println("Pierwszy argument musi być liczbą całkowitą");
            System.exit(1);
        }

        Matrix matrixA = new Matrix(args[1]);
        Matrix matrixB = new Matrix(args[2]);

        // Resetowanie zmiennych statycznych przed mnożeniem
        sum = 0;
        squaresSum = 0;

        Matrix result = matrixA.multiply(matrixB, threadsNumber);
        System.out.println("MATRIX C:");
        result.printMatrix();
        System.out.println("SUMA ELEMENTOW MACIERZY WYJSCIOWEJ: " + sum + ", NORMA FROBENIUSA: " + Math.sqrt(squaresSum));

    }
}