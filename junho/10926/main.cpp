#include <iostream>
#include <string>
using namespace std;

int main(void) {
    ios_base::sync_with_stdio(false); cin.tie(nullptr); cout.tie(nullptr);
    string id;              // 1. 문자열을 저장하는 변수 선언
    cin >> id;              // 2. 입력받은 문자열을 id에 저장
    cout << id << "??!";    // 3. 입력받은 id와 "??!"를 붙여서 출력

    return 0;
}