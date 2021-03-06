from assets.src import button, config
from assets.src.qr_gen import gen, filter
import pygame as pg
from pygame import font
import cv2
import sys, os
import numpy as np
import sys
from audioplayer import AudioPlayer
from gtts import gTTS

pg.init()

try:
	os.mkdir('qr_codes')
except:
	pass

# height-width	
SCREEN_HEIGHT = 450
SCREEN_WIDTH = 800
TEXTBOX_WIDTH = 272
TEXTBOX_HEIGHT = 35

WHITE = (255, 255, 255)

# create display window
pg.display.set_caption('Lab-Eyes')
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# back button
backImg = pg.image.load('assets/textures/back.png').convert_alpha()
backButton = button.Button(10,10, backImg, 0.05)

# load homepage images
genImg = pg.image.load('assets/textures/QR_GEN.png').convert_alpha()
scanImg = pg.image.load('assets/textures/QR_SCAN.png').convert_alpha()
font = pg.font.Font('assets/fonts/Luckiestguy.ttf', 40*SCREEN_WIDTH//800)
subFont = pg.font.Font('assets/fonts/Luckiestguy.ttf', 20*SCREEN_WIDTH//800)
base_font = pg.font.Font('assets/fonts/Segoe_UI.ttf', 40*SCREEN_WIDTH//800)

genQR = subFont.render('GENERATE QR', True, WHITE)
scanQR = subFont.render('SCAN QR', True, WHITE)
genPrompt = font.render('Enter your text', True, WHITE)
titleText = font.render('LAB EYES', True, WHITE)

# game loop
run = True
pg.key.set_repeat(300, 25)
data = ''
enteredText = ''
camera = cv2.VideoCapture(0)

try:
	while run:
		screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		events = pg.event.get()
		screen.fill((37,38,39,1))

		if config.page in ['scan', 'gen']:
			if backButton.draw(screen):
				config.page = ''

		# Homepage buttons
		if config.page == '':
			screen.blit(titleText, (SCREEN_WIDTH/2-titleText.get_width()/2, SCREEN_HEIGHT/5))
			screen.blit(genQR, (100+genImg.get_width()*0.25/2-genQR.get_width()/2,180 + genImg.get_width()*0.25 + 5))
			screen.blit(scanQR, (500+scanImg.get_width()*0.25/2-scanQR.get_width()/2,180 + scanImg.get_width()*0.25 +5))
			if button.Button(100,180, genImg, 0.25).draw(screen):
				config.page = 'gen'
			elif button.Button(500,180, scanImg, 0.25).draw(screen):
				config.page = 'scan'

		# QR generator
		elif config.page == 'gen':
			try:
				currQrImg = pg.image.load(f'qr_codes/{staticData}.png').convert_alpha()
				if button.Button(SCREEN_WIDTH/2 - currQrImg.get_width()/2*0.4,
								   SCREEN_HEIGHT*0.65,
								   currQrImg, 0.4).draw(screen):
					pass
					# print(f'print qr code here')
			except:
				pass
			
			screen.blit(genPrompt, (SCREEN_WIDTH/2-genPrompt.get_width()/2, SCREEN_HEIGHT/5))

			textSurface = base_font.render(enteredText,True, WHITE)
			screen.blit(textSurface,(100,150))

		# QR scanner
		elif config.page == 'scan':

			while True:

				# read image
				ret, imgOG = camera.read()
				imgOG = cv2.cvtColor(imgOG, cv2.COLOR_BGR2RGB)

				# decode qr
				detector = cv2.QRCodeDetector()
				H_len = np.shape(imgOG)[1]
				config.Data, points, straight_qrcode = detector.detectAndDecode(imgOG)

				if points is not None and len(config.Data) > 0:
					imgOG = cv2.flip(imgOG, 1)

					# simpifies points array->list
					points = np.ndarray.tolist(points)
					points = points[0]
					n_lines = len(points)  

					# converts floats->ints
					for i in range(n_lines):  
						points[i] = [round(a) for a in points[i]]

					# flips lines horizontally
					for i in points:
						i[0] = H_len - i[0]

					# qr bounding
					for i in range(n_lines):
						point1 = tuple(points[i])
						point2 = tuple(points[(i+1) % n_lines])

						# makes box around qr
						cv2.line(imgOG, point1, point2, color=(255, 0, 0),
								thickness=3)  

						# prints text above box
						if i == 0:
							x, y = ((point1[0]//2 + point2[0]//2) - len(config.Data) //
									2*13, (point1[1]//2 + point2[1]//2) - 10)
							cv2.putText(imgOG, config.Data, (x, y),
										cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 0), 2)
						
						# text to speech
						if len(config.Data) >= 1 and config.Data!= config.oldData:
							print('playing')
							speech = gTTS(text=(config.Data), lang='en', slow=False)
							speech.save("current_audio.mp3")
							AudioPlayer("current_audio.mp3").play(block=True)
							print("Just played")
							os.remove("current_audio.mp3")
							config.oldData = config.Data = ''

				else:

					# flips image
					imgOG = cv2.flip(imgOG, 1)

				# image manipulation
				h, w = imgOG.shape[:2]
				ratio = SCREEN_WIDTH/SCREEN_HEIGHT
				if ratio > w/h:
					imgOG = imgOG[int(h-w/ratio)//2:(h - int(h-w/ratio)//2), :]
				elif ratio < w/h:
					imgOG = imgOG[:, :int(w-ratio*h)]
				imgOG = cv2.resize(imgOG, (800, 450), interpolation =cv2.INTER_LINEAR)
				imgOG = imgOG.swapaxes(0, 1)

				# print the image on screen
				pg.surfarray.blit_array(screen, imgOG)

				# back button
				if button.Button(10,10, backImg, 0.05).draw(screen):
					config.page = ''
					screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),)
					break

				# exit events
				pg.display.update()
				events = pg.event.get()
				flag = False

				for event in events:
					if event.type == pg.QUIT: 
						sys.exit(0)
					if event.type == pg.KEYDOWN:
						if event.key == pg.K_ESCAPE:
							sys.exit(0)
						if pg.key.get_mods() & pg.KMOD_LCTRL:
							config.page = ''
							flag = True
						if event.key == pg.K_UP:
							config.page = 'gen'
							flag = True
				# exit
				if flag:
					flag = False
					break
				
			pg.display.quit()
			screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
			pg.display.init()

		# event handler
		for event in events:

			# quit game
			if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
				run = False

			# enter data
			if event.type == pg.KEYDOWN:
				if config.page == 'gen':
					if event.key == pg.K_RETURN:
						data = filter(enteredText)
						staticData = data
						gen(data)
						enteredText = ''
						enteredText = enteredText[:-2]
					if event.key == pg.K_BACKSPACE:
						enteredText = enteredText[:-2]
					else:
						enteredText += event.unicode

				if event.key == pg.K_UP:
					config.page = 'gen'

				if event.key == pg.K_DOWN:
					config.page = 'scan'

				if pg.key.get_mods() & pg.KMOD_LCTRL:
					config.page = ''

		pg.display.update()

except (KeyboardInterrupt, SystemExit):
    pg.quit()
    cv2.destroyAllWindows()

pg.quit()