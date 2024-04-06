# Fantasy Map Generator Blender Addon

A Blender script/addon that allows you to import a map from [Azgaar's Fantasy Map Generator](https://azgaar.github.io/Fantasy-Map-Generator/) as a mesh.

## Getting the JSON from Azgaar

Export the full JSON from the site. 

![Screenshot 2024-03-25 102607](https://github.com/kwarzeski/FantasyMapGeneratorBlenderAddon/assets/99751286/adb2ef6b-3f1c-40ce-9975-e223326b7b5d)
![Screenshot 2024-03-25 102627](https://github.com/kwarzeski/FantasyMapGeneratorBlenderAddon/assets/99751286/916abca8-251c-4b2b-ad94-80216ce4938b)

## Using the Addon

When installed, a panel will appear under the 'Create' tab in Object mode.

![Screenshot 2024-04-06 141121](https://github.com/kwarzeski/FantasyMapGeneratorBlenderAddon/assets/99751286/880f0b82-2653-4310-a140-1cec245d6c3b)

Select a collection with meshes to represent the burgs. Needs a minimum of one mesh object. Select the JSON file from Azgaar, then click the 'Build Terrain' button. 

Distscaling is the scaling for distances on the terrain. Leaving the value at 1 results in a large map, which assumes blender units = 1 meter. Heightscaling adjusts the scaling for heights. Underwater scales differently than above.

All the cells will be created as seperate objects. Materials are created for each biome and assigned to the cells. The burg meshes will be randomly assigned to each culture and will appear on each burg location, scaled for population.

## To Do & Known Bugs:
- Check for duplicate vertices when building the cells
- Burg Flags to indicate state allegiance
  * Some way of indicating province allegiance
  * Set a secondary material on each burg mesh for province or state
- Road implementation
  * Roads are not included in the full JSON export - will need to be loaded from the geoJSON file
- River implementation
- Lake implementation
