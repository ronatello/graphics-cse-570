''' read the file line by line to understanding how the half edge load 
an off file and to save the half edge mesh as an obj file.

author:
    zhangsihao yang
'''
print ('hello')

data_path = 'tests/data/brain.off'
data_path1 = 'cube_1.off'

import mesh
from mesh import Vertex
import math

# HalfedgeMesh
mesh = mesh.HalfedgeMesh(data_path)

# Returns a list of Vertex type (in order of file)--similarly for halfedges,
# and facet
mesh.vertices

# The number of facets in the mesh
print(len(mesh.facets))

# Get the 10th halfedge
mesh.halfedges[10]

# Get the halfedge that starts at vertex 25 and ends at vertex 50
# mesh.get_halfedge(0, 1)

print(mesh.vertices)
for vertex in mesh.vertices:
    print(vertex.get_vertex())

print(mesh.facets)
print('--------------------')
for face in mesh.facets:
    pass
    # print(face.a, face.b, face.c)

updated_vertices_list = {}
new_vertices_list = {}

def new_odd_vertex_calc(he):

    if (new_vertices_list.get(he.index)):
        return None
    elif (he.opposite and new_vertices_list.get(he.opposite.index)):
        return None

    vx = 0
    vy = 0
    vz = 0

    if he.opposite:
        vx = 3/8 * (he.vertex.get_vertex()[0]) + 3/8 * (he.opposite.vertex.get_vertex()[0]) + 1/8 * (he.next.vertex.get_vertex()[0]) + 1/8 * (he.opposite.next.vertex.get_vertex()[0])
        vy = 3/8 * (he.vertex.get_vertex()[1]) + 3/8 * (he.opposite.vertex.get_vertex()[1]) + 1/8 * (he.next.vertex.get_vertex()[1]) + 1/8 * (he.opposite.next.vertex.get_vertex()[1])
        vz = 3/8 * (he.vertex.get_vertex()[2]) + 3/8 * (he.opposite.vertex.get_vertex()[2]) + 1/8 * (he.next.vertex.get_vertex()[2]) + 1/8 * (he.opposite.next.vertex.get_vertex()[2])
    
    else:
        vx = 1/2 * (he.vertex.get_vertex()[0]) + 1/2 * (he.prev.vertex.get_vertex()[0])
        vy = 1/2 * (he.vertex.get_vertex()[1]) + 1/2 * (he.prev.vertex.get_vertex()[1])
        vz = 1/2 * (he.vertex.get_vertex()[2]) + 1/2 * (he.prev.vertex.get_vertex()[2])

    #return Vertex(vx, vy, vz)
    return [vx, vy, vz]

def is_boundary(he):
    return False if he.opposite else True

def one_ring_even_calc(he):

    if (updated_vertices_list.get(he.vertex.index)):
        return None
    
    vx = 0
    vy = 0
    vz = 0

    head = he

    next_b_edge = he
    prev_b_edge = he.next

    interior_flag = False
    adjacent_vertices = []

    vertex_sums = he.vertex.get_vertex()

    while next_b_edge.opposite:
        #print(next_b_edge.opposite.vertex.get_vertex())
        adjacent_vertices.append(next_b_edge.opposite.vertex.get_vertex())
        next_b_edge = next_b_edge.opposite.prev
        if (next_b_edge == head):
            interior_flag = True
            break

    #print(adjacent_vertices)

    if (not interior_flag):
        adjacent_vertices = []
        
        next_b_edge = next_b_edge.prev
        adjacent_vertices.append(next_b_edge.vertex.get_vertex())

        while prev_b_edge.opposite:
            prev_b_edge = prev_b_edge.opposite.next

        adjacent_vertices.append(prev_b_edge.vertex.get_vertex())

        vertex_sums = [sum(val) for val in zip(*adjacent_vertices)]

        vx = 3/4 * he.vertex.get_vertex()[0] + 1/8 * vertex_sums[0]
        vy = 3/4 * he.vertex.get_vertex()[1] + 1/8 * vertex_sums[1]
        vz = 3/4 * he.vertex.get_vertex()[2] + 1/8 * vertex_sums[2]

        #return Vertex(vx, vy, vz)
        return [vx, vy, vz]

    else:
        n = len(adjacent_vertices)
        # Can set condition for n <= 3 but on ignoring, output looks nicer when beta is calculated fully, especially on cube
        if (n <= 3):
            beta = 3/16
        else:
            beta = ((5/8 - ((3/8 + (1/4 * math.cos(2 * math.pi / n))) ** 2))) / n

        vertex_sums = [sum(val) for val in zip(*adjacent_vertices)]

        # print(n)
        # print(vertex_sums)
        vx = (1 - (n * beta)) * he.vertex.get_vertex()[0] + (beta * vertex_sums[0])
        vy = (1 - (n * beta)) * he.vertex.get_vertex()[1] + (beta * vertex_sums[1])
        vz = (1 - (n * beta)) * he.vertex.get_vertex()[2] + (beta * vertex_sums[2])

        #return Vertex(vx, vy, vz)
        return [vx, vy, vz]

def new_vertices(mesh):
    vertex_new_indices = len(mesh.vertices)
    face = mesh.facets[9]
    #print("FACE: ", face.index, face.a, face.b, face.c)
    #print("HALFEDGE: ", face.halfedge.index, face.halfedge.vertex.get_vertex())
    for face in mesh.facets:
        new_v1 = one_ring_even_calc(face.halfedge)
        new_v2 = one_ring_even_calc(face.halfedge.next)
        new_v3 = one_ring_even_calc(face.halfedge.prev)

        new_v4 = new_odd_vertex_calc(face.halfedge)
        new_v5 = new_odd_vertex_calc(face.halfedge.next)
        new_v6 = new_odd_vertex_calc(face.halfedge.prev)

        if (new_v1 is not None):
            updated_vertices_list.update({face.halfedge.vertex.index: new_v1})
        if (new_v2 is not None):
            updated_vertices_list.update({face.halfedge.next.vertex.index: new_v2})
        if (new_v3 is not None):
            updated_vertices_list.update({face.halfedge.prev.vertex.index: new_v3})


        if (new_v4 is not None):
            new_vertices_list.update({face.halfedge.index: vertex_new_indices})
            updated_vertices_list.update({vertex_new_indices: new_v4})
            vertex_new_indices += 1
        if (new_v5 is not None):
            new_vertices_list.update({face.halfedge.next.index: vertex_new_indices})
            updated_vertices_list.update({vertex_new_indices: new_v5})
            vertex_new_indices += 1
        if (new_v6 is not None):
            new_vertices_list.update({face.halfedge.prev.index: vertex_new_indices})
            updated_vertices_list.update({vertex_new_indices: new_v6})
            vertex_new_indices += 1

    # print(new_v2)
    # print(new_v3)
    # print(new_v4)
    # print(new_v5)
    # print(new_v6)

new_faces_list = []

def outer_faces(he):
    v1 = he.vertex.index
    v2 = []
    v3 = []

    if he.next.index in new_vertices_list:
        v2 = new_vertices_list[he.next.index]
    else:
        v2 = new_vertices_list[he.next.opposite.index]

    if he.index in new_vertices_list:
        v3 = new_vertices_list[he.index]
    else:
        v3 = new_vertices_list[he.opposite.index]

    return [v1, v2, v3]

def new_faces(mesh):
    for face in mesh.facets:
        
        face1 = outer_faces(face.halfedge)
        face2 = outer_faces(face.halfedge.next)
        face3 = outer_faces(face.halfedge.prev)

        f4_v1 = []
        f4_v2 = []
        f4_v3 = []

        if face.halfedge.index in new_vertices_list:
            f4_v1 = new_vertices_list[face.halfedge.index]
        else:
            f4_v1 = new_vertices_list[face.halfedge.opposite.index]

        if face.halfedge.next.index in new_vertices_list:
            f4_v2 = new_vertices_list[face.halfedge.next.index]
        else:
            f4_v2 = new_vertices_list[face.halfedge.next.opposite.index]

        if face.halfedge.prev.index in new_vertices_list:
            f4_v3 = new_vertices_list[face.halfedge.prev.index]
        else:
            f4_v3 = new_vertices_list[face.halfedge.prev.opposite.index]
            
        face4 = [f4_v1, f4_v2, f4_v3]

        new_faces_list.append(face1)
        new_faces_list.append(face2)
        new_faces_list.append(face3)
        new_faces_list.append(face4)

#odd_vertices(mesh)
#print(New_Faces)
#even_vertices(mesh)
# print(New_Faces)

new_vertices(mesh)
new_faces(mesh)
#print(updated_vertices_list)
#print()
#print(new_faces_list)

#print()
#print(updated_vertices_list.keys())
#print(max(updated_vertices_list.keys()))

# to save the halfedge mesh you will need to following function.
def save_halfmesh_as_obj(mesh, file_name):
    with open(file_name, 'w') as open_file:
        for vertex in mesh.vertices:
            lv = vertex.get_vertex()
            open_file.write("v {} {} {} \n".format(lv[0], lv[1], lv[2]))

        for face in mesh.facets:
            open_file.write("f {} {} {}\n".format(face.a+1, face.b+1, face.c+1))

def custom_save_halfmesh_as_obj(file_name):
    with open(file_name, 'w') as open_file:
        for i in range(0, max(updated_vertices_list.keys()) + 1):
            # print(i)
            # print(new_vertices_list[i])
            open_file.write("v {} {} {} \n".format(updated_vertices_list[i][0], updated_vertices_list[i][1], updated_vertices_list[i][2]))

        for face in new_faces_list:
            open_file.write("f {} {} {}\n".format(face[0]+1, face[1]+1, face[2]+1))

def custom_save_halfmesh_as_off(file_name):
    with open(file_name, 'w') as open_file:
        open_file.write('OFF\n')
        open_file.write(str(len(updated_vertices_list)) + " " + str(len(new_faces_list)) + " 0" + "\n")
        for i in range(0, max(updated_vertices_list.keys()) + 1):
            # print(i)
            # print(new_vertices_list[i])
            open_file.write("{} {} {} \n".format(updated_vertices_list[i][0], updated_vertices_list[i][1], updated_vertices_list[i][2]))

        for face in new_faces_list:
            open_file.write("3 {} {} {}\n".format(face[0], face[1], face[2]))

custom_save_halfmesh_as_off('brain_1.off')

