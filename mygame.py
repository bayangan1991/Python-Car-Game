import pygame
import objects
import time
import colour

g_displayWidth = 500
g_displayHeight = 600

pygame.display.set_caption("PyRacing")

g_displayWindow = pygame.display.set_mode((g_displayWidth,g_displayHeight))
g_gameClock = pygame.time.Clock()

pygame.init()

def gameLoop(gameDisplay):
	gameExit = False
	gamePaused = True
	objs = []
	obst = []
	bgs = []
	
	hlanes = [80,165,250,335,420]
	vlanes = [250,0,500,300,0]
	lanespeed = [1,0.5,1.5,0.8,1.8]
	score = 0
	
	for x in range(2):
		BG = objects.bg('assets/fullroad.png',500,600,500,600)
		BG.offset = 600 * x
		objs.append(BG)
		bgs.append(BG)
		
		
	P1 = objects.car('assets/racecar1.png',120,120,64,100)
	objs.append(P1)
	
	startPos = [(g_displayWidth / 2) - (P1.boxwidth / 2),(g_displayHeight / 2) - (P1.boxheight / 2)]
	P1.setpos(startPos)
	
	for x in range(5):
		newOp = objects.opponent('assets/racecar2.png',120,120,64,100)
		newOp.hoffset = hlanes[x] - (newOp.boxwidth / 2)
		newOp.voffset = vlanes[x]
		newOp.speed = lanespeed[x]
		newOp.setpos((newOp.hoffset,newOp.voffset))
		objs.append(newOp)
		obst.append(newOp)

	x_change = 0
	y_change = 0
	keyRIGHT = 0
	keyLEFT = 0
	keyUP = 0
	keyDOWN = 0
	passed = 0
	dif = 0
	difmod = 0
	score = 0
	highscore = 0

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

			for o in obst:
				o.move((0,(dif + difmod) * o.speed))
				if o.position[1] > g_displayHeight:
					o.setpos((o.position[0],-o.boxheight))
					score += 1
				collided = P1.hascollided(o)
				if collided[0]:
					if collided[1] != 0:
						if o.center()[1] > P1.center()[1]:
							x = -1
						else:
							x = 1
						y_change = ((dif + difmod) * o.speed) * x
					if collided[1] > collided[2]:
						if o.center()[0] > P1.center()[0]:
							x = -1
						else:
							x = 1
						x_change = x * (abs(x_change) + 0.5)

			#CHECK AND CHANGE X POSITION
			if car_Nx > g_displayWidth - P1.boxwidth + 25 or car_Nx < -25:
				x_change = 0
			
			#CHECK AND CHANGE Y POSITION
			if car_Ny > g_displayHeight - P1.height:
				##Crashed##
				P1.setang(0)
				P1.setpos(startPos)
				x_change = 0
				y_change = 0
				difmod = 0
				passed = 0
				highscore = max(score,highscore)
				msg = objects.textObject('Score: %i/%i' % (score,highscore),'freesansbold.ttf',40,colour.Red,(g_displayWidth/2,g_displayHeight/2)).drawCenter(gameDisplay)
				pygame.display.update()
				time.sleep(2)
				msg = None
				score = 0
				for Op in obst:
					Op.setpos((Op.hoffset,Op.voffset))
				gamePaused = True
			elif car_Ny <= 0:
				y_change = 1

			P1.move((x_change,y_change + ((dif + difmod) / 2) + (abs(keyRIGHT - keyLEFT) / 2)))
				
			for b in bgs:
				b.setpos((0,((passed * 2.5) % g_displayHeight) - b.offset))
				
			passed += dif + difmod
			difmod = round(min(5.9,difmod + 0.001),3)
		#DRAW TO FRAME
		for o in objs:
			o.draw(gameDisplay)

		#UPDATE DISPLAY
		pygame.display.update()
		g_gameClock.tick(60)


gameLoop(g_displayWindow)
pygame.quit()
quit()