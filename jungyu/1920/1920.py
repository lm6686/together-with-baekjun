a = input()
b = set(map(int, input().split(" ")))
c = input()
d = list(map(int, input().split(" ")))
for i in d:
    if i in b:
        print(1)
    else:
        print(0)