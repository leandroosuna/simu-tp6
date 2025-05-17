import numpy
from itertools import chain
from scipy.stats import chi
from scipy.stats import foldcauchy

AZUL = '\033[94m'
CYAN = '\033[96m'
BLANCO = '\033[0m'
VERDE = '\033[92m'
AMARILLO = '\033[93m'
ROJO = '\033[91m'
def PrintColor(color, msg, e = '\n'):
    print(f"{color}{msg} {BLANCO}",end=e)

def ILL():
    return chi.rvs(df= 0.20, loc= 59.999999999999986, scale = 250)

def TR():
    res = 1000
    while res > 800:
        res = foldcauchy.rvs(c =1.256741235220129, loc = 0.999999999922885, scale = 91.94734106845496)
    return res

def TRA():
    return TR()
def TRP():
    return TR()
def TRO():
    return TR()

def Random():
    return numpy.random.rand()

class ProxSalida:
    def __init__(self, T,S,C):
        self.T = T
        self.S = S
        self.C = C

#variables de control
P = 3
A = 3
O = 3

#contadores puestos
CA = 0
CM = 0
CB = 0

C = ''
#variables simulacion
#Tiempo proxima salida cada puesto
TPSP = [None] 
TPSA = [None] 
TPSO = [None] 
TPS = 0

STOA = [None]
ITOA = [None]
STOP = [None]
ITOP = [None]
STOO = [None]
ITOO = [None]

STRA = 0
STRP = 0
STRO = 0

NTA = 0
NTO = 0
NTP = 0

SLL = 0
SLLA = 0


STSA = 0
STSP = 0
STSO = 0

LLF = 0
LLD = 0
STLLA = 0
STLLP = 0
STLLO = 0

PORC_FALSAS = .23
PORC_DERIVADAS = .09
PORC_ALTA = .24
PORC_MEDIA = .59
# PORC_BAJA = .41

PORC_AMBULANCIA = 0.06
PORC_POLICIA = 0.83
# PORC_OTRO = 0.3

#contadores auxiliares criticidad servicio 
CAAP = 0
CAMP = 0
CABP = 0
CAAA = 0
CAMA = 0
CABA = 0
CAAO = 0
CAMO = 0
CABO = 0
CABS = 0

T = 0
TF = 31536000 
# TF = 500000

HV = 9999999999999999
TPLL = 0

verProgreso = False 

def Simular():
    global T, TF, TPLL

    while True:

        if verProgreso :
            it = int(T)
            if(it % 10000 == 0):
                print(f"{it}")
        
        TPS,i = MinProxSalida()
        if TPLL <= TPS.T:
            Llegada()
        else:
            Salida(TPS, i)

        if T <= TF:
            continue
        else:
            if TodosTPSHV():
                break
            else:
                TPLL = HV
                continue
        
    print("-----------------")
    Resultados()
    print("-----------------")



def Llegada():
    global T, TPLL, SLL, SLLA, LLF, LLD, CA, CM, CB, C
    global STLLA, STLLO, STLLP 
    global STOA, ITOA, STRO, STRA, STRP
    # PrintColor(AMARILLO, f"{T} llegada")
    T = TPLL
    TPLL = T + ILL()
    SLL += 1

     
    r = Random()
    if r <= PORC_FALSAS:
        LLF += 1
        return
    
    elif r <= (PORC_FALSAS + PORC_DERIVADAS):
        LLD += 1
        return

    SLLA += 1
    r = Random()

    if r <= PORC_ALTA:
        CA += 1
        C = 'A'
    elif r <= PORC_MEDIA:
        CM += 1
        C = 'M'
    else:
        CB += 1
        C = 'B'

    r = Random()

    if r < PORC_AMBULANCIA:
        STLLA += T
        i = AlgunHV(TPSA)
        if i != -1:
            tr = TRA()
            TPSA[i].T = T + tr
            TPSA[i].C = C
            STOA[i] += T-ITOA[i]
            STRA += tr
        else:
            ModifAux(C, 'A', +1)
            
        
    elif r < PORC_POLICIA:
        STLLP += T
        # print(f"stllp < {STLLP}")
        i = AlgunHV(TPSP)
        if i != -1:
            tr = TRP()
            TPSP[i].T = T + tr
            TPSP[i].C = C
            STOP[i] += T-ITOP[i]
            STRP += tr 
            # print(f"L strp < {STRP}")
        else:
            ModifAux(C, 'P', +1)
    else:
        STLLO += T
        i = AlgunHV(TPSO)
        if i != -1:
            tr = TRO()
            TPSO[i].T = T + tr
            TPSO[i].C = C
            STOO[i] += T-ITOO[i]
            STRO += tr 
        else:
            ModifAux(C, 'O', +1)
    
def Salida(TPS, i):
    global T, CA, CM, CB, C, NTA, NTP, NTO
    global CAAP,CAMP,CABP,CAAA,CAMA,CABA,CAAO,CAMO,CABO
    global STRO, STRA, STRP, STSA, STSO, STSP
    # PrintColor(AZUL, f"{T} salida")
    
    T = TPS.T
    
    match TPS.C:
        case 'A': 
            CA -= 1
        case 'M': 
            CM -= 1
        case 'B': 
            CB -= 1
    
    tr = 0
    match TPS.S:
        case 'A':
            # Incrementar contadores al completar el servicio
            STSA += T  # Sumar tiempo de finalización
            NTA += 1   # Contar servicio completado
            
            tr = TRA()
            if CAAA > 0:
                CAAA -=1
                C = 'A'
            elif CAMA > 0:
                CAMA -=1
                C = 'M'
            elif CABA > 0:
                CABA -=1
                C = 'B' 
            else:
                ITOA[i] = T
                TPSA[i].T = HV
                return
            TPSA[i].T = T + tr
            TPSA[i].C = C
            STRA += tr 

        case 'P':
            # Incrementar contadores al completar el servicio
            STSP += T  # Sumar tiempo de finalización
            NTP += 1   # Contar servicio completado
            
            tr = TRP()
            if CAAP > 0:
                CAAP -=1
                C = 'A'
            elif CAMP > 0:
                CAMP -=1
                C = 'M'
            elif CABP > 0:
                CABP -=1
                C = 'B' 
            else:
                ITOP[i] = T
                TPSP[i].T = HV
                return
            TPSP[i].T = T + tr
            TPSP[i].C = C
            STRP += tr 

        case 'O':
            # Incrementar contadores al completar el servicio
            STSO += T  # Sumar tiempo de finalización
            NTO += 1   # Contar servicio completado
            
            tr = TRO()
            if CAAO > 0:
                CAAO -=1
                C = 'A'
            elif CAMO > 0:
                CAMO -=1
                C = 'M'
            elif CABO > 0:
                CABO -=1
                C = 'B' 
            else:
                ITOO[i] = T
                TPSO[i].T = HV
                return
            TPSO[i].T = T + tr
            TPSO[i].C = C
            STRO += tr 
    
def ModifAux(crit, s, add):
    global CAAP,CAMP,CABP,CAAA,CAMA,CABA,CAAO,CAMO,CABO
    match s:
        case 'A': 
            match crit:
                case 'A': 
                    CAAA += add
                case 'M':
                    CAMA += add
                case 'B':
                    CABA += add
        case 'P': 
            match crit:
                case 'A': 
                    CAAP += add
                case 'M':
                    CAMP += add
                case 'B':
                    CABP += add
        case 'O': 
            match crit:
                case 'A': 
                    CAAO += add
                case 'M':
                    CAMO += add
                case 'B':
                    CABO += add
        
def AlgunHV(TPS):
    for index, obj in enumerate(TPS):
        if obj.T == HV:
            return index
    return -1

def TodosTPSHV():
    return all(obj.T == HV for obj in chain(TPSP, TPSA, TPSO))


def ColorLowerBetter(porc):
    if(porc < -0.1 or porc > 100):
        return ROJO
    
    if(porc < 25):
        return CYAN
    elif(porc < 50):
        return VERDE
    elif(porc < 75):
        return AMARILLO
    else:
        return ROJO


def ColorLowerBetterSeconds(sec):
    max = 3600
    if(sec < -0.1 or sec > max):
        return ROJO
    
    if(sec < .25 * max ):
        return CYAN
    elif(sec < .5 * max ):
        return VERDE
    elif(sec < .75 * max):
        return AMARILLO
    else:
        return ROJO

    

def Resultados():
    PrintColor(CYAN, "Resultados")

    PrintColor(VERDE, F"Simulando TF {TF:.2f} segundos (1 año)","\n")
    print("Controles: ",end="")
    print(A, end="")
    PrintColor(VERDE, F" Ambulancias, ", "")
    print(P, end="")
    PrintColor(AMARILLO, F" Patrullas, ", "")
    print(O, end="")
    PrintColor(AZUL, F" Otros ", "\n")
    
    PrintColor(AZUL,"Promedio tiempo ocioso ambulancias ","")
    for i in range(0, A):
        ptoa = (STOA[i] * 100 / T)
        PrintColor(ColorLowerBetter(ptoa), f"{ptoa:.2f}% ", "")
    print("")
    
    PrintColor(AZUL,"Promedio tiempo ocioso patrullas ","")
    for i in range(0, P):
        ptop = (STOP[i] * 100 / T)
        PrintColor(ColorLowerBetter(ptop), f"{ptop:.2f}% ", "")
    print("")

    PrintColor(AZUL,"Promedio tiempo ocioso otros ","")
    for i in range(0, O):
        ptoo = (STOO[i] * 100 / T)
        PrintColor(ColorLowerBetter(ptoo), f"{ptoo:.2f}% ", "")
    print("")
    
    PrintColor(AZUL,"Promedio espera ambulancias ","")
    
    pea = (STSA - STLLA - STRA) / NTA
    peaM = pea / 60
    PrintColor(ColorLowerBetterSeconds(pea), f"{pea:.2f} s | {peaM:.2f} min", "")
    print("")


    PrintColor(AZUL,"Promedio espera patrullas ","")
    pep = (STSP - STLLP - STRP) / NTP
    pepM = pep / 60
    PrintColor(ColorLowerBetterSeconds(pep), f"{pep:.2f} s | {pepM:.2f} min ", "")
    print("")


    PrintColor(AZUL,"Promedio espera otros ","")
    
    peo = (STSO - STLLO - STRO) / NTO
    peoM = peo / 60
    PrintColor(ColorLowerBetterSeconds(peo), f"{peo:.2f} s | {peoM:.2f} min", "")
    print("")

    PrintColor(AZUL,"Promedio llamadas falsas ","")
    pllf = LLF * 100 / SLL
    PrintColor(ColorLowerBetter(pllf), f"{pllf:.2f}% ", "")
    print("")

    PrintColor(AZUL,"Promedio llamadas derivadas ","")
    plld = LLD * 100 / SLL
    PrintColor(ColorLowerBetter(plld), f"{plld:.2f}% ", "")
    print("")

def Init_TPS(default_T=0, default_C=None):
    global P, A, O, TPSP, TPSA, TPSO
    TPSP = [ProxSalida(default_T,'P', default_C) for _ in range(P)]
    TPSA = [ProxSalida(default_T,'A', default_C) for _ in range(A)]
    TPSO = [ProxSalida(default_T,'O', default_C) for _ in range(O)]
    return TPSP, TPSA, TPSO

def Init_STO_ITO():
    global P, A, O, STOA, ITOA, STOP, ITOP, STOO, ITOO
    
    STOP = [0 for _ in range(P)]
    ITOP = [0 for _ in range(P)]
    STOA = [0 for _ in range(A)]
    ITOA = [0 for _ in range(A)]
    STOO = [0 for _ in range(O)]
    ITOO = [0 for _ in range(O)]

def MinProxSalida():
    global TPSP, TPSA, TPSO

    min_obj = None
    min_idx = -1

    # Check TPSP
    for idx, obj in enumerate(TPSP):
        if min_obj is None or obj.T < min_obj.T:
            min_obj, min_idx = obj, idx

    # Check TPSA
    for idx, obj in enumerate(TPSA):
        if min_obj is None or obj.T < min_obj.T:
            min_obj, min_idx = obj, idx

    # Check TPSO
    for idx, obj in enumerate(TPSO):
        if min_obj is None or obj.T < min_obj.T:
            min_obj, min_idx = obj, idx

    return min_obj, min_idx

if __name__ == "__main__":
    
    PrintColor(VERDE, "Iniciando simulacion")
    Init_TPS(default_T=HV, default_C=None)
    Init_STO_ITO()
    
    Simular()


