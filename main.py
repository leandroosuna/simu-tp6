import numpy
from itertools import chain
from scipy.stats import hypsecant
from scipy.stats import gamma

AZUL = '\033[94m'
CYAN = '\033[96m'
BLANCO = '\033[0m'
VERDE = '\033[92m'
AMARILLO = '\033[93m'
ROJO = '\033[91m'
def PrintColor(color, msg, e = '\n'):
    print(f"{color}{msg} {BLANCO}",end=e)

ILLshape = 0.5925
ILLscale = 200.7316
dist_ill = gamma(a=ILLshape, loc=0, scale=ILLscale)

def ILL():
    return dist_ill.rvs()

TRloc = 160.47700477859175
TRscale = 285.0396220949126

def TRA():
    return hypsecant.rvs(TRloc, TRscale)
def TRP():
    return hypsecant.rvs(TRloc, TRscale) 
def TRO():
    return hypsecant.rvs(TRloc, TRscale)

def Random():
    return numpy.random.rand()

class ProxSalida:
    def __init__(self, T,S,C):
        self.T = T
        self.S = S
        self.C = C

#variables de control
P = 10
A = 10
O = 2

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
# TF = 1314000 
TF = 500000

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

def ColorHigherBetter(porc):
    if(porc < -0.1 or porc > 100):
        return ROJO
    
    if(porc < 25):
        return ROJO
    elif(porc < 50):
        return AMARILLO
    elif(porc < 75):
        return VERDE
    else:
        return CYAN

    

def Resultados():
    PrintColor(CYAN, "Resultados")

    PrintColor(VERDE, F"T {T:.2f} ","")
    print(F"CA {CA} CM {CM} CB {CB} SLLA {SLLA} NT {NTA+NTP+NTO} NTA {NTA} NTP {NTP} NTO {NTO}")
    
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
    PrintColor(ColorLowerBetter(pea), f"{pea:.2f}% ", "")
    print("")
    PrintColor(AZUL,"Promedio espera patrullas ","")
    pep = (STSP - STLLP - STRP) / NTP
    PrintColor(ColorLowerBetter(pep), f"{pep:.2f}% ", "")
    print("")


    PrintColor(AZUL,"Promedio espera otros ","")
    
    peo = (STSO - STLLO - STRO) / NTO
    PrintColor(ColorLowerBetter(peo), f"{peo:.2f}% ", "")
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
    # print(TodosTPSHV())   
    # TPSP[0] = ProxSalida(10,'P', 'A')
    # TPSP[1] = ProxSalida(5,'P', 'A')
    # TPSP[2] = ProxSalida(30,'P', 'A')
    
    # TPSA[0] = ProxSalida(12,'P', 'A')
    # TPSA[1] = ProxSalida(7,'P', 'A')
    # TPSA[2] = ProxSalida(9,'P', 'A')
    
    # TPSO[0] = ProxSalida(20,'P', 'A')
    # TPSO[1] = ProxSalida(25,'P', 'A')
    # TPSO[2] = ProxSalida(35,'P', 'A')
    # TPSP = [ProxSalida(4,'P', 'a') for _ in range(P)]

    # i = AlgunHV(TPSP)
    # print(i)
    # print(algunTPSHV(TPSP))
    # tps, ind = MinProxSalida()
    # print(f"{tps.T} {tps.S} {tps.C} at {ind}")   


