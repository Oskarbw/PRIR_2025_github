import numpy as np
import math
import random
import constants

def update_nodes(ENL, U_u, NL, Fu):
    PD = np.size(NL,1)
    NoN= np.size(NL,0)
    
    DOFs = 0
    DOCs = 0
    
    for i in range(0,NoN):
        for j in range(0,PD):
            if ENL[i,PD+j] == 1:
                DOFs += 1
                ENL[i,4*PD+j] = U_u[DOFs-1].item()
            else:
                DOCs += 1
                ENL[i,5*PD+j] = Fu[DOCs-1].item()
    
    return ENL

def assemble_forces(ENL, NL):
    PD = np.size(NL,1) # problem dimension - w ilu wymiarach dzialamy
    NoN = np.size(NL,0)
    DOF = 0
    Fp = []
    
    for i in range(NoN):
        for j in range(PD):
            if ENL[i,PD+j] == 1:
                DOF += 1 # sprawdz pote
                Fp.append(ENL[i,5*PD+j])
                
    Fp = np.vstack([Fp]).reshape(-1,1)
    
    return Fp
                
def assemble_displacements(ENL, NL):
    PD = np.size(NL,1) # problem dimension - w ilu wymiarach dzialamy
    NoN = np.size(NL,0)
    DOC = 0
    Up = []
    
    for i in range(NoN):
        for j in range(PD):
            if ENL[i,PD+j] == -1:
                DOC += 1 # sprawdz pote
                Up.append(ENL[i,4*PD+j])
                
    Up = np.vstack([Up]).reshape(-1,1)
    
    return Up
                            

def assemble_stiffness(ENL,EL,NL,E, diameters, A):
    NoE = np.size(EL,0)
    NPE = np.size(EL,1)
    PD = np.size(NL,1)
    NoN = np.size(NL,0)
    top_chord_diameter = diameters[0]
    bottom_chord_diameter = diameters[1]
    post_diameter = diameters[2]
    diagonal_diameter = diameters[3]

    K = np.zeros([NoN*PD,NoN*PD])
    for i in range(NoE):
        match (i % 4):
            case 0:
                diameter = post_diameter
            case 1:
                diameter = bottom_chord_diameter
            case 2:
                diameter = diagonal_diameter
            case 3:
                diameter = top_chord_diameter
        
        section_area = (diameter/2)**2 * math.pi
        print("seciton area: " + str(section_area*1000000))
        nl = EL[i,0:NPE]
        k = element_stiffness(nl,ENL,E,section_area)
        for r in range(NPE):
            for p in range(PD):
                for q in range(NPE):
                     for s in range(PD):
                        row = ENL[int(nl[r])-1, p+3*PD]
                        column = ENL[int(nl[q])-1, s+3*PD]
                        value = k[r*PD+p, q*PD+s]
                        K[int(row)-1, int(column)-1] = K[int(row)-1,int(column)-1] +value
    return K
                
                

def element_stiffness(nl,ENL,E,A):
    X1 = ENL[int(nl[0])-1,0]
    Y1 = ENL[int(nl[0])-1,1]
    X2 = ENL[int(nl[1])-1,0]
    Y2 = ENL[int(nl[1])-1,1]

    L = math.sqrt((X1-X2)**2+(Y1-Y2)**2)
    print("L WYNOSI: " + str(L))
    C = (X2-X1)/L # cos
    S = (Y2-Y1)/L # sin

    k = (E*A)/L * np.array([[C**2, C*S, -C**2, -C*S],
                            [C*S, S**2, -C*S, -S**2],
                            [-C**2, -C*S, C**2, C*S],
                            [-C*S, -S**2, C*S, S**2]])
    

    
    return k

def assign_BCs(NL, ENL):
    PD = np.size(NL,1)
    NoN= np.size(NL,0)
    
    DOFs = 0
    DOCs = 0
    
    for i in range(0,NoN):
        for j in range(0,PD):
            if ENL[i,PD+j] == -1:
                DOCs -= 1
                ENL[i,2*PD+j] = DOCs
            else:
                DOFs += 1
                ENL[i,2*PD+j] = DOFs
    
    for i in range(0,NoN):
        for j in range(0,PD):
            if ENL[i,2*PD+j] < 0:
                ENL[i,3*PD+j] = abs(ENL[i,2*PD+j]) + DOFs
            else:
                ENL[i,3*PD+j] = abs(ENL[i,2*PD+j])
                
    DOCs = abs(DOCs)
    
    return (ENL, DOFs, DOCs)

def assemble_force_in_elements(ENL, EL, NL, E, sigma_d):
    num_elements = np.size(EL,0)
    NPE = np.size(EL,1)
    PD = 2
    F_elem = []
    sigma_d = 355e6 # MPa, stal S335
    youngs_modulus = 210e9 # GPa, stały dla prawie każdej stali    
    max_pressure = 0
    for element in EL:
        # oblicz długość przed
        x1 = NL[int(element[0])-1, 0]
        y1 = NL[int(element[0])-1, 1]
        x2 = NL[int(element[1])-1, 0]
        y2 = NL[int(element[1])-1, 1]
        
        L = math.sqrt((x1-x2)**2+(y1-y2)**2)
        
        # długość po
        x1_p = x1 + ENL[int(element[0])-1, PD*4]
        y1_p = y1 + ENL[int(element[0])-1, PD*4+1]
        x2_p = x2 + ENL[int(element[1])-1, PD*4]
        y2_p = y2 + ENL[int(element[1])-1, PD*4+1]
        
        L_p = math.sqrt((x1_p-x2_p)**2+(y1_p-y2_p)**2)
        print("L_p wynosi:" + str(L_p))
        # oblicz odkształcenie    
        pressure_in_element = E * abs(L_p-L) / L
        if pressure_in_element > max_pressure:
            max_pressure = pressure_in_element
        # czy wytrzyma
        if pressure_in_element <= sigma_d:
            F_elem.append(True)
        else:
            F_elem.append(False)
            
    return F_elem, max_pressure

def define_nodes(length, height,segments):
    # Środek układu współrzędnych jest w lewym dolnym węźle
    # Jest to też pierwszy węzeł w kolejności
    # Drugim węzłem jest ten nad nim
    # Trzecim jest węzeł po prawo od pierwszego
    # I tak dalej
    
    num_nodes = segments*2 + 2
    problem_dimension = 2
    NL = np.zeros((num_nodes, problem_dimension))
    for i in range(0, num_nodes, 2):
        bottom_node = [length/segments/2*i, 0]
        top_node = [length/segments/2*i, height]
        NL[i] = bottom_node
        NL[i+1] = top_node
    return NL

def define_elements(segments):
    
    num_elements = segments*4 + 1
    num_nodes = segments*2 + 2
    problem_dimension = 2
    EL = np.zeros((num_elements, problem_dimension))
    for i in range(1, num_elements, 4):
        pivot_node = int(i/2 + 1)
        post = [pivot_node, pivot_node+1]
        bottom = [pivot_node, pivot_node+2]
        diagonal = [pivot_node, pivot_node+3]
        top = [pivot_node+1, pivot_node+3]
        EL[i-1] = post
        EL[i] = bottom
        EL[i+1] = diagonal
        EL[i+2] = top
    right_far_post = [num_nodes - 1 , num_nodes]
    EL[num_elements - 1] = right_far_post
    
    return EL

def define_DorN(segments):
    num_nodes = segments*2 + 2
    problem_dimension = 2
    DorN = np.zeros((num_nodes, problem_dimension))
    for i in range(1, num_nodes+1):
        if i == 1:
            restricted_movement_in_both_axis = [-1, -1]
            DorN[i-1] = restricted_movement_in_both_axis
        elif i == num_nodes - 1:
            restricted_movement_in_y_axis = [1, -1]
            DorN[i-1] = restricted_movement_in_y_axis
        else:
            allowed_movement_in_both_axis = [1, 1]
            DorN[i-1] = allowed_movement_in_both_axis
            
    return DorN
            
def define_initial_forces(segments, force_in_middle):
    num_nodes = segments*2 + 2
    problem_dimension = 2
    Fu = np.zeros((num_nodes, problem_dimension))
    is_segments_even = segments % 2 == 0
    for i in range(1, num_nodes+1):
        if i == num_nodes/2 + 1 and is_segments_even:
            force_in_node = [0, -force_in_middle]
        elif i in (num_nodes/2,num_nodes/2 + 2) and not is_segments_even:
            force_in_node = [0, -force_in_middle/2]
        else:
            force_in_node = [0, 0]
        Fu[i-1] = (force_in_node)
    return Fu
    
def define_initial_displacements(segments):
    num_nodes = segments*2 + 2
    problem_dimension = 2 # problem dimension wrzucić do stałych
    U_u = np.zeros((num_nodes, problem_dimension))
    
    return U_u

def define_bridge_structure(length, height, segments, force):
    NL = define_nodes(length, height,segments)
    EL = define_elements(segments)
    DorN = define_DorN(segments)
    Fu = define_initial_forces(segments, force)
    U_u = define_initial_displacements(segments)
    return (NL, EL, DorN, Fu, U_u)


def main():
    top_chord_diameter = 8e-2
    bottom_chord_diameter = 9e-2
    post_diameter = 9e-2
    diagonal_diameter = 5e-2

    length = 20
    height = 5
    segments = 5
    diameters = [top_chord_diameter,
                 bottom_chord_diameter,
                 post_diameter,
                 diagonal_diameter]
    force = 200000 # 2 000 000 N = 200 ton
    
    

    NL = np.array([[0,0],
            [1,0],
            [0.5,1]])

    EL = np.array([[1,2],
                [2,3],
                [3,1]])
    # ograniczenia w ruchu w osiach dla wezlow
    # 1 ruch dozwolony -1 uniemozliwiony
    DorN =  np.array([[-1,-1],
                    [1,-1],
                    [1,1]])

    # siły dla każdego węzła w każdej z osi
    Fu = np.array([[0,0],
                [0,0],
                [0,-20]])

    U_u = np.array([[0,0],
                [0,0],
                [0,0]])

    
    (NL, EL, DorN, Fu, U_u) = define_bridge_structure(length, height, segments, force)

    print("NL:")
    print(NL)
    print("EL:")
    print(EL)

    E = 210e9

    # A = 1e-1 # 35 cm średnicy
    # A = 1e-2 # 11 cm średnicy
    A = 4e-3 # 8 cm
    # A = 1e-3 # 3,5 cm 
    # A = 1e-4 # 1 cm
    # A = 1e-5 # 3mm średnicy

    PD = np.size(NL,1) # problem dimension - w ilu wymiarach dzialamy
    NoN = np.size(NL,0)

    ENL = np.zeros([NoN,6*PD])

    ENL[:,0:PD] = NL[:,:]
    ENL[:,PD:2*PD] = DorN[:,:]

    (ENL, DOFs, DOCs) = assign_BCs(NL,ENL) # dodaj warunki brzegowe
    #dof deegres of freedon
    # doc deegres of constraint

    K = assemble_stiffness(ENL,EL,NL,E,diameters, A)

    ENL[:,4*PD:5*PD] = U_u[:,:]
    ENL[:,5*PD:6*PD] = Fu[:,:]
    print("W SRODKU")
    print(ENL)
    U_u = U_u.flatten()
    Fu = Fu.flatten()

    Fp = assemble_forces(ENL, NL)
    Up = assemble_displacements(ENL, NL)


    K_UU = K[0:DOFs, 0:DOFs]
    K_UP = K[0:DOFs, DOFs:DOFs+DOCs]
    K_PU = K[DOFs:DOFs+DOCs, 0:DOFs]
    K_PP = K[DOFs:DOFs+DOCs, DOFs:DOFs+DOCs]

    F = Fp - np.matmul(K_UP,Up)
    U_u = np.matmul(np.linalg.inv(K_UU),F)
    print("U_u wynosi:" + str(U_u))
    Fu = np.matmul(K_PU, U_u) + np.matmul(K_PP,Up)

    ENL = update_nodes(ENL, U_u, NL, Fu)
    print("potem")
    for row in ENL:
        print(row)

    sigma_d = 355e6 
    F_elem, max_pressure = assemble_force_in_elements(ENL, EL, NL, E, sigma_d)
    print("Czy kolejne pręty wytrzymają:")
    print(F_elem)
    print("Max_pressure: " + str(max_pressure/1e6))

if __name__ == "__main__":
    main()