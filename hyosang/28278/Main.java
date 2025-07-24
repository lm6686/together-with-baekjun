import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.StringTokenizer;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();
        int N = Integer.parseInt(br.readLine());
        ArrayList<Integer> stack = new ArrayList<>();

        for (int i = 0; i < N; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int val = Integer.parseInt(st.nextToken());

            switch (val) {
                case 1:
                    int num = Integer.parseInt(st.nextToken());
                    stack.add(num);
                    break;
                case 2:
                    if (!stack.isEmpty()) {
                        sb.append(stack.remove(stack.size() - 1)).append('\n');
                    } else {
                        sb.append(-1).append('\n');
                    }
                    break;
                case 3:
                    sb.append(stack.size()).append('\n');
                    break;
                case 4:
                    sb.append(stack.isEmpty() ? 1 : 0).append('\n');
                    break;
                case 5:
                    if (!stack.isEmpty()) {
                        sb.append(stack.get(stack.size() - 1)).append('\n');
                    } else {
                        sb.append(-1).append('\n');
                    }
                    break;
            }
        }
        System.out.print(sb);
    }
}
