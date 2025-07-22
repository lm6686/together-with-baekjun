import sys

N = int(sys.stdin.readline())

for i in range(N):
    M = int(sys.stdin.readline())

    while True:
        is_prime = True

        if M < 2:
            is_prime = False
        else:
            for j in range(2, int(M ** 0.5) + 1):
                if M % j == 0:
                    is_prime = False
                    break

        if is_prime:
            print(M)
            break
        else:
            M += 1
