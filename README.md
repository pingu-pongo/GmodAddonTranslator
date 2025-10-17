# GmodAddonTranslator
* This application searches for your Garry's Mod content folder and creates a new one with "Translated" appended to it
* It then iterates through each addon in the folder and creates a new folder under 4000Translated named after the addon's title on the workshop
* In each addon folder, it decompiles the gmpublisher.gma file from the original addon folder, and creates a link file that, when clicked, pulls up the addon on the workshop 
* Sometimes these addon folders contain no .gma file, in this case it searches your GarrysMod/garrysmod/cache/workshop folder for the .gma

