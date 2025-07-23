#include <iostream>

#define N_MAX_SIZE 100

int main()
{
	int nMaxSize = 100;
	int coins[N_MAX_SIZE] = { 0, };
	int n, k;
	std::cin >> n >> k;
	for (int i = 0; i < n; i++) {
		std::cin >> coins[i];
	}

	int count = 0;
	int coinCount[100] = { 0, };

	int frontIndex = 0, endIndex = 0;
	int point = 0;
	while (true) {

		if (point < k && coins[endIndex] != 0) {
			point += coins[endIndex];
			coinCount[endIndex]++;
		}
		if (point == k) {
			count++;
		}
		if (point >= k) {
			point -= coins[endIndex];
			coinCount[endIndex]--;
			endIndex++;
		}
		if (coins[endIndex] == 0) {
			while (coinCount[endIndex] == 0)
			{
				endIndex--;
				if (endIndex < 0) {
					std::cout << count << std::endl;
					return 0;
				}
			}
			point -= coins[endIndex];
			coinCount[endIndex]--;
			endIndex++;
		}
	}
}