import pyautogui
from random import randint as rnd, choice
from time import sleep, time
#to do
#global unsnum
#unsnum sat-1

#returns rounded values for screen coordinates
def getpixel(x,y):
    global screen
    rgb=screen.getpixel((x,y))
    return tuple(int((rgb[i]/255+.05)*10) for i in (0,1,2))

#returns rounded rgb values
def roundcolor(clr):
    return tuple(int((int(clr[i:i+2], 16)/255+.05)*10) for i in (0, 2, 4))
    
clrindex={
    roundcolor("a1d149"):"u",
    roundcolor("aad751"):"u",
    roundcolor("e5c29f"):"0",
    roundcolor("d7b899"):"0",
    roundcolor("1976d2"):"1",
    roundcolor("3d8f3f"):"2",
    roundcolor("d32f2f"):"3",
    roundcolor("7e24a2"):"4",
    roundcolor("fe9001"):"5",
    roundcolor("269ea5"):"6",
}

global screen, board, bombs, clicked, clicks, unsnumcount, won, loop, unsatisfied, toadd, toremove, satisfied

def usleep():
    global screen
    screen=pyautogui.screenshot()

#initialize board
def _init():
    global board, bombs, clicked, clicks, unsnumcount, won, loop, unsatisfied, toadd, toremove, satisfied
    board = list()
    bombs = set()
    unsatisfied = dict()
    satisfied=set()
    toadd=set()
    toremove=set()
    clicks = set()
    clicked = set()
    won=False
    loop = 0
    unsnumcount=0
    for x in range (0,18):
        board.append(list())
        for y in range(0,14):
            board[x].append('u')

#clicks on tile
def clicktile(x,y):
    pyautogui.click(99+x*45,340+y*45)
    
#returns tile type for screen coordinate
def gettile(x,y):
    global won
    tries=0
    while tries<10 and not won:
        try:
            return clrindex[getpixel(99+x*45,340+y*45)]
        except:
            usleep()
            tries+=1
        else:
            break
    won=True
    return 'w'
    
def checksat(x,y,n):
    global unsnumcount
    npot=0
    ndef=0
    nbombs=set()
    unsatcheck=set()
    for i in range (x-1,x+2):
        for j in range(y-1,y+2):
            if (i,j) in bombs:
                ndef+=1
                npot+=1
            elif (i!=x or j!=y) and i>=0 and i<18 and j>=0 and j<14:
                dc=board[i][j]
                if dc=='u':
                    dc=gettile(i,j)
                    if dc!='w':
                        if dc=='u':
                            npot+=1
                            nbombs.add((i,j))
                        elif (i,j,dc) not in satisfied or (i,j,dc) not in unsatisfied:
                            board[i][j]=dc
                            toadd.add((i,j,dc,0))
                elif (i,j,dc) not in toremove and (i,j,dc) in unsatisfied and unsatisfied[(i,j,dc)]!=0:
                    unsatcheck.add((i,j,dc))
    if n=='0' or ndef==int(n) or npot==int(n):
        toremove.add((x,y,n))
        if n=='0': 
            if npot>0:
                dc=gettile(x,y)
                tries=0
                while not won and tries<20 and dc=='0' and dc=='u':
                    usleep()
                    dc=gettile(x,y)
                if dc!='0' and dc!='u':
                    board[x][y]=dc
                    toremove.add((x,y,n))
                    toadd.add((x,y,dc,0))
            return 
    if ndef==int(n):
        for s in nbombs:
            clicks.add(s)
    elif npot==int(n):
        for b in nbombs:
            bombs.add(b)
    elif len(nbombs)>0:
        unsatisfied[(x,y,n)]=(nbombs,ndef)
        for i1,j1,dc1 in unsatcheck:
            bombscheck=unsatisfied[(i1,j1,dc1)][0]
            if len(nbombs)>len(bombscheck) and len(nbombs.intersection(bombscheck))==len(bombscheck):
                unsnumcount+=1
                unsnum=nbombs.difference(bombscheck)
                if ndef+int(dc1)-unsatisfied[(i1,j1,dc1)][1]==int(n):
                    for s in unsnum:
                        clicks.add(s)
                elif n!='1' and len(unsnum)==int(n)-(ndef+int(dc1)-unsatisfied[(i1,j1,dc1)][1]) and ndef+int(dc1)-unsatisfied[(i1,j1,dc1)][1]==int(n)-1:
                    for b in unsnum:
                        bombs.add(b)
                break

def updateboard():
    global toremove, toadd, unsure, clicktemp
    if not won:
        if len(unsatisfied)==0:
            for x in range(0,18):
                for y in range(0,14):
                    if board[x][y]=='u':
                        n=gettile(x,y)
                        if n!='u':
                            unsatisfied[(x,y,n)] = 0
                            board[x][y]=n
                            break
                        if won: break
                if len(unsatisfied)>0 or won:
                    break
    
        for x,y,n in unsatisfied:
            if n!='w':
                checksat(x,y,n)

        for x,y,n,p in toadd:
            unsatisfied[(x,y,n)] = p
        toadd=set()

        for x,y,n in toremove:
            unsatisfied.pop((x,y,n))
            satisfied.add((x,y,n))
        toremove=set()

def drawboard():
    print("-----------------------------------")
    for y in range(0,14):
        r=''
        for x in range(0,18):
            n=board[x][y]
            if (x,y) in bombs:
                n="B"
            r+=n+' '
        print(r)
    print("-----------------------------------")

while True:
    print("restarting...")
    end="finished!"
    screen=pyautogui.screenshot()
    _init()
    if getpixel(721,261)!=roundcolor('ffffff'):
        pyautogui.click(730,275)
    startx, starty, = rnd(0, 17), rnd(0, 13)
    clicks.add((startx,starty))
    clicktile(startx, starty)
    while not won and (len(bombs)!=40 or len(unsatisfied)!=0 or len(satisfied)!=212):
        screen=pyautogui.screenshot()
        pyautogui.moveTo(76,230)
        for c in clicks:
            n = gettile(c[0],c[1])
            tries=0
            while (n=='u' or n=='w') and tries<20 and not won:
                usleep()
                n = gettile(c[0],c[1])
                tries+=1
            if n!='u' and n!='w':
                board[c[0]][c[1]] == n
                unsatisfied[(c[0],c[1],n)] = 0
        clicks = set()
        updateboard()
        for c in clicks:
            if c not in clicked:
                clicktile(c[0],c[1])
                clicked.add(c)
        if len(clicks)>0:
            loop=0
        else:
            loop+=1
        if loop>5:
            if len(bombs)<40:
                end="got stuck..."
            else:
                for x in range(0,18):
                    for y in range(0,14):
                        if (x,y) not in bombs and board[x][y]=='u':
                            clicktile(x,y)
            break
    
    drawboard()
    #print(f"errw={won}")
    #print(f"unsnum saved us {unsnumcount} times. praise unsnum!")
    print(end)
    sleep(3)
    pyautogui.typewrite('r')    