# This is a sample Python script.
import random


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
col,row=(6,6)
tet = [[0]*6]*6
print(tet)


rows, cols = (6, 6)
arr = [[0 for i in range(cols)] for j in range(rows)]
print(arr)


for row in tet:
    print(row)

rn= [0,1,2,3,4,5]
a=random.choice(rn)
b=random.choice(rn)

print("the Number a is",a);
print("the number b is",b);
temp=[[a,b]]
k=0
if a==0:
    temp1=[a,a+1,a+2,a+3]
elif (a==6):
    temp2=[a,a-1,a-2,a-3]
else:
    while k<7:
        print("Inside")
        c=random.choice(rn)
        d=random.choice(rn)
        print("The value of a c = %s and d= %s ",c,d)
        for i in range (0,len(temp)):
            j=0
            add=0
            if ((temp[i][j] == c + 1) and (temp[i][j + 1] == d)) or ((temp[i][j] == c) and (temp[i][j + 1] == d - 1)) or ((temp[i][j] == c - 1) and (temp[i][j + 1] == d)) or ((temp[i][j] == c) and (temp[i][j + 1] == d + 1)):
                print ("C=",c)
                print("The value of Temp[i][j]",temp[i][j])
                temp3=[c,d]
                for l in range (0,len(temp)):
                    m=0
                    if(temp[l][m]==c) and (temp[l][m+1]==d):
                        add=1
                        break
                if(add==0):
                    temp.append(temp3)
                    k=k+1;
                    print("The Temp =",temp)
                    break

print("the Final output",temp)
for i in range(0,len(temp)):
    j=0
    print("The tet value=",temp[i][j],temp[i][j+1])

    tet[temp[i][j]][temp[i][j+1]]=1
    arr[temp[i][j]][temp[i][j + 1]] = 1




for row in arr:
    print(row)




