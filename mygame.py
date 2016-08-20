#!/usr/bin/python3

import pygame
import objects
from objects import Vector
import time
from colour import Colour

# Global Declare
g_displayWidth = 500
g_displayHeight = 600
g_display = Vector(g_displayWidth,g_displayHeight)

# Create Pygame Window
g_displayWindow = pygame.display.set_mode(g_display.t())
g_gameClock = pygame.time.Clock()
pygame.init()
pygame.display.set_caption("PyRacing")

def gameLoop(gameDisplay):
	gameExit = False
	gamePaused = True
	
	hlanes = [75,170,255,325,418]
	vlanes = [250,0,500,300,0]
	lanespeed = [1,0.5,1.5,0.8,1.8]
	score = 0
	x_change = 0
	y_change = 0
	keyRIGHT = 0
	keyLEFT = 0
	keyUP = 0
	keyDOWN = 0
	passed = 0
	dif = 2
	difmod = 0
	score = 0
	highscore = 0
	
	# Load background
	for x in range(2):
		BG = objects.Background('assets/fullroad.png',Vector(500,600),Vector(500,600))
		BG.offset = 600 * x
		
	# Load Player Car	
	P1 = objects.Car('assets/racecar1.png',Vector(120,120),Vector(64,100))
	P1.name = 'player'

	# Set Stating position
	startPos = (g_display / 2) - (P1.box / 2)
	P1.position = startPos

	# Load Obstacles
	for x in range(5):
		newOp = objects.Opponent('assets/racecar2.png',Vector(120,120),Vector(64,100))
		newOp.speed = lanespeed[x]
		newOp.hoffset = hlanes[x] - (newOp.boxwidth() / 2)
		newOp.voffset = vlanes[x]
		newOp.setpos(Vector(newOp.hoffset,newOp.voffset))
		newOp.name = 'opp%i' % x


	# GameLoop
	while not gameExit:
		# Read Events
		for event in pygame.event.get():
			# Exit if window quits
			if event.type == pygame.QUIT:
				gameExit = True

			# Read key Values
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					keyLEFT = 1
				elif event.key == pygame.K_RIGHT:
					keyRIGHT = 1
				elif event.key == pygame.K_UP:
					keyUP = 1
				elif event.key == pygame.K_DOWN:
					keyDOWN = 1
				elif event.key == pygame.K_SPACE:
					gamePaused = not gamePaused
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT:
					keyLEFT = 0
				elif event.key == pygame.K_RIGHT:
					keyRIGHT = 0
				elif event.key == pygame.K_UP:
					keyUP = 0
				elif event.key == pygame.K_DOWN:
					keyDOWN = 0
				elif event.key == pygame.K_ESCAPE:
					gameExit = True

		# Run Simulation
		if not gamePaused:
			# ADJUST MOVE DELTA
			if x_change != 0 and keyRIGHT - keyLEFT == 0:
				# DECREASE X SPEED
				x_change = round(x_change - ((x_change / abs(x_change)) / 4),3)
			else:
				# INCREASE X SPEED
				x_change = max(min(x_change + ((keyRIGHT - keyLEFT) / 2),5),-5)

			if y_change != 0 and keyDOWN - keyUP == 0:
				# DECREASE Y SPEED
				y_change = round(y_change - ((y_change / abs(y_change)) / 10),3)
			else:
				# INCREASE Y SPEED
				y_change = max(min(y_change + ((keyDOWN - keyUP) / 2),4),-4)

			# CHECK POSITION
			car_pos = P1.position
			 
			car_Nx = car_pos.x + x_change
			car_Ny = car_pos.y + y_change

			for o in objects.Opponent.collection.members:
				o.move(Vector(0,(dif + difmod) * o.speed))
				if o.position.y > g_displayHeight:
					o.setpos(Vector(o.position.x,-o.boxheight()))
					score += 1
				collided = P1.hascollided(o)
				if collided[0]:
					if collided[1] != 0:
						if o.center().y > P1.center().y:
							x = -1
						else:
							x = 1
						y_change = ((dif + difmod) * o.speed) * x
					if collided[1] > collided[2]:
						if o.center().x > P1.center().x:
							x = -1
						else:
							x = 1
						x_change = x * (abs(x_change) + 0.5)

			# CHECK AND CHANGE X POSITION
			if car_Nx > g_displayWidth - P1.boxwidth() + (P1.width() / 2) or car_Nx < -(P1.width() / 2):
				x_change = 0
			
			# CHECK FOR Y CONDITIONS
			if car_Ny > g_displayHeight - P1.height():
				# PLAYER HIT BOTTOM OF SCREEN : DISPLAY SCORE AND RESET
				highscore = max(score,highscore)
				msgtxt = 'Score: %i/%i' % (score,highscore)
				msg = objects.TextObject(msgtxt,'freesansbold.ttf',40,Colour.Red,g_display / 2)
				msg.drawcenter = True
				msg.draw(gameDisplay)
				pygame.display.update()
				P1.setang(0)
				P1.setpos(startPos)
				x_change = 0
				y_change = 0
				difmod = 0
				passed = 0
				time.sleep(2)
				del msg
				score = 0
				for Op in objects.Opponent.collection.members:
					Op.setpos(Vector(Op.hoffset,Op.voffset))
				gamePaused = True
			elif car_Ny <= 0:
				# PLAYER HIT TOP OF SCREEN
				y_change = 1

			# MOVE PLAYER
			P1.move(Vector(x_change,y_change + ((dif + difmod) / 2) + (abs(keyRIGHT - keyLEFT) / 2)))
				
			# MOVE OPPONENTS
			for b in objects.Background.collection.members:
				b.setpos(Vector(0,((passed * 2.5) % g_displayHeight) - b.offset))
			
			# INCREMENT PASSED TIME AND INCREASE DIFFICULTY	
			passed += dif + difmod
			difmod = round(min(3.9,difmod + 0.002),3)

		#DRAW TO FRAME
		objects.Sprite.All.draw(gameDisplay)

		#UPDATE DISPLAY
		pygame.display.update()
		g_gameClock.tick(60)

# START GAME LOOP
gameLoop(g_displayWindow)
pygame.quit()
quit()
