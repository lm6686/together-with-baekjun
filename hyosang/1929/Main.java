import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String[] numbers = scanner.nextLine().split(" ");
        int N = Integer.parseInt(numbers[0]);
        int M = Integer.parseInt(numbers[1]);
        scanner.close();
        find_decimal(N, M);
    }

    public static void find_decimal(int N, int M) {
        for (int i = N; i <= M; i++) {
            if (i < 2) continue;
            boolean isPrime = true;
            for (int j = 2; j <= Math.sqrt(i); j++) {
                if (i % j == 0) {
                    isPrime = false;
                    break;
                }
            }
            if (isPrime) {
                System.out.println(i);
            }
        }
    }
}