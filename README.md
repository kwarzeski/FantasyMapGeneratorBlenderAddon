# Fantasy Map Generator Blender Addon

A Blender script/addon that allows you to import a map from [Azgaar's Fantasy Map Generator](https://azgaar.github.io/Fantasy-Map-Generator/) as a mesh.

## Getting the JSON from Azgaar

Export the full JSON from the site. 

![Screenshot 2024-03-25 102607](https://github.com/kwarzeski/FantasyMapGeneratorBlenderAddon/assets/99751286/adb2ef6b-3f1c-40ce-9975-e223326b7b5d)
![Screenshot 2024-03-25 102627](https://github.com/kwarzeski/FantasyMapGeneratorBlenderAddon/assets/99751286/916abca8-251c-4b2b-ad94-80216ce4938b)

## Using the Addon

Currently, you need 14 mesh objects to represent the different cultures' cities. They are named 'house01', 'house02', 'house03', 'house04', 'house05', 'house06', 'house07', 'house08', 'house09', 'house10', 'house11', 'house12', 'house13', and 'house14'. The addon randomly selects from the list for each culture.

When installed, a panel will appear under the 'Create' tab in Object mode.

![Screenshot 2024-03-25 103150](https://github.com/kwarzeski/FantasyMapGeneratorBlenderAddon/assets/99751286/7618ad35-72f7-4c75-b4bf-0d54514d512e)

Select the JSON file, then click the 'Build Terrain' button. 

All the cells will be created as seperate objects. Materials are created for each biome and assigned to the cells. A house 'icon' will appear on each burg location, scaled for population.

## To Do:
- Maps are currently flipped on the y-axis
- Match scaling from the generator
- Check for duplicate vertices
- Burg Flags to indicate state allegiance
  * Some way of indicating province allegiance 
- Road implementation
- River implementation
- Lake implementation
