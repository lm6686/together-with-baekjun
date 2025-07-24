#include <stdio.h>
#include <string.h>
int number(char* color) {
    if (strcmp(color, "black")==0) return 0;
    else if (strcmp(color, "brown")==0) return 1;
    else if (strcmp(color, "red")==0) return 2;
    else if (strcmp(color, "orange")==0) return 3;
    else if (strcmp(color, "yellow")==0) return 4;
    else if (strcmp(color, "green")==0) return 5;
    else if (strcmp(color, "blue")==0) return 6;
    else if (strcmp(color, "violet")==0) return 7;
    else if (strcmp(color, "grey")==0) return 8;
    else if (strcmp(color, "white")==0) return 9;
    else return -1;}
int main(void) {
    char a[7], b[7], c[7];
    scanf("%s", a);
    scanf("%s", b);
    scanf("%s", c);
    int c_a = number(a);
    int c_b = number(b);
    int c_c = number(c);
    long long result = (c_a*10+c_b);
    for (int i = 0; i < c_c; i++){
        result*=10;
    }
    printf("%lld", result);
    return 0;
}