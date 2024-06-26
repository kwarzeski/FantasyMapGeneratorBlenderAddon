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

from bpy.props import (StringProperty,
                       PointerProperty,
                       FloatProperty,
                       )
                       
from bpy.types import (Panel,
                       PropertyGroup,
                       Operator,
                       )

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

def coaBaseColor(coa):
    coa_colors = {
        "argent" : [250, 250, 250, 255],
        "or" : [255, 224, 102, 255],
        "gules" : [215, 55, 74, 255],
        "azure" : [55, 124, 215, 255],
        "sable" : [51, 51, 51, 255],
        "purpure" : [82, 45, 91, 255],
        "vert" : [38, 192, 97, 255],
        "murrey" : [133, 24,91, 255],
        "sanguine" : [182, 58, 58, 255],
        "tenne" : [204, 127, 25, 255]   
    }
    normalized_colors = {k: [i / 255 for i in v] for (k, v) in coa_colors.items() }
    tint = "argent"
    if "-" in coa['t1']:
        tint = coa['t1'].split("-")[1]
    else:
        tint = coa['t1']
    return tuple(normalized_colors[tint])

def buildTerrain(data, hScale, dscale):
    # For testing, use a smaller subset of cells
    cellData = data['pack']['cells'][1000:3000]
    
    # Boundary info used to place and center the map
    # Center the map on 0,0,0
    # Flip the y axis
    bounds = [data['grid']['boundary'][0],data['grid']['boundary'][1],data['grid']['boundary'][-2],data['grid']['boundary'][-1]]
    mapSize = [(bounds[3][0]+bounds[2][0])*dscale, (bounds[0][1]+bounds[1][1])*dscale]
    
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
        # scale height
        if thisCell['h'] >= 20:
            vertHeight = ((thisCell['h'] - 18) ** hScale) * bpy.context.scene.heightScaling
        else:
            vertHeight = (((thisCell['h'] - 20) / max(thisCell['h'],1)) * 50) * bpy.context.scene.heightScaling
        cellCenter = [thisCell['p'][0]*dscale- mapSize[0]/2,mapSize[1]/2 -thisCell['p'][1]*dscale,vertHeight]
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
            # Scale height
            if vertHeight >= 20:
                vertHeight = ((vertHeight - 18) ** hScale) * bpy.context.scene.heightScaling
            else:
                vertHeight = (((vertHeight - 20) / max(vertHeight,1)) * 50) * bpy.context.scene.heightScaling
            # Check if connected vertices are in the list yet. build a face with any that are
            # Ignore -1 vertex id
            # Faces are vertex, neighbor, center
            for neighborVert in connectedVertices:
                if neighborVert in vertList and not neighborVert == -1:
                    # This vertex will be in n+1 position in the polyVertices list
                    polyFace = [(n+1), vertList.index(neighborVert),0]
                    polyFaces.append(polyFace)
            vertList.append(vertID)
            vert = Vector((vertPosition[0]*dscale - mapSize[0]/2, mapSize[1]/2 -vertPosition[1]*dscale, vertHeight))
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

# Add burgs. 
def buildBurgs(data, meshList, hScale, distanceScale):
    # Create a burg collection to put the cities in
    # bpy.ops.object.select_all(action='DESELECT')
    # bpy.ops.collection.create(name="burgs")
    cultures = data['pack']['cultures']
    cells = data['pack']['cells']
    cityList = data['pack']['burgs']
    
    # Set up culture specific models for burgs
    # Get the models for the cities. Assign a model to each culture
    # Todo: give each culture its own model, have secondary material for state
    # If no collection is selected, use cubes
    cultureMeshList = []
    for x in range(0, len(cultures)):
        # prints a random value from the list
        aMesh = random.choice(meshList)
        cultureMeshList.append(aMesh)
        # Hide the collection in viewport after using the meshes
        # bpy.context.scene.burg_icon_collection.hide_viewport = True
        
    # Boundary info used to place and center the map
    # Center the map on 0,0,0
    # Flip the y axis
    # x - mapSize[0]/2
    # mapSize[1]/2 - y
    bounds = [data['grid']['boundary'][0],data['grid']['boundary'][1],data['grid']['boundary'][-2],data['grid']['boundary'][-1]]
    mapSize = [(bounds[3][0]+bounds[2][0]) * distanceScale, (bounds[0][1]+bounds[1][1]) * distanceScale]
    
    # The first city is empty, skip it and any other empty ones
    # For smaller scale testing, check if the cell that contains the city is in the range above
    for theCity in cityList:
        if theCity:
            cellID = theCity['cell']
            thisCell = cells[cellID]
            # get the height of the city from the originating cell
            # Will need to switch to raytracing to get correct height
            cityLoc = (theCity['x'] * distanceScale - mapSize[0]/2, mapSize[1]/2 - theCity['y'] * distanceScale, ((thisCell['h'] - 18) ** hScale) * bpy.context.scene.heightScaling)
            
            # scale by population
            cityScale = theCity['population']*data['settings']['populationRate']/100 + 1
            cityName = theCity['name']
            cityCulture = theCity['culture']
            cityIcon = cultureMeshList[cityCulture]
            house = bpy.data.objects[cityIcon].data
            # If no mesh available/selected, place a cube
            # bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            # bpy.context.object.name = cityName

            object_data_add(bpy.context, house, name=cityName)
            bpy.data.objects[cityName].location = cityLoc
            bpy.data.objects[cityName].scale = [cityScale,cityScale,cityScale]
            bpy.data.objects[cityName].rotation_euler[2]= random.uniform(-3.14159,3.14159)
            # print(cityLoc)

class BuildAzTerrainOperator(bpy.types.Operator):
    """Builds Terrain and Burgs into the scene"""
    bl_idname = "mesh.build_az_terrain"
    bl_label = "Build Terrain"

    def execute(self, context):
        # Load the JSON file
        file_name = context.scene.my_tool.path
        f = open(file_name, "r", encoding="utf8")
        data = json.loads(f.read())
        cells = data['pack']['cells']
        f.close()

        # Scaling for distance and getting the size of the map
        # Blender's default units are meters
        # scaling for height manually at the moment
        hScale = float(data['settings']['heightExponent'])
        
        # ToDo: convert from miles to meters for Blender. Scale up using settings
        # scaleUnit = 1609.34
        distanceScale = float(data['settings']['distanceScale'])
        distanceUnit = data['settings']['distanceUnit']
        # convert distance to meters
        if distanceUnit == 'mi':
            distanceScale = distanceScale * 1609.34
        elif distanceUnit == 'km':
            distanceScale = distanceScale * 1000
        else:
            distanceScale = distanceScale * 1500
        # Get the distScaling from the panel
        distanceScale = distanceScale * bpy.context.scene.distScaling
        bounds = [data['grid']['boundary'][0],data['grid']['boundary'][1],data['grid']['boundary'][-2],data['grid']['boundary'][-1]]
        mapSize = [bounds[3][0]+bounds[2][0], bounds[0][1]+bounds[1][1]]
        mapName = data['info']['mapName']
        # ToDo: Scale and convert height. Height is in meters
        # height = (cell['h'] - 18) ** float(data['settings']['heightExponent'])
        
        # Get the collection to pull the city meshes from. Do this BEFORE making anything. If user has the collection selected, it will build the objects into the city collection :(
        meshList = bpy.context.scene.burg_icon_collection.all_objects.keys()
        
        # create a collection to put everthing in
        # bpy.ops.collection.create(name  = mapName)
        # bpy.context.scene.collection.children.link(bpy.data.collections[mapName])

        buildMaterials(data['biomesData'])

        # For testing, just generate a few cells in the middle. Hope its not ocean :)
        buildTerrain(data, hScale, distanceScale)
                    
        buildBurgs(data, meshList, hScale, distanceScale)

        # Add the Ocean at 20 * hScale
        # oceanLevel = 18
        # bpy.ops.mesh.primitive_plane_add(size=2000, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        # bpy.context.object.data.materials.append(bpy.data.materials['Marine'])
        
        return {'FINISHED'}

class MyProperties(PropertyGroup):
    path: StringProperty(
        name="File",
        description="Path to Directory",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')

class SamplePanel(bpy.types.Panel):
    """ Displayy panel in 3D view"""
    bl_label = "Import Azgaar Fantasy Map"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Create"
    bl_context = "objectmode"
    bl_options = {'HEADER_LAYOUT_EXPAND'}
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(context.scene.my_tool, "path", text="")
        col.prop(context.scene, "burg_icon_collection")
        col.prop(context.scene, "distScaling")
        col.prop(context.scene, "heightScaling")
        col.operator("mesh.build_az_terrain", icon="MESH_CUBE")
    
classes = (
        MyProperties,
        SamplePanel,
        BuildAzTerrainOperator
        )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_tool = PointerProperty(type=MyProperties)
    bpy.types.Scene.burg_icon_collection = PointerProperty(name="Burgs",type=bpy.types.Collection)
    bpy.types.Scene.distScaling = bpy.props.FloatProperty(
        name='distScaling',
        default=1.0 
    )
    bpy.types.Scene.heightScaling = bpy.props.FloatProperty(
        name='heightScaling',
        default=1.0 
    )

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.my_tool
    del bpy.types.Scene.burg_icon_collection
    del bpy.types.Scene.distScaling
    del bpy.types.Scene.heightScaling

if __name__ == "__main__":
    register()