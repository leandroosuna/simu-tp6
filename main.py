import numpy
from itertools import chain

ROJO = '\033[91m'
VERDE = '\033[92m'
AMARILLO = '\033[93m'
AZUL = '\033[94m'
BLANCO = '\033[0m'

def PrintColor(color, msg):
    print(f"{color}{msg} {BLANCO}")

def ILL():
    return numpy.random.uniform(0, 10)
def TRA():
    return numpy.random.uniform(10, 20)
def TRP():
    return numpy.random.uniform(10, 20)
def TRO():
    return numpy.random.uniform(10, 20)

def Random():
    return numpy.random.rand()

class ProxSalida:
    def __init__(self, T,S,C):
        self.T = T
        self.S = S
        self.C = C

#variables de control
P = 20
A = 10
O = 5

#variables de resultado

#variables de estado
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
TF = 3600

HV = 9999999999999999
TPLL = 0

def Simular():
    global T, TF, TPLL

    while True:
        TPS,i = MinProxSalida()
        if TPLL <= TPS.T:
            Llegada()
        else:
            Salida(TPS, i)

        if T <= TF:
            continue
        else:
            break
            # if TodosTPSHV():
            #     break
            # else:
            #     TPLL = HV
            #     continue
        

    Resultados()

SLL = 0
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

def Llegada():
    global T, TPLL, SLL, LLF, LLD, CA, CM, CB, C
    global STLLA, STLLO, STLLP
    global STOA, ITOA
    PrintColor(AMARILLO, f"{T} llegada")
    T = TPLL
    TPLL = T + ILL()
    SLL += 1

    if Random() <= PORC_FALSAS:
        LLF += 1
        return

    if Random() <= PORC_DERIVADAS:
        LLD += 1
        return

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
        else:
            ModifAux(C, 'A', +1)
            
        
    elif r < PORC_POLICIA:
        STLLP += T
        i = AlgunHV(TPSP)
        if i != -1:
            tr = TRP()
            TPSP[i].T = T + tr
            TPSP[i].C = C
            STOP[i] += T-ITOP[i]
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
        else:
            ModifAux(C, 'P', +1)
    
def Salida(TPS, i):
    # print(f"{TPS.T} {TPS.S} {TPS.C}")
    global T, CA, CM, CB, C 
    global CAAP,CAMP,CABP,CAAA,CAMA,CABA,CAAO,CAMO,CABO
    PrintColor(AZUL, f"{T} salida")
    
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
            tr = TRA()
            if CAAA > 0:
                CAAA -=1
                C = 'A'
            elif CAMA > 0:
                CANA -=1
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
            # STR += T
        
        case 'P':
            tr = TRP()
            if CAAP > 0:
                CAAP -=1
                C = 'A'
            elif CAMP > 0:
                CANP -=1
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
            # STR += T
        
        case 'O':
            tr = TRO()
            if CAAO > 0:
                CAAO -=1
                C = 'A'
            elif CAMO > 0:
                CANO -=1
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
            # STR += T
        
        



    return
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

def Resultados():
    PrintColor(VERDE, "Resultados")

    print(F"T {T} CA {CA} CM {CM} CB {CB}")
    print("PTOP ",end ="")
    for i in range(0, P):
        print(f"{(STOP[i] * 100 / T):.2f}% ", end="")
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


