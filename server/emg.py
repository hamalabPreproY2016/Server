# vim:fileencoding=utf-8
def Getave( c ) :
     sum=0
     for i in range(len(c)):
             sum = sum + c[i]["value"]
     ave = sum/len(c)
     return ave

def EmgAnarayze(arr, ave) :
    for i in range(len(arr) - 1):
        before = arr[i]['value']
        print before
        after = arr[i + 1]['value']
        result = Getnow(before, after, ave)
        if (result != 2):
            return True
    return False 

def Getnow( before, after, ave ) :
     now1 = 0
     now2 = 0
     result = 0
     if int(after) < 900 :
         now1 = 1
     bunshi = float(after)-float(before)
     if bunshi/21 > -1.5 and bunshi/21 < 1.5:
         now2=1
     if now1==now2 :
         if int(after) >= (ave+29) :
             result=1         
         else :
             result=2
     else :
         result=3
     return result
