#include <iostream>

int main()
{
    int coins[101] = { 0, };
    int n, k;
    int dp[100000 + 1] = { 0, };
    std::cin >> n >> k;
    for (int index = 1; index <= n; index++) {
        std::cin >> coins[index];
    }

    dp[0] = 1;
    for (int coinIndex = 1; coinIndex <= n; coinIndex++) {
        for (int dpIndex = coins[coinIndex]; dpIndex <= k; dpIndex++) {
            dp[dpIndex] += dp[dpIndex - coins[coinIndex]];
        }
    }
    std::cout << dp[k] << std::endl;
}
