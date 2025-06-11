import numpy as np
import math
import random
import constants
class Strength:
    def __init__(self, bridge_template, force):
        self.segments = bridge_template.segments
        self.bridge_length = bridge_template.length
        self.diameters = bridge_template.diameters
        self.force = force

    def _assemble_displacements(self, dirichlet_neumann, displacements):
        num_nodes = np.size(dirichlet_neumann,0)
        displacements_assembled = []
        
        for i in range(num_nodes):
            for j in range(constants.PROBLEM_DIMENSION):
                if dirichlet_neumann[i,j] == -1:
                    displacements_assembled.append(displacements[i,j])
                    
        displacements_assembled = np.vstack([displacements_assembled]).reshape(-1,1)
        return displacements_assembled

    def _assemble_forces(self, dirichlet_neumann, forces):
        num_nodes = np.size(dirichlet_neumann,0)
        forces_assembled = []
        
        for i in range(num_nodes):
            for j in range(constants.PROBLEM_DIMENSION):
                if dirichlet_neumann[i,j] == 1:
                    forces_assembled.append(forces[i,j])
                    
        forces_assembled = np.vstack([forces_assembled]).reshape(-1,1)
        return forces_assembled

    def _order_results(self, dirichlet_neumann, final_displacements_unordered, nodes, final_forces_unordered):
        num_nodes= np.size(nodes,0)
        
        deegres_of_freedom = 0
        deegres_of_constraint = 0
        final_forces_in_order = np.zeros((num_nodes, constants.PROBLEM_DIMENSION))   
        final_displacements_in_order = np.zeros((num_nodes, constants.PROBLEM_DIMENSION))        

        for i in range(0,num_nodes):
            for j in range(0, constants.PROBLEM_DIMENSION):
                if dirichlet_neumann[i,j] == 1:
                    deegres_of_freedom += 1
                    final_displacements_in_order[i,j] = final_displacements_unordered[deegres_of_freedom-1].item()
                else:
                    deegres_of_constraint += 1
                    final_forces_in_order[i,j] = final_forces_unordered[deegres_of_constraint-1].item()
        
        return final_displacements_in_order, final_forces_in_order                     

    def _assemble_stiffness_matrix(self, node_deegres_of_freedom_global ,elements,nodes, diameters):
        num_elements = np.size(elements,0)
        num_nodes = np.size(nodes,0)
        top_chord_diameter = diameters[0] * constants.MM_TO_M
        bottom_chord_diameter = diameters[1] * constants.MM_TO_M
        post_diameter = diameters[2] * constants.MM_TO_M
        diagonal_diameter = diameters[3] * constants.MM_TO_M

        K = np.zeros([num_nodes*constants.PROBLEM_DIMENSION, num_nodes*constants.PROBLEM_DIMENSION])
        
        for i in range(num_elements):
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
            # print("seciton area: " + str(section_area*1000000))
            element_nodes = elements[i,0:constants.NODES_PER_ELEMENT]
            k = self._element_stiffness(element_nodes,nodes,section_area)
            
            for p in range(constants.NODES_PER_ELEMENT):
                for q in range(constants.PROBLEM_DIMENSION):
                    for r in range(constants.NODES_PER_ELEMENT):
                        for s in range(constants.PROBLEM_DIMENSION):
                            row = node_deegres_of_freedom_global[int(element_nodes[p])-1, q]
                            column = node_deegres_of_freedom_global[int(element_nodes[r])-1, s]
                            value = k[p*constants.PROBLEM_DIMENSION+q, r*constants.PROBLEM_DIMENSION+s]
                            K[int(row)-1, int(column)-1] = K[int(row)-1,int(column)-1] +value
        return K
                    
    def _element_stiffness(self, element_nodes,nodes,A):
        X1 = nodes[int(element_nodes[0])-1,0]
        Y1 = nodes[int(element_nodes[0])-1,1]
        X2 = nodes[int(element_nodes[1])-1,0]
        Y2 = nodes[int(element_nodes[1])-1,1]

        L = math.sqrt((X1-X2)**2+(Y1-Y2)**2)
        #print("L WYNOSI: " + str(L))
        C = (X2-X1)/L # cos
        S = (Y2-Y1)/L # sin

        k = (constants.YOUNGS_MODULUS*A)/L * np.array([[C**2, C*S, -C**2, -C*S],
                                                       [C*S, S**2, -C*S, -S**2],
                                                       [-C**2, -C*S, C**2, C*S],
                                                       [-C*S, -S**2, C*S, S**2]])
        
        return k

    def _assign_boundary_conditions(self, nodes, dirichlet_neumann):
        num_nodes = np.size(nodes, 0)
        
        node_deegres_of_freedom_local  = np.zeros((num_nodes, constants.PROBLEM_DIMENSION))
        node_deegres_of_freedom_global = np.zeros((num_nodes, constants.PROBLEM_DIMENSION))

        deegres_of_freedom = 0
        deegres_of_constraint = 0
        
        for i in range(0, num_nodes):
            for j in range(0, constants.PROBLEM_DIMENSION):
                if dirichlet_neumann[i,j] == -1:
                    deegres_of_constraint -= 1
                    node_deegres_of_freedom_local[i,j] = deegres_of_constraint
                else:
                    deegres_of_freedom += 1
                    node_deegres_of_freedom_local[i,j] = deegres_of_freedom
        
        for i in range(0, num_nodes):
            for j in range(0, constants.PROBLEM_DIMENSION):
                if node_deegres_of_freedom_local[i,j] < 0:
                    node_deegres_of_freedom_global[i,j] = abs(node_deegres_of_freedom_local[i,j]) + deegres_of_freedom
                else:
                    node_deegres_of_freedom_global[i,j] = abs(node_deegres_of_freedom_local[i,j])
                    
        deegres_of_constraint = abs(deegres_of_constraint)
        
        return (node_deegres_of_freedom_global, deegres_of_freedom, deegres_of_constraint)

    def _calculate_highest_stress(self, displacements, elements, nodes):  
        highest_stress = 0
        for element in elements:
            # Długość przed przemieszczeniem
            x1 = nodes[int(element[0])-1, 0]
            y1 = nodes[int(element[0])-1, 1]
            x2 = nodes[int(element[1])-1, 0]
            y2 = nodes[int(element[1])-1, 1]
            
            L = math.sqrt((x1-x2)**2+(y1-y2)**2)
            
            # Długość po przemieszczeniu
            x1_p = x1 + displacements[int(element[0])-1, 0]
            y1_p = y1 + displacements[int(element[0])-1, 1]
            x2_p = x2 + displacements[int(element[1])-1, 0]
            y2_p = y2 + displacements[int(element[1])-1, 1]
            
            L_p = math.sqrt((x1_p-x2_p)**2+(y1_p-y2_p)**2)
            # print("L_p wynosi:" + str(L_p))
            # oblicz odkształcenie    
            element_stress = constants.YOUNGS_MODULUS * abs(L_p-L) / L
            if element_stress > highest_stress:
                highest_stress = element_stress

        return highest_stress

    def _define_nodes(self, length, height,segments):
        # Środek układu współrzędnych jest w lewym dolnym węźle
        num_nodes = segments*constants.NODES_PER_SEGMENT + 2
        nodes = np.zeros((num_nodes, constants.PROBLEM_DIMENSION))
        for i in range(0, num_nodes, 2):
            bottom_node = [length/segments/2*i, 0]
            top_node = [length/segments/2*i, height]
            nodes[i] = bottom_node
            nodes[i+1] = top_node
        return nodes

    def _define_elements(self, segments):
        num_elements = segments*constants.ELEMENTS_PER_SEGMENT + 1
        num_nodes = segments*constants.NODES_PER_SEGMENT + 2
        elements = np.zeros((num_elements, constants.PROBLEM_DIMENSION))
        for i in range(1, num_elements, constants.ELEMENTS_PER_SEGMENT):
            pivot_node = int(i/constants.NODES_PER_SEGMENT + 1)
            post = [pivot_node, pivot_node+1]
            bottom = [pivot_node, pivot_node+2]
            diagonal = [pivot_node, pivot_node+3]
            top = [pivot_node+1, pivot_node+3]
            elements[i-1] = post
            elements[i] = bottom
            elements[i+1] = diagonal
            elements[i+2] = top
        right_far_post = [num_nodes - 1 , num_nodes]
        elements[num_elements - 1] = right_far_post
        
        return elements

    def _define_dirichlet_neumann(self, segments):
        num_nodes = segments*constants.NODES_PER_SEGMENT + 2
        dirichlet_neumann = np.zeros((num_nodes, constants.PROBLEM_DIMENSION))
        for i in range(1, num_nodes+1):
            if i == 1:
                restricted_movement_in_both_axis = [-1, -1]
                dirichlet_neumann[i-1] = restricted_movement_in_both_axis
            elif i == num_nodes - 1:
                restricted_movement_in_y_axis = [1, -1]
                dirichlet_neumann[i-1] = restricted_movement_in_y_axis
            else:
                allowed_movement_in_both_axis = [1, 1]
                dirichlet_neumann[i-1] = allowed_movement_in_both_axis
                
        return dirichlet_neumann
                
    def _define_initial_forces(self, segments):
        num_nodes = segments*constants.NODES_PER_SEGMENT + 2
        initial_forces = np.zeros((num_nodes, constants.PROBLEM_DIMENSION))
        is_segments_even = segments % 2 == 0
        for i in range(1, num_nodes+1):
            if i == num_nodes/2 + 1 and is_segments_even:
                force_in_node = [0, -self.force]
            elif i in (num_nodes/2, num_nodes/2 + constants.NODES_PER_SEGMENT) and not is_segments_even: # W przypadku nieparzystej l segmentów siłę dzielimy po równo dla 2 środkowych węzłów
                force_in_node = [0, -self.force/2] 
            else:
                force_in_node = [0, 0]
            initial_forces[i-1] = (force_in_node)
        return initial_forces
        
    def _define_initial_displacements(self, segments):
        num_nodes = segments*constants.NODES_PER_SEGMENT + 2
        initial_displacements = np.zeros((num_nodes, constants.PROBLEM_DIMENSION))
        
        return initial_displacements

    def _define_bridge_structure(self, length, height, segments):
        nodes = self._define_nodes(length, height,segments)
        elements = self._define_elements(segments)
        dirichlet_neumann = self._define_dirichlet_neumann(segments)
        initial_forces = self._define_initial_forces(segments)
        initial_displacements = self._define_initial_displacements(segments)
        return (nodes, elements, dirichlet_neumann, initial_forces, initial_displacements)

    def stress_overload(self, diameters):        
        (nodes,
        elements,
        dirichlet_neumann,
        initial_forces,
        initial_displacements) = self._define_bridge_structure(self.bridge_length, constants.BRIDGE_HEIGHT, self.segments)

        (node_deegres_of_freedom_global,
        deegres_of_freedom,
        deegres_of_constraint) = self._assign_boundary_conditions(nodes, dirichlet_neumann) # dodaj warunki brzegowe

        K = self._assemble_stiffness_matrix(node_deegres_of_freedom_global,elements,nodes,diameters)

        initial_displacements_vector = self._assemble_displacements(dirichlet_neumann,initial_displacements)
        initial_forces_vector = self._assemble_forces(dirichlet_neumann, initial_forces)

        dof = deegres_of_freedom
        doc = deegres_of_constraint

        K_UU = K[0:dof, 0:dof]
        K_UP = K[0:dof, dof:dof+doc]
        K_PU = K[dof:dof+doc, 0:dof]
        K_PP = K[dof:dof+doc, dof:dof+doc]

        intermediate_matrix = initial_forces_vector - np.matmul(K_UP,initial_displacements_vector)
        final_displacements_unordered = np.matmul(np.linalg.inv(K_UU),intermediate_matrix)
        final_forces_unordered = np.matmul(K_PU, final_displacements_unordered) + np.matmul(K_PP,initial_displacements_vector)

        (final_displacements, final_forces) = self._order_results(dirichlet_neumann, final_displacements_unordered, nodes, final_forces_unordered)
 
        highest_stress = self._calculate_highest_stress(final_displacements, elements, nodes)
        if highest_stress > constants.ELASTIC_LIMIT_OF_STEEL:
            stress_overload = highest_stress - constants.ELASTIC_LIMIT_OF_STEEL
        else:
            stress_overload = None
        # print("Max_pressure: " + str(highest_stress/1e6))
        
        return stress_overload

