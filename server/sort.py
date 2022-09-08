a = [1,55,47,4,2,5,674,12,2,4,2]
for i in range(1,len(a)):
    for r in range(i,0,-1):
        if a[r-1] > a[r]:
            a[r-1], a[r] = a[r], a[r-1]
print(a)