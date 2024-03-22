# summon librarys
import json
import bpy
from mathutils import Vector
from bpy_extras.object_utils import AddObjectHelper, object_data_add
import random

# JSON file
file_name = "JSON File Path Here"

f = open(file_name, "r", encoding="utf8")
 
# Reading from file
data = json.loads(f.read())
cells = data['pack']['cells']
 
 
# Closing file
f.close()

# Create materials for each biome
for x in data['biomesData']['i']:
    # name for the biome
    biomeName = data['biomesData']['name'][x]
    new_mat = bpy.data.materials.new(biomeName)
    #convert hex to rgb, add 1 as fourth digit for full opacity
    h = data['biomesData']['color'][x].lstrip('#')
    diffColor = [int(h[i:i+2], 16) for i in (0, 2, 4)]
    diffColor = [(i/255) for i in diffColor]
    diffColor.append(1)
    # setting the diffuse color to the material
    bpy.data.materials[biomeName].diffuse_color = tuple(diffColor)
    #bpy.context.object.active_material.diffuse_color = (18.4789, 14.8636, 40.4601, 1)

# scaling for height manually at the moment
hScale = .25

# For testing, just generate a few cells in the middle. Hope its not ocean :)
# For edges, when an empty iterable is passed in, the edges are inferred from the polygons.

for x in range(1000, 3000):
    thisCell = cells[x]
    verticesCount = len(thisCell['v'])
    cellName = "cell" + str(x)
    # List of vertex coordinates
    polyVertices = []
    # ids of vertices added
    vertList = []
    # list of faces, references index of vertices in polyVertices
    polyFaces = []
    # Add each pair of vertices to the list of vetices.
    # Add the cell center into the vertex lists - all vertices will make triangles with neighbors and the center
    # the cell center has no ID
    cellCenter = [thisCell['p'][0],thisCell['p'][1],(thisCell['h']*hScale)]
    polyVertices.append(cellCenter)
    vertList.append(-1)
    for n in range(0, verticesCount):
        vertID = thisCell['v'][n]
        vertex = data['pack']['vertices'][vertID]
        connectedVertices = vertex['v']
        vertPosition = vertex['p']
        vertHeight = 0
        # The height of the vertex is the average of the cells it touches
        for neighborCell in vertex['c']:
            if neighborCell < len(data['pack']['cells']):
                vertHeight = vertHeight + data['pack']['cells'][neighborCell]['h']
        vertHeight = vertHeight/len(vertex['c'])
        # Check if connected vertices are in the list yet. build a face with any that are
        # Ignore -1 vertex id
        # Faces are vertex, neighbor, center
        for neighborVert in connectedVertices:
            if neighborVert in vertList and not neighborVert == -1:
                # This vertex will be in n+1 position in the polyVertices list
                polyFace = [(n+1), vertList.index(neighborVert),0]
                polyFaces.append(polyFace)
        vertList.append(vertID)
        vert = Vector((vertPosition[0], vertPosition[1], (vertHeight*hScale)))
        polyVertices.append(vert)
        
    # Build the mesh and add the object
    mesh = bpy.data.meshes.new(name=cellName)
    mesh.from_pydata(polyVertices, [], polyFaces)
    object_data_add(bpy.context, mesh, name=cellName)
    
    # Set the origin to the center of the mesh
    # bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    
    # Assign the correct biome material
    biomeID = thisCell['biome']
    biomeName = data['biomesData']['name'][biomeID]
    bpy.context.object.data.materials.append(bpy.data.materials[biomeName])
    # add a solidify modifier using h as the height
    #grid.cells.h: number[] - cells elevation in [0, 100] range, where 20 is the minimal land elevation.
    # bpy.ops.object.modifier_add(type='SOLIDIFY')
    # bpy.context.object.modifiers["Solidify"].offset = 1
    # bpy.context.object.modifiers["Solidify"].thickness = thisCell['h']*hScale

# Add burgs. For smaller scale testing, check if the cell that contains the city is in the range above
cityList = data['pack']['burgs']

# Create a burg collection to put the cities in
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.collection.create(name="burgs")

# Get the models for the cities. Assign a model to each culture
# For the initial script, I have objects that are copied and used for the models
cultureMeshList = []
meshList = ['house01','house02','house03','house04','house05','house06','house07','house08','house09','house10','house11','house12','house13','house14']
for x in range(0, len(data['pack']['cultures'])):
    # prints a random value from the list
    aMesh = random.choice(meshList)
    cultureMeshList.append(aMesh)

# The first city is empty, skip it and any other empty ones
for theCity in cityList:
    if theCity and theCity['cell'] > 1000 and theCity['cell'] < 3000:
        cellID = theCity['cell']
        thisCell = data['pack']['cells'][cellID]
        # get the height of the city from the originating cell
        cityLoc = (theCity['x'], theCity['y'], thisCell['h']*hScale)
        # scale by population
        cityScale = theCity['population']/30+.5
        cityName = theCity['name']
        cityCulture = theCity['culture']
        cityIcon = meshList[cityCulture]
        house = bpy.data.objects[cityIcon].data
        object_data_add(bpy.context, house, name=cityName)
        bpy.data.objects[cityName].location = cityLoc
        bpy.data.objects[cityName].scale = [cityScale,cityScale,cityScale]
        # bpy.context.object.name = theCity['name']
        # print(cityLoc)

# Add the Ocean at 20 * hScale
oceanLevel = 20*hScale
bpy.ops.mesh.primitive_plane_add(size=2000, enter_editmode=False, align='WORLD', location=(1000, 1000, oceanLevel), scale=(1, 1, 1))
