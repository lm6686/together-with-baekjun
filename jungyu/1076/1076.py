a = input()
b = input()
c = input()
d = {"black":"0", "brown":"1", "red":"2", "orange":"3", "yellow":"4",
    "green":"5", "blue":"6", "violet":"7", "grey":"8", "white":"9"}
a_int = int(d[a])
b_int = int(d[b])
c_int = int(d[c])
print((10*a_int + b_int)*(10**c_int))