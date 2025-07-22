#include <iostream>
#include <string>
using namespace std;

int main() {
	cin.tie(NULL);
	ios_base::sync_with_stdio(false);

	int a, b, c;
	cin >> a >> b >> c;

	cout << a+b-c << "\n";

	string strA = to_string(a);
	string strB = to_string(b);
	string strAB = strA + strB;
	int res = stoi(strAB) - c;

	cout << res;

	return 0;
}