import pygame
import objects
import time
import colour

g_displayWidth = 500
g_displayHeight = 600

g_displayWindow = pygame.display.set_mode((g_displayWidth,g_displayHeight))
g_gameClock = pygame.time.Clock()

pygame.init()
pygame.display.set_caption("PyRacing")

def gameLoop(gameDisplay):
	_gameExit = False
	_gamePaused = True
	_objs = []
	_obst = []
	_bgs = []
	
	_hlanes = [80,165,250,335,420]
	_vlanes = [250,0,500,300,0]
	_lanespeed = [1,0.5,1.5,0.8,1.8]
	_score = 0
	
	for x in range(2):
		__BG = objects.Background('assets/fullroad.png',500,600,500,600)
		__BG.offset = 600 * x
		_objs.append(__BG)
		_bgs.append(__BG)
		
		
	_P1 = objects.Car('assets/racecar1.png',120,120,64,100)
	_objs.append(_P1)
	
	_startPos = [(g_displayWidth / 2) - (_P1.boxwidth / 2),(g_displayHeight / 2) - (_P1.boxheight / 2)]
	_P1.setpos(_startPos)
	
	for x in range(5):
		__newOp = objects.Opponent('assets/racecar2.png',120,120,64,100)
		__newOp.hoffset = _hlanes[x] - (__newOp.boxwidth / 2)
		__newOp.voffset = _vlanes[x]
		__newOp.speed = _lanespeed[x]
		__newOp.setpos((__newOp.hoffset,__newOp.voffset))
		_objs.append(__newOp)
		_obst.append(__newOp)

	_x_change = 0
	_y_change = 0
	_keyRIGHT = 0
	_keyLEFT = 0
	_keyUP = 0
	_keyDOWN = 0
	_passed = 0
	_dif = 2
	_difmod = 0
	_score = 0
	_highscore = 0

	while not _gameExit:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				_gameExit = True

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					_keyLEFT = 1
				elif event.key == pygame.K_RIGHT:
					_keyRIGHT = 1
				elif event.key == pygame.K_UP:
					_keyUP = 1
				elif event.key == pygame.K_DOWN:
					_keyDOWN = 1
				elif event.key == pygame.K_SPACE:
					_gamePaused = not _gamePaused
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT:
					_keyLEFT = 0
				elif event.key == pygame.K_RIGHT:
					_keyRIGHT = 0
				elif event.key == pygame.K_UP:
					_keyUP = 0
				elif event.key == pygame.K_DOWN:
					_keyDOWN = 0
				elif event.key == pygame.K_ESCAPE:
					_gameExit = True

		if not _gamePaused:
			#ADJUST MOVE DELTA
			if _x_change != 0 and _keyRIGHT - _keyLEFT == 0:
				#DECREASE X SPEED
				_x_change = round(_x_change - ((_x_change / abs(_x_change)) / 4),3)
			else:
				#INCREASE X SPEED
				_x_change = max(min(_x_change + ((_keyRIGHT - _keyLEFT) / 2),5),-5)

			if _y_change != 0 and _keyDOWN - _keyUP == 0:
				#DECREASE Y SPEED
				_y_change = round(_y_change - ((_y_change / abs(_y_change)) / 10),3)
			else:
				#INCREASE Y SPEED
				_y_change = max(min(_y_change + ((_keyDOWN - _keyUP) / 2),4),-4)

			#CHECK POSITION
			_car_pos = _P1.position
			
			_car_Nx = _car_pos[0] + _x_change
			_car_Ny = _car_pos[1] + _y_change

			for o in _obst:
				o.move((0,(_dif + _difmod) * o.speed))
				if o.position[1] > g_displayHeight:
					o.setpos((o.position[0],-o.boxheight))
					_score += 1
				__collided = _P1.hascollided(o)
				if __collided[0]:
					if __collided[1] != 0:
						if o.center()[1] > _P1.center()[1]:
							__x = -1
						else:
							__x = 1
						_y_change = ((_dif + _difmod) * o.speed) * __x
					if __collided[1] > __collided[2]:
						if o.center()[0] > _P1.center()[0]:
							__x = -1
						else:
							__x = 1
						_x_change = __x * (abs(_x_change) + 0.5)

			#CHECK AND CHANGE X POSITION
			if _car_Nx > g_displayWidth - _P1.boxwidth + (_P1.width / 2) or _car_Nx < -(_P1.width / 2):
				_x_change = 0
			
			#CHECK AND CHANGE Y POSITION
			if _car_Ny > g_displayHeight - _P1.height:
				##Crashed##
				_P1.setang(0)
				_P1.setpos(_startPos)
				_x_change = 0
				_y_change = 0
				_difmod = 0
				_passed = 0
				_highscore = max(_score,_highscore)
				__msg = objects.TextObject('Score: %i/%i' % (_score,_highscore),'freesansbold.ttf',40,colour.Red,(g_displayWidth/2,g_displayHeight/2)).drawCenter(gameDisplay)
				pygame.display.update()
				time.sleep(2)
				del __msg
				_score = 0
				for Op in _obst:
					Op.setpos((Op.hoffset,Op.voffset))
				_gamePaused = True
			elif _car_Ny <= 0:
				_y_change = 1

			_P1.move((_x_change,_y_change + ((_dif + _difmod) / 2) + (abs(_keyRIGHT - _keyLEFT) / 2)))
				
			for b in _bgs:
				b.setpos((0,((_passed * 2.5) % g_displayHeight) - b.offset))
				
			_passed += _dif + _difmod
			_difmod = round(min(3.9,_difmod + 0.002),3)
		#DRAW TO FRAME
		for o in _objs:
			o.draw(gameDisplay)

		#UPDATE DISPLAY
		pygame.display.update()
		g_gameClock.tick(60)


gameLoop(g_displayWindow)
pygame.quit()
quit()