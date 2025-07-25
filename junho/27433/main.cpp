#include <iostream>
using namespace std;

int main() {
	cin.tie(NULL);
	ios_base::sync_with_stdio(false);

	int n;
	cin >> n;

    long long res = 1;
    for (int i = 1; i <= n; i++) {
        res *= i;
    }

	cout << res << endl;

	return 0;
}