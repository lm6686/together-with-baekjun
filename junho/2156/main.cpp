#include <iostream>

int main()
{
    int wine[10001] = { 0, };
    int n;
    int drink[10001] = { 0, };
    std::cin >> n;
    for (int index = 0; index < n; index++) {
        std::cin >> wine[index];
    }

    drink[0] = wine[0];
    drink[1] = wine[1] + wine[0];
    drink[2] = std::max(drink[1], std::max(wine[2] + wine[0], wine[2] + wine[1]));
    
    for(int index = 3; index < n ; index++){
        drink[index] = std::max(drink[index - 1], 
                                std::max(drink[index - 2] + wine[index], 
                                         drink[index - 3] + wine[index] + wine[index - 1]));
    }
    std::cout << drink[n - 1] << std::endl;
}
