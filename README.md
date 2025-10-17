# GmodAddonTranslator (how it works)
* Searches for your Garry's Mod content folder (4000) and creates a new one with 'Translated' appended to it
* It then iterates over your Gmod content folder and translates each addon to a new folder in the newly created 'Translated' folder
* These folders are instead named with the addons workshop title instead of a meaningless addon ID for ease of understanding and searchability
* Inside each addon folder, this program will decompile the .gma file from the original addon folder.
     - Occasionally, these will be stored in your \steamapps\common\GarrysMod\garrysmod\cache\workshop folder.
     - The program will yoink the gma from here if it can't find it in the addon folder
* Inside each addon folder, it will also generate a URL file that, when clicked, will take you to the workshop listing for the addon
     - This feature only works on Windows for now.

# How to Install
* On the right-hand side, find the 'Releases' tab
* Click the latest release
* Download the source code zip
* Unzip it
* Run GmodAddonTranslator.exe
     - Windows will complain because the exe isn't signed.
     - I did not feel like shelling out money to professionally sign this since it's a hobby project
* If you are unsure of this code's legitimacy, feel free to either inspect the two source code files (translator_gui.py + translator_logic.py) or chuck them in your choice of AI model and have it summarize them for you. 

# Program Options
* To start, you will have to click the 'Initialize' button, as this searches your drives for your Garry's Mod installation.
* After this, 'Start Processing' should appear. Before you click this, though, change the thread count if you want.
      - More threads = faster processing. More threads also mean more instability. Depending on how large your addon folder is, I would even recommend going up to 12.
      - For most people, the default setting of 6 is plenty fine. 
* Click 'Start Processing' and let it do its magic. Once complete, the 'Open Translated Folder' button will take you there. 
