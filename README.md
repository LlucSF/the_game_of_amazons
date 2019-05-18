# the_game_of_amazons
Python self-learning project based on the board game called The game of amazons, invented in 1988 by Walter Zamkauskas of Argentina. Written in python using the pygame and networkx libraries.

<p align="center">
<img src="https://github.com/LlucSF/the_game_of_amazons/blob/master/resources/cells_6.PNG" width="500">
<p/>

## Installation
In order to play the game you just need to run the module, but first you need to install the packages included in the requirements.txt file.
I recommend creating a new venv, installing there the packages and then running the module as follows:
```
# Create a new venv using conda
$ conda create -n game_amazons_env python=3.7

# Activate it
$ conda activate game_amazons_env

# Install from requirements.txt
(game_amazons_env)$ pip install --user --requirement requirements.txt

# Run the module from the project folder
(game_amazons_env) ~\your_project_folder $ python -m the_game_of_amazons
```
This way, anytime you want to run the module, just change to your new venv and run it from there. 

## Game instructions
If you run the module, the menu screen appears.
<p align="center">
<img src="https://github.com/LlucSF/the_game_of_amazons/blob/master/resources/menu_display.PNG" width="500">
</p>

From it, you can select your desired game. Choose the board size by clicking the square boxes, write the player names by clicking in the text boxes and write the maximum score a player can reach during a full game.
When you are done with the menu click 'New game' and the game will start. If you want to load a previous game click 'Load game'.
At this point, a board should appear.

<p align="center">
<img src="https://github.com/LlucSF/the_game_of_amazons/blob/master/resources/cells_8_new_game.PNG" width="500">
</p>

At the top right corner of the screen, the name and colour of the player that moves is displayed.
Each turn is divided in two phases. 

The first one consist on choosing one of your amazons and moving it to a legal position. 
When that player click on one of its amazons, black circles appear around it, indicating ready to move.
You can click again over it if you want to undo the selection. After selecting, you can move your amazon in diagonals or straight lines, as the image indicates (black lines do not appear in the game):

<p align="center">
<img src="https://github.com/LlucSF/the_game_of_amazons/blob/master/resources/cells_8_move.PNG" width="500">
</p>

After the move is completed, the amazon is going to turn red, indicating ready to shoot fire arrow, which is the second phase of the turn.
You can shoot a fire arrow into a cell following the same rules as moving. The cell where the arrow lands is forbidden for all players. 
You can't shoot arrows across other amazons or other fire arrows.If you click again the amazon, the previous move is going to be undone. 

<p align="center">
<img src="https://github.com/LlucSF/the_game_of_amazons/blob/master/resources/cells_8_shooting.PNG" width="500">
</p>

Finally, when you click on a valid cell, a red cross is going to appear, indicating fire in that cell. No one can reach that cell anymore during the game.
The game ends when a player has all its amazons surrounded by fire or other amazons. 

<p align="center">
<img src="https://github.com/LlucSF/the_game_of_amazons/blob/master/resources/cells_8_fire.PNG" width="500">
</p>

You can save a game anytime you want in a .txt file by pressing 'S'. Then you can load it from the menu screen.

For more information about the game, its rules or history check the following section.
Enjoy!

## About the game
History and rules: https://en.wikipedia.org/wiki/Game_of_the_Amazons

Explanation video by Numberphile: https://www.youtube.com/watch?v=kjSOSeRZVNg&t=308s
