public class MatrixMultiplier implements Runnable {
    private final Matrix matrixA;
    private final Matrix matrixB;
    private final Matrix result;
    private final int operationsNumber;
    private final int position;
    private int startRow;
    private int startColumn;
    private int endRow;
    private int endColumn;

    public MatrixMultiplier(Matrix matrixA, Matrix matrixB, Matrix result, int operationsNumber, int position) {
        this.matrixA = matrixA;
        this.matrixB = matrixB;
        this.result = result;
        this.operationsNumber = operationsNumber;
        this.position = position;
        initStartEndIndexes();
    }

    @Override
    public void run() {
        multiply();
        double sumValue = sumComputedValues();
        double squaresSumValue = sumSquaresOfComputedValues();
        addToGlobalVariables(sumValue, squaresSumValue);
    }

    private void multiply() {
        double[][] resultValues = result.getValues();

        for (int i = startRow; i <= endRow; i++) {
            for (int j = (i == startRow ? startColumn : 0); j < (i == endRow ? endColumn : result.getColumns()); j++) {
                double sum = 0;
                for (int k = 0; k < matrixA.getColumns(); k++) {
                    sum += matrixA.getValues()[i][k] * matrixB.getValues()[k][j];
                }
                resultValues[i][j] = sum;
            }
        }
    }

    private double sumComputedValues() {
        double sum = 0;
        double[][] resultValues = result.getValues();
        for (int i = startRow; i <= endRow; i++) {
            for (int j = (i == startRow ? startColumn : 0); j < (i == endRow ? endColumn : result.getColumns()); j++) {
                sum += resultValues[i][j];
            }
        }
        return sum;
    }

    private double sumSquaresOfComputedValues() {
        double sum = 0;
        double[][] resultValues = result.getValues();
        for (int i = startRow; i <= endRow; i++) {
            for (int j = (i == startRow ? startColumn : 0); j < (i == endRow ? endColumn : result.getColumns()); j++) {
                sum += resultValues[i][j] * resultValues[i][j];
            }
        }
        return sum;
    }

    private synchronized void addToGlobalVariables(double sumValue, double squaresSumValue) {
        Main.sum += sumValue;
        Main.squaresSum += squaresSumValue;
    }

    private void initStartEndIndexes() {
        int resultColumns = result.getColumns();
        startRow = position / resultColumns;
        startColumn = position % resultColumns;
        endRow = (position + operationsNumber) / resultColumns;
        endColumn = (position + operationsNumber) % resultColumns;
    }
}
