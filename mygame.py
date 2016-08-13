import pygame
import math
import objects
import colour

display_width = 500
display_height = 600

mainDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption("A Bit Racey")
clock = pygame.time.Clock()
pygame.init()

def gameLoop(gameDisplay):
	gameExit = False
	gamePaused = False
	objs = []
	obst = []
	bgs = []
	lanes = [80,165,250,335,420]
	for x in range(2):
		BG = objects.bg('assets/fullroad.png',500,600,500,600)
		BG.offset = 600 * x
		objs.append(BG)
		bgs.append(BG)
		
		
	P1 = objects.car('assets/racecar1.png',120,120,64,100)
	objs.append(P1)
	
	for x in range(3):
		newOp = objects.opponent('assets/racecar2.png',120,120,64,100)
		newOp.hoffset = lanes[x] - (newOp.boxwidth / 2)
		newOp.voffset = [250,0,500][x]
		newOp.speed = 0.8 * (x + 1) 
		objs.append(newOp)
		obst.append(newOp)

	startPos = [(display_width / 2) - (P1.boxwidth / 2),(display_height / 2) - (P1.boxheight / 2)]
	P1.setpos(startPos)

	x_change = 0
	y_change = 0
	keyRIGHT = 0
	keyLEFT = 0
	keyUP = 0
	keyDOWN = 0
	passed = 0
	dif = 2
	difmod = 0
	collision = False
	while not gameExit:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				gameExit = True

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

		if not gamePaused:
			#ADJUST MOVE DELTA
			if x_change != 0 and keyRIGHT - keyLEFT == 0:
				#DECREASE X SPEED
				x_change = round(x_change - ((x_change / abs(x_change)) / 4),3)
			else:
				#INCREASE X SPEED
				x_change = max(min(x_change + ((keyRIGHT - keyLEFT) / 2),5),-5)

			if y_change != 0 and keyDOWN - keyUP == 0:
				#DECREASE Y SPEED
				y_change = round(y_change - ((y_change / abs(y_change)) / 10),3)
			else:
				#INCREASE Y SPEED
				y_change = max(min(y_change + ((keyDOWN - keyUP) / 2),4),-4)

			#CHECK POSITION
			car_pos = P1.position
			
			car_Nx = car_pos[0] + x_change
			car_Ny = car_pos[1] + y_change
			
			#ANGLE
			if P1.angle != 0 and (keyRIGHT - keyLEFT) == 0:
				#DECREASE ANGLE
				P1.setang(P1.angle - (P1.angle / abs(P1.angle)))
			else:
				#INCREASE ANGLE
				P1.setang(max(min(10,P1.angle - (keyRIGHT - keyLEFT)),-10))

			#CHECK AND CHANGE X POSITION
			if car_Nx < display_width - P1.boxwidth + 25 and car_Nx > -25:
				P1.move((x_change,0))

			
			for o in obst:
				o.setpos((o.hoffset,(((passed + o.voffset) * o.speed) % (display_height + o.boxheight)) - o.boxheight))
				collided = P1.hascollided(o)
				if collided[0]:
					if collided[1] != 0:
						y_change = dif * (min(max(int(collided[1]),-1),1))
					if collided[1] > collided[2]:
						x_change = x_change * -1
						P1.setang(P1.angle / 2)
			


			#CHECK AND CHANGE Y POSITION
			if car_Ny > display_height - P1.height:
				##Crashed##
				P1.setang(0)
				P1.setpos(startPos)
				x_change = 0
				y_change = 0
				difmod = 0
				passed = 0
				gamePaused = True
			elif car_Ny > 0:
				P1.move((0,y_change + ((dif + difmod) / 2) + (abs(keyRIGHT - keyLEFT) / 2)))
				
			for b in bgs:
				b.setpos((0,((passed * 2) % display_height) - b.offset))
				
			passed += dif + difmod
			difmod = round(min(3.9,difmod + 0.002),3)
		#DRAW TO FRAME
		#gameDisplay.fill(colour.DavyGrey)
		for o in objs:
			o.draw(gameDisplay)

		#UPDATE DISPLAY
		pygame.display.update()
		clock.tick(60)


gameLoop(mainDisplay)
pygame.quit()
quit()
