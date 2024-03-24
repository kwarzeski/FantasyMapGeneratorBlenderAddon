bl_info = {
    "name": "Import Azgaar Map",
    "blender": (2, 80, 0),
    "version": (1, 0),
    "location": "View3D > Add > Mesh",
    "category": "3D View"
}

# summon librarys
import json
import bpy
from mathutils import Vector
from bpy_extras.object_utils import AddObjectHelper, object_data_add
import random

class BuildAzTerrainOperator(bpy.types.Operator):
    """Builds Terrain and Burgs into the scene"""
    bl_idname = "mesh.build_az_terrain"
    bl_label = "Build Terrain"

    def execute(self, context):
        # JSON file
        file_name = "C:/Users/kolse/Downloads/Thouzon-Full.json"

        f = open(file_name, "r", encoding="utf8")
         
        # Reading from file
        data = json.loads(f.read())
        cells = data['pack']['cells']
        # Closing file
        f.close()

        # scaling for height manually at the moment
        hScale = .25

        # Create basic materials for each biome
        def buildMaterials(biomesData):
            for x in biomesData['i']:
                # name for the biome
                biomeName = biomesData['name'][x]
                new_mat = bpy.data.materials.new(biomeName)
                #convert hex to rgb, add 1 as fourth digit for full opacity
                h = biomesData['color'][x].lstrip('#')
                diffColor = [int(h[i:i+2], 16) for i in (0, 2, 4)]
                diffColor = [(i/255) for i in diffColor]
                diffColor.append(1)
                # setting the diffuse color to the material
                bpy.data.materials[biomeName].diffuse_color = tuple(diffColor)
        buildMaterials(data['biomesData'])

        def buildTerrain(cellData):
            for thisCell in cellData:
                verticesCount = len(thisCell['v'])
                cellName = "cell" + str(thisCell['i'])
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
                    #grid.cells.h: number[] - cells elevation in [0, 100] range, where 20 is the minimal land elevation.
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

        # For testing, just generate a few cells in the middle. Hope its not ocean :)
        demoCells = cells[1000:3000]
        buildTerrain(demoCells)

        # Set up culture specific models for burgs
        # Get the models for the cities. Assign a model to each culture
        # Todo: Better way of referencing models, give each culture its own model, have secondary material for state
        cultureMeshList = []
        meshList = ['house01','house02','house03','house04','house05','house06','house07','house08','house09','house10','house11','house12','house13','house14']
        for x in range(0, len(data['pack']['cultures'])):
            # prints a random value from the list
            aMesh = random.choice(meshList)
            cultureMeshList.append(aMesh)

        # Add burgs. 
        def buildBurgs(cityList):
            # Create a burg collection to put the cities in
            # bpy.ops.object.select_all(action='DESELECT')
            # bpy.ops.collection.create(name="burgs")
            
            # The first city is empty, skip it and any other empty ones
            # For smaller scale testing, check if the cell that contains the city is in the range above
            for theCity in cityList:
                if theCity and theCity['cell'] > 1000 and theCity['cell'] < 3000:
                    cellID = theCity['cell']
                    thisCell = data['pack']['cells'][cellID]
                    # get the height of the city from the originating cell
                    # Will need to switch to raytracing to get correct height
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
                    bpy.data.objects[cityName].rotation_euler[2]= random.uniform(-3.14159,3.14159)
                    # bpy.context.object.name = theCity['name']
                    # print(cityLoc)
        buildBurgs(data['pack']['burgs'])

        # Add the Ocean at 20 * hScale
        oceanLevel = 20*hScale
        bpy.ops.mesh.primitive_plane_add(size=2000, enter_editmode=False, align='WORLD', location=(1000, 1000, oceanLevel), scale=(1, 1, 1))
        
        return {'FINISHED'}

class SamplePanel(bpy.types.Panel):
    """ Displayy panel in 3D view"""
    bl_label = "Import Azgaar Fantasy Map"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'HEADER_LAYOUT_EXPAND'}
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("mesh.build_az_terrain", icon="MESH_CUBE")
    
classes = (
        SamplePanel,
        BuildAzTerrainOperator
        )
    

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()