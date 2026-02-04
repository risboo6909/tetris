# A simple classic Tetris game

import math
import os
import random
import sys
import time
from pathlib import Path

import pygame
from consts import *
from font_utils import load_font
from pygame.locals import *

global gameState

GAME_STATE = STATE_PLAY
BASE_DIR = Path(__file__).resolve().parent.parent
HIGHSCORE_PATH = BASE_DIR / "highscore.dat"

class FlyingScore():

	def drawMe(self, surface):
		""" Draws score """
		self.rendered = smallfont.render(str(self.lbl), 1, (self.initialColor, self.initialColor, self.initialColor))
		surface.blit(self.rendered, (self.lblX, self.lblY))
		
	def advance(self):
		""" Advances score position on the screen """
		if(self.startY - self.lblY < 30):
			self.lblY -= 1
			self.initialColor -= 5
			return(True)
		return(False)
		
	def __init__(self, lbl, startX, startY):
		""" Initialization """
		global smallfont
		self.lblX = startX
		self.lblY = startY
		self.startY = self.lblY
		self.lbl = str(lbl)
		self.initialColor = 255

class PlayField():

	def drawMe(self, surface):
		""" Draws playfield """
		global COLORS
		y = 0
		x = FIELD_X
		for j in range(0,  SCREEN_HEIGHT // STEP_XY):
			for i in range(0, self.floorWidth):
				if(self.floor[i+j*self.floorWidth] != 0):
					# floor
					pygame.draw.rect(surface, COLORS[self.floor[i+j*self.floorWidth]], pygame.Rect(x, y, STEP_XY, STEP_XY), 0)
				x += STEP_XY
			y += STEP_XY
			x = FIELD_X

	def getFloor(self):
		""" Return playfield data """
		return(self.floor)
		
	def getVirtualCoords(self, blockRef):
		""" Returns slice which consists of the field coordinates taken by the current block """
		self.tmp_slice = []
		for j in range(0, blockRef.sideLen):
			for i in range(0, blockRef.sideLen):
				if(blockRef.getForm()[(blockRef.sideLen) * j + i] != 0):
					# here goes the devil's formula ]:=
					# don't ask me what it does I dont remember it )
					self.tmp_slice.append( blockRef.y // STEP_XY * (self.floorWidth) + j * (self.floorWidth) - (FIELD_X // STEP_XY) + blockRef.x // STEP_XY + i )
		return(self.tmp_slice)

	def getRow(self, rowNum):
		""" Returns selected row """
		return(self.floor[rowNum * self.floorWidth: (rowNum * self.floorWidth + self.floorWidth)])

	def destroyRows(self):
		""" Checks if we need to destroy rows which doesn't contain spaces, moves down
		all the blocks at the top of destroyed rows """
		global score
		global sndBlkDestroy
		global highScore
		global linesDestroyed
		
		scoreAdded = 0
		rowsToDestroy = []
		for j in range ( 0, (SCREEN_HEIGHT // STEP_XY - 1) ):
			needToDestroy = True
			for i in range(0, self.floorWidth):
				if(self.getRow(j)[i] == 0):
					# there is a space in a row therefore we can't destroy it
					needToDestroy = False
					break
			if(needToDestroy == True):
					# add rows which need to be destroyed into array
			        rowsToDestroy.append(j)

		if(len(rowsToDestroy) != 0):
			sndBlkDestroy.play()
			# update score
			for j in range(0, len(rowsToDestroy)):
				scoreAdded += (j + 1) * 100
			score += scoreAdded
			linesDestroyed += len(rowsToDestroy)
			# if current score is greater than the high score => update high score
			if(score > highScore):
				highScore = score
				updateHighScore()
			# destroy lines
			for j in range(0, len(rowsToDestroy)):
				for i in range(0, self.floorWidth):
					self.floor[rowsToDestroy[j] * self.floorWidth + i] = 0
			# lift upper rows down
			for j in range(0, len(rowsToDestroy)):
				for i in range(0, rowsToDestroy[j]):
					for k in range(0, self.floorWidth):
						self.floor[(rowsToDestroy[j] - i) * self.floorWidth + k] = self.getRow(rowsToDestroy[j] - 1 - i)[k]
			return(scoreAdded)
		return(False)
	
	def updateField(self, in_arr, color):
		""" Updates game field """
		for m in range(0, len(in_arr)):
			floor[in_arr[m]] = color

	def __init__(self):
		# initialize floor
		self.floorWidth = FIELD_WIDTH // STEP_XY
		self.floor = []
		for j in range (0, self.floorWidth * SCREEN_HEIGHT // STEP_XY):
			# init walls ->
			if( (j % self.floorWidth) == 0 ):
				self.floor.append(1)
				continue
			if( (j + 1) % (self.floorWidth) == 0 ):
				self.floor.append(1)
				continue
			# init walls <-
			self.floor.append(0)
			# init floor
		for j in range (0, self.floorWidth):
			self.floor[j + SCREEN_HEIGHT // STEP_XY * self.floorWidth - self.floorWidth] = 1

class Tetrix():

	# Array represents blocks data '0' means this cell is free
	# any number greater than zero means it's not a free cell and also
	# refers to a specific color in colors array
	typeData = [
 
			 [0,0,0,0,0,0, 
			  0,0,0,0,0,0, 
			  0,0,2,2,0,0,
			  0,0,0,2,0,0,
			  0,0,0,2,0,0,
			  0,0,0,0,0,0]
			,
			 [0,0,0,0,0,0, 
			  0,0,0,0,0,0, 
			  0,0,3,3,0,0,
			  0,0,3,0,0,0,
			  0,0,3,0,0,0,
			  0,0,0,0,0,0]
			,
			 [0,0,0,0,0,0,
			  0,0,0,0,0,0,
			  0,0,4,4,0,0,
			  0,0,4,4,0,0,
			  0,0,0,0,0,0,
			  0,0,0,0,0,0]
			,
			 [0,0,0,0,0,0,
			  0,0,5,0,0,0,
			  0,0,5,5,0,0,
			  0,0,0,5,0,0,
			  0,0,0,0,0,0, 
			  0,0,0,0,0,0]
			,
			 [0,0,0,0,0,0,
			  0,0,0,6,0,0,
			  0,0,6,6,0,0,
			  0,0,6,0,0,0,
			  0,0,0,0,0,0, 
			  0,0,0,0,0,0]
			,
			 [0,0,0,0,0,0,0,
			  0,0,0,0,0,0,0,
			  0,0,0,7,0,0,0,
			  0,0,7,7,7,0,0,
			  0,0,0,0,0,0,0, 
			  0,0,0,0,0,0,0,
			  0,0,0,0,0,0,0]
			,
			 [0,0,0,0,0,
			  0,0,8,0,0,
			  0,0,8,0,0,
			  0,0,8,0,0,
			  0,0,8,0,0]
			
			  ]


	def drawMe(self, surface):
		""" Draws a single block """
		global COLORS
		self.tmp_y = 0
		self.tmp_x = 0
		for j in range(1, len(self.getForm())):
			if(self.getForm()[j - 1] != 0):
				pygame.draw.rect(surface, COLORS[self.getForm()[j - 1]], pygame.Rect(self.x + self.tmp_x, self.y + self.tmp_y, STEP_XY, STEP_XY), 0)
			self.tmp_x += STEP_XY
			if( ((j % self.sideLen) == 0) and (j != 0) ):
				self.tmp_y += STEP_XY
				self.tmp_x  = 0

	def getForm(self):
		""" Returns structure and color data of selected block """
		return(self.typeData);

	def setCoords(self, cur_x, cur_y):
		""" Sets up block coordinates """
		self.x = cur_x
		self.y = cur_y
	
	def rotateMe(self):
		""" Rotates block's matrix (and hence that rotates a block itself) """
		self.phase += 1
		# restric rotation for some blocks
		if(self.idx == 3 or self.idx == 4 or self.idx == 6):
			if(self.phase >= 3):
				self.phase = 1
				curBlock.typeData = Tetrix.typeData[self.idx][0:len(Tetrix.typeData[self.idx])]
				return
		tmp = self.getForm()[0:len(self.getForm())]
		# transformations.... groovy
		for j in range(0, self.sideLen):
			tmp_col = []
			for i in range(0, self.sideLen):
				tmp_col.append(tmp[j+self.sideLen*i])
			for i in range(j, self.sideLen):
				self.getForm()[j+self.sideLen*i] = 0
			for i in range(0, self.sideLen):
				self.getForm()[(self.sideLen - 1 -i ) + self.sideLen * j] = tmp_col[i]

	def __init__(self, def_x, def_y, idx = -1):
		if(idx == -1):
			# if idx = -1 we randomly choose which block will be created
			self.idx = int((random.random() * 10)) % 7
		else:
			# if idx != -1 we shall create a block with the given index (need it to show NEXT BLOCK)
			self.idx = idx
		# copy block data from the shared array
		self.typeData = Tetrix.typeData[self.idx][0:len(Tetrix.typeData[self.idx])]
		# setup coordinates
		self.setCoords(def_x, def_y)
		# calculate the length of diagonal of the given matrix
		self.sideLen = int(math.sqrt(len(self.getForm())))
		# rotation phase (needed to restric rotation of some blocks)
		self.phase = 1
		# determine block color by looking for the first non-zero element in block matrix
		for j in self.getForm():
			if(j != 0):
				self.color = j
				break


def checkCollision(blkRef, blk_x, blk_y, old_x):
	""" Function checks collision between block and field walls """
	blkRef.setCoords(blk_x, blk_y)
	virtualCoords = playArea.getVirtualCoords(blkRef)
	for j in range(0, len(virtualCoords)):
		if(floor[virtualCoords[j]] != 0):
		    # collision found, restore old coordinates of the block
			blk_x = old_x
			blkRef.setCoords(blk_x, blk_y)
			break
	# return coordinates
	return(blk_x)


def showDialog(in_str, centerX, centerY):
	""" Shows a rectangle with the text in it """
	lbl = bigfont.render(in_str, 1, COLOR_WHITE)
	width, height = bigfont.size(in_str) 
	width += 8
	pygame.draw.rect(screen, COLOR_GRAY, pygame.Rect(centerX - width // 2, centerY - height // 2, width, height), 0)
	screen.blit(lbl, (centerX - width // 2 + 4, centerY - height // 2))


def showStats():
	""" Show current game statistics """
	
	screen.blit(lblHighScore, (FIELD_X + FIELD_WIDTH + 10, 20))
	curScore = smallfont.render(str(highScore), 1, COLOR_WHITE)
	screen.blit(curScore, (FIELD_X + FIELD_WIDTH + 40, 40))

	screen.blit(lblScore, (FIELD_X + FIELD_WIDTH + 10, 90))
	curScore = smallfont.render(str(score), 1, COLOR_WHITE)
	screen.blit(curScore, (FIELD_X + FIELD_WIDTH + 55, 90))

	screen.blit(lblLines, (FIELD_X + FIELD_WIDTH + 10, 110))
	curLines = smallfont.render(str(linesDestroyed), 1, COLOR_WHITE)
	screen.blit(curLines, (FIELD_X + FIELD_WIDTH + 55, 110))
		
	screen.blit(lblLevel, (FIELD_X + FIELD_WIDTH + 10, 130))
	curLevel = smallfont.render(str(level), 1, COLOR_WHITE)
	screen.blit(curLevel, (FIELD_X + FIELD_WIDTH + 55, 130))
	
	screen.blit(lblAuthor, (FIELD_X + FIELD_WIDTH + 10, 290))
	
def readHighScore():
	""" Reads the best score from a file and creates it if needed """
	global highScore
	try:
		with open(HIGHSCORE_PATH, "rt", encoding="utf-8") as f:
			highScore = int(f.read())
	except (OSError, ValueError):
		with open(HIGHSCORE_PATH, "wt", encoding="utf-8") as f:
			f.write(str(0))
		highScore = 0
		
def updateHighScore():
	""" Writes a new high score into file """
	global highScore
	try:
		# open file for writing
		with open(HIGHSCORE_PATH, "wt", encoding="utf-8") as f:
			f.write(str(highScore))
	except:
		pass
	
def mainInit():
	""" Main initiliztion function, needs to be called each time new game starts """
	
	global gameState
	global blk_x, blk_y
	global playArea
	global curBlock, nextBlock
	global doRotate, accelerate
	global skipFramesNum
	global delayBeforeNextBlock
	global showLevelDialog
	global fallingTime
	global floor
	global score, level, nextLevel, linesDestroyed
	global flyUpScore
	
	score = 0
	level = 1
	linesDestroyed = 0
	nextLevel = 1000
	
	gameState = STATE_PLAY
	blk_x, blk_y = 40, 0
	playArea = PlayField()
	curBlock = Tetrix(blk_x, blk_y)
	nextBlock = Tetrix(FIELD_X + FIELD_WIDTH + 10, 180)
	doRotate = False
	accelerate = False
	skipFramesNum = 0
	delayBeforeNextBlock = False
	showLevelDialog = False
	# time to fall down (regulates falling speed)
	fallingTime = 15000
	floor = playArea.getFloor()
	flyUpScore = []
	
# main initialization
readHighScore()

# initialize game window
pygame.init()
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen = pygame.display.get_surface()

# init sounds
sndFall = pygame.mixer.Sound(os.path.join(BASE_DIR, "sounds", "sound1.ogg"))
sndBlkDestroy = pygame.mixer.Sound(os.path.join(BASE_DIR, "sounds", "sound2.ogg"))
sndRotate = pygame.mixer.Sound(os.path.join(BASE_DIR, "sounds", "sound3.ogg"))

# creating fonts
bigfont = load_font(40, BASE_DIR)
smallfont = load_font(12, BASE_DIR)
verysmallfont = load_font(7, BASE_DIR)

# render string
lblScore = smallfont.render("Score: ", 1, COLOR_WHITE)
lblLevel = smallfont.render("Level: ", 1, COLOR_WHITE)
lblLines = smallfont.render("Lines: ", 1, COLOR_WHITE)
lblHighScore = smallfont.render("Best score: ", 1, COLOR_WHITE)
lblAuthor = verysmallfont.render("2008 by Boris Tatarintsev", 1, COLOR_WHITE)

# initialize
mainInit()

while True:

	updateStartTime = pygame.time.get_ticks()

	if(skipFramesNum <= -1 and gameState == STATE_PLAY):
		skipFramesNum = int(fallingTime / ((FIELD_HEIGHT // STEP_XY) * (updateTime + updateDelay * 1000)))

	newCreated = False
	for event in pygame.event.get(): 
		if event.type == ACTIVEEVENT:
			if ((event.state == 2 and event.gain == 0) or (event.state == 6 and event.gain == 0)):
				gameState = STATE_GAMEPAUSED
				strToDisplay = "Paused"
			elif(event.state == 6 and event.gain == 1):
				gameState = STATE_PLAY
			continue
				
		if event.type == QUIT: 
			sys.exit(0) 

		elif event.type == KEYDOWN:
			if(gameState == STATE_GAMEOVER or gameState == STATE_PLAYERWINS):
				 mainInit()
				 continue
				 
			# right
			if(event.key == KEY_RIGHT):
				old_x = blk_x
				blk_x += STEP_XY
				blk_x = checkCollision(curBlock, blk_x, blk_y, old_x)
				
			# left
			if(event.key == KEY_LEFT):
				old_x = blk_x
				blk_x -= STEP_XY
				blk_x = checkCollision(curBlock, blk_x, blk_y, old_x)

			# rotate
			if(event.key == KEY_UP and not delayBeforeNextBlock):
				doRotate = True
				oldState = curBlock.typeData[0:len(Tetrix.typeData[curBlock.idx])]

			# throttle
			if(event.key == KEY_SPACE):
				accelerate = True

	screen.fill(COLOR_BLACK)
	playArea.drawMe(screen)
	showStats()

	# show next block
	nextBlock.drawMe(screen)

	if(gameState == STATE_GAMEOVER or gameState == STATE_PLAYERWINS):
		skipFramesNum -= 1
		continue

	# shows LEVEL dialog for a one second
	if(showLevelDialog == True and pygame.time.get_ticks() - levelDialogStart <= 1000):
		showDialog("Level " + str(level), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
	elif(showLevelDialog == True and pygame.time.get_ticks() - levelDialogStart >= 1000):
		showLevelDialog = False

	# check if it's possible to rotate a block and rotate it then
	if(doRotate and not accelerate):
		curBlock.rotateMe()
		doRotate = False
		rotationPossible = True
		virtualCoords = playArea.getVirtualCoords(curBlock)
		# check if it is possible to rotate the block
		for j in range(0, len(virtualCoords)):
			if(floor[virtualCoords[j]] != 0):
				curBlock.typeData = oldState
				rotationPossible = False
				break
		if(rotationPossible):
			# play sound if rotation is possible
			sndRotate.play()

	curBlock.setCoords(blk_x, blk_y)
	# get vertual coordinates of the current block
	virtualCoords = playArea.getVirtualCoords(curBlock)

	# if user pressed 'space' give him 200 m/sec to adjust the block position after falling
	if(delayBeforeNextBlock and (pygame.time.get_ticks() - timeLeft) >= TIME_TO_SET):
		curBlock.setCoords(blk_x, blk_y)
		delayBeforeNextBlock = False

	# check collisions
	for j in range(0, len(virtualCoords)):
		if(floor[virtualCoords[j]] != 0):

			blk_y -= STEP_XY
			if(accelerate and delayBeforeNextBlock == False):
				timeLeft = pygame.time.get_ticks()
				delayBeforeNextBlock = True
				accelerate = False
				curBlock.setCoords(blk_x, blk_y)
				break

			if(blk_y <= GAMEOVER_TRESHOLD_Y):
				# game over detected ;)
				gameState = STATE_GAMEOVER
				strToDisplay = "Game over"
				curBlock.setCoords(blk_x, blk_y)
				break

			curBlock.setCoords(blk_x, blk_y)

			virtualCoords = playArea.getVirtualCoords(curBlock)
			playArea.updateField(virtualCoords, curBlock.color)
			floor = playArea.getFloor()
			curBlock.drawMe(screen)
			scoreAdded = playArea.destroyRows()
			if(scoreAdded):
				offsetX = curBlock.x + int(math.sqrt(len(curBlock.getForm()))) // 2 * STEP_XY
				if(offsetX + 20 >= (FIELD_X + FIELD_WIDTH)):
					offsetX -= 20
				elif(offsetX - 20 <= FIELD_X):
					offsetX += 20
				flyUpScore.append(FlyingScore(scoreAdded, offsetX, blk_y))

			# advance to a new level if needed
			if(score > nextLevel):
				level += 1
				if(level == 12):
					# player wins, hurray
					gameState = STATE_PLAYERWINS
					strToDisplay = "You win!"
					break
				# calculate how much point player has to collect to advance to next level
				nextLevel += (score + 1000 * (level - 1))
				# show next level dialog
				levelDialogStart = pygame.time.get_ticks()
				showLevelDialog = True
				# speed up blocks falling
				fallingTime = fallingTime - INITIAL_FALLING_TIME // 12

			# create a new block
			blk_y = 0
			blk_x = 40
			sndFall.play()
			curBlock = Tetrix(blk_x, blk_y, nextBlock.idx)
			nextBlock = Tetrix(FIELD_X + FIELD_WIDTH + 10, 180)
			break

	curBlock.drawMe(screen)

	if(gameState == STATE_GAMEOVER or gameState == STATE_PLAYERWINS or gameState == STATE_GAMEPAUSED):
		# draw game over string
		showDialog(strToDisplay, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
		pygame.display.flip()
		continue
		
	# draw flying up score
	tmpSlice = flyUpScore[0: len(flyUpScore)]
	for j in range(0, len(flyUpScore)):
		flyUpScore[j].drawMe(screen)
		if(not flyUpScore[j].advance()):
			del(tmpSlice[j])
	flyUpScore = tmpSlice
	
	# advance block
	if((skipFramesNum == 0 or accelerate) and not delayBeforeNextBlock):
		blk_y += STEP_XY

	skipFramesNum -= 1

	if(accelerate):
		continue
	
	# calculate delay we need to maintain desired FPS
	updateTime = pygame.time.get_ticks() - updateStartTime
	# avoid devision by zero error
	updateTime += 1
	updateDelay = ( (1000 / MAX_FPS) - updateTime ) / 1000.0

	if(updateDelay < 0): 
		updateDelay = 0

	if( updateTime < (1000 / MAX_FPS) ):
		time.sleep(updateDelay)

	# update display
	pygame.display.flip()	
