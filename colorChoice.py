#!/usr/bin/python
#									oOosys							     2024-09-30_05:26
#													last update:		     2024-09-30_22:31
'''	Text-FREE color choice interface showing all possible colors in channel slider strips		
				and a large area showing the currently selected color					     '''
#	Requires installed cv2 and for the color name functionality the webcolor module. 
withOutputOfClosestColorName = 'Yes'  ## [ 'Yes' , '' ] 
wID = "[f] : Fullscreen   ||   Slider: [Tab], [arrowLeftRightUpDown], [PageUp/Down]   ||   [r]/[h]/[l] -> RGB/HSV/HLS   ||   Enter/Click to print (R,G,B) to stdout and Exit."	
windowXpos	=	  30
windowYpos	=	  10
windowWidth	 = 1890
windowHeight	 = 1050
# ---
widthColorStripColor			=	7
heightColorStrip				= 130
verticalSpacingBetweenStrips	=    12
topStripsOffset					= 590
topMargin						=   10
bottomMargin					=   10
leftMargin						=   30
rightMargin						=   30
sliderPositionMarkerLineWidth	=	 3
sliderPositionMarkerColor		=  (0,0,0)
activeSliderPositionMarkerColor = {	
	'RGB' : (     0,     0, 255)	, 	# RED
	'HSV' : (255, 255,     0)	, 	# YELLOW
	'HLS' : (     0, 255, 255)	,   }	# CYAN
sliderChangeOnPageUpDown	=   10
sliderChangeOnUpDown		=	 5
# ---
R, G, B 				= 255, 127, 127
colorMode 			= 'RGB'
activeChannelIndex	=  0
# ---
fullscreenMode		=  ''
# =======================================================================

from cv2 import (
	namedWindow						,
		WINDOW_GUI_NORMAL		,
		WINDOW_NORMAL				,
		WINDOW_KEEPRATIO			,
		WINDOW_AUTOSIZE			,
		WINDOW_GUI_EXPANDED		,
	setWindowProperty					,
		WND_PROP_FULLSCREEN		,
			WINDOW_FULLSCREEN		,
	moveWindow						,
	resizeWindow						,
	destroyAllWindows					,
	rectangle							,
	imshow					as imShow	,
	waitKey							,
	setMouseCallback					,
		EVENT_LBUTTONDOWN		,
	cvtColor							,	# cvtcolor( im, COLOR_RGB2HSV_FULL )
#		cvtColor FULL conversions below support 0-255,0-255,0-255 color space
##		To convert single color values make a one pixel image and convert the
##			returned numpy array of uint8 values into an ordinary tuple of integers:
#	 tuple( cvtColor( uint8([[(0,0,0)]]), COLOR_RGB2Lab)[0][0].tolist() ) == (0, 128, 128)
		COLOR_RGB2BGR				,
		COLOR_BGR2RGB				,
		COLOR_RGB2HSV_FULL			,
		COLOR_HSV2RGB_FULL			,
		COLOR_RGB2HLS_FULL			,
		COLOR_HLS2RGB_FULL			,
)
from numpy import (
	zeros								,
	uint8								,
)
if withOutputOfClosestColorName : 
	from webcolors import (
		rgb_to_name						,
		CSS3_HEX_TO_NAMES				,
		hex_to_rgb							,
	)

def updateRGBstripColors() :
	global RstripColors , GstripColors , BstripColors 
	if colorMode == 'RGB' : cvtCOLOR_FLAG = COLOR_RGB2BGR
	if colorMode == 'HLS' : cvtCOLOR_FLAG = COLOR_HLS2RGB_FULL
	if colorMode == 'HSV' : cvtCOLOR_FLAG = COLOR_HSV2RGB_FULL
	cvtColor_retVal = cvtColor( uint8([[(0, G, B)]]), cvtCOLOR_FLAG)[0][0].tolist()
	RstripColors = [ tuple( cvtColor( uint8([[( r, G, B)]]), cvtCOLOR_FLAG)[0][0].tolist() ) for  r  in range(256) ]
	GstripColors = [ tuple( cvtColor( uint8([[(R, g, B)]]), cvtCOLOR_FLAG)[0][0].tolist() ) for g  in range(256) ]
	BstripColors = [ tuple( cvtColor( uint8([[(R, G, b)]]), cvtCOLOR_FLAG)[0][0].tolist() ) for b  in range(256) ]

def updateGUI(im) :
	# global im, R, G, B, activeChannelIndex
	im[:] = (230, 255, 230)
	# Draw border
	rectangle(im, (1, 1), 
				  (widthColorStripColor * 256 + leftMargin + rightMargin - 1, 
				   topStripsOffset + bottomMargin + 3*(heightColorStrip + verticalSpacingBetweenStrips) - 1),
				  (0, 0, 0), 1)
	# Draw color strips and markers
	updateRGBstripColors()
	for channelIndex, (colorsChannelStrip, colorChannelValue) in enumerate([(RstripColors, R), (GstripColors, G), (BstripColors, B)]):
		yOffset = channelIndex * (heightColorStrip + verticalSpacingBetweenStrips)
		# Draw the color strip for the current channel
		for colorIndexInStrip, colorInStrip in enumerate(colorsChannelStrip):
			rectangle(im, 
						  ( leftMargin + colorIndexInStrip * widthColorStripColor		  ,   topStripsOffset + yOffset )						,
						  ( leftMargin + (colorIndexInStrip + 1) * widthColorStripColor	  ,   topStripsOffset + yOffset + heightColorStrip )	,
						  colorInStrip, -1 )
		# Draw the slider marker
		markerColor = activeSliderPositionMarkerColor[colorMode] if activeChannelIndex == channelIndex else sliderPositionMarkerColor
		rectangle(im,
					(leftMargin + colorChannelValue * widthColorStripColor - sliderPositionMarkerLineWidth, 
					topStripsOffset + yOffset - sliderPositionMarkerLineWidth),
					(leftMargin + (colorChannelValue + 1) * widthColorStripColor + sliderPositionMarkerLineWidth, 
					topStripsOffset + yOffset + heightColorStrip + sliderPositionMarkerLineWidth),
					markerColor, 3)
	
	# Draw the large upper color square showing the selected color
	rectangle(im, (leftMargin, topMargin),
				  (leftMargin + 256 * widthColorStripColor, topStripsOffset - 15)	,
				  RstripColors[R]												, 
				  -1	)
	imShow(wID, im)

def onMouse(event, x, y, flags, param):
	global R, G, B, activeChannelIndex
	# Check if clicked inside the upper large square (showing selected color)
	if event == EVENT_LBUTTONDOWN:
		if topMargin <= y <= topStripsOffset - 15 and leftMargin <= x <= leftMargin + 256 * widthColorStripColor:
			print(f"rgb( {R}, {G}, {B} )")
			exit()	##	EXIT
		# Check if clicked in any of the color strips
		else: 
			yOffsetR = topStripsOffset + 0 * (heightColorStrip + verticalSpacingBetweenStrips)
			yOffsetG = topStripsOffset + 1 * (heightColorStrip + verticalSpacingBetweenStrips)
			yOffsetB = topStripsOffset + 2 * (heightColorStrip + verticalSpacingBetweenStrips)
			if yOffsetR <= y <= yOffsetG	:
				R = (x - leftMargin) // widthColorStripColor
			if yOffsetG <= y <= yOffsetB	:
				G = (x - leftMargin) // widthColorStripColor
			if yOffsetB <= y 			:
				B = (x - leftMargin) // widthColorStripColor
			# Make sure that clicks left/right outside the strip are properly handled: 
			R = max(0, min(R, 255)) ; G = max(0, min(G, 255))  ; B = max(0, min(B, 255)) 
			updateGUI(im)

def onKey(key):
	global R, G, B, activeChannelIndex, colorMode, fullscreenMode

	if key == 13 : # Enter to confirm the current color choice 
		b,g,r = RstripColors[R]
		if withOutputOfClosestColorName  : 
			print(f"#{R:02X}{G:02X}{B:02X} rgb({R},{G},{B}) {exactOrClosestCss3colorName((r,g,b))}")
		else : 
			print(f"#{R:02X}{G:02X}{B:02X} rgb({R},{G},{B})")
		exit()	##	EXIT

	elif key == 9:  # Tab key to cycle channels
		activeChannelIndex = (activeChannelIndex + 1) % 3
		
	elif key == ord('r'):  # Switch to RGB mode
		colorMode = 'RGB'
	elif key == ord('h'):  # Switch to HSV mode
		colorMode = 'HSV'
		H = min(180, R)
	elif key == ord('l'):  # Switch to HLS mode
		colorMode = 'HLS'

	elif key == 82:  # Up arrow key : move all slider markes simultaneously
		R = min(255, R + sliderChangeOnUpDown ) 
		G = min(255, G + sliderChangeOnUpDown ) 
		B = min(255, B + sliderChangeOnUpDown ) 
	elif key == 84:  # Down arrow key : move all slider markes simultaneously
		R = max(	0, R - sliderChangeOnUpDown) 
		G = max(	0, G - sliderChangeOnUpDown) 
		B = max(	0, B - sliderChangeOnUpDown) 

	elif key == 81:  # Left arrow
		if activeChannelIndex == 0: R = max(0, R - 1)
		if activeChannelIndex == 1: G = max(0, G - 1)
		if activeChannelIndex == 2: B = max(0, B - 1)
	elif key == 83:  # Right arrow
		if activeChannelIndex == 0: R = min(255, R + 1)
		if activeChannelIndex == 1: G = min(255, G + 1)
		if activeChannelIndex == 2: B = min(255, B + 1)
	elif key == 85:  # Page up
		if activeChannelIndex == 0: R = max(	0, R - sliderChangeOnPageUpDown)
		if activeChannelIndex == 1: G = max(	0, G - sliderChangeOnPageUpDown)
		if activeChannelIndex == 2: B = max(	0, B - sliderChangeOnPageUpDown)
	elif key == 86:  # Page down
		if activeChannelIndex == 0: R = min(255, R + sliderChangeOnPageUpDown)
		if activeChannelIndex == 1: G = min(255, G + sliderChangeOnPageUpDown)
		if activeChannelIndex == 2: B = min(255, B + sliderChangeOnPageUpDown)

	elif key == ord("f") : # key [f] : go Fullscreen
		if fullscreenMode == '' :
			#import os
			#os.system( "notify-send   -u normal   --expire-time 5000   '   colorChoice WINDOW mode'   f'     changed to FULLSCREEN ' " )
			fullscreenMode = 'yes'
			setWindowProperty(wID, WND_PROP_FULLSCREEN, WINDOW_FULLSCREEN);

	updateGUI(im)

def exactOrClosestCss3colorName( RGBtuple ):
	try:
		# Try to find the exact match
		colorName = rgb_to_name( RGBtuple )
		return f"'Css3colorName: {colorName} (exact match)'"
	except ValueError:
		# If no exact match, find the closest color name
		colorName = closestCss3colorName(RGBtuple)
		return f"'Css3ColorName: {colorName} (closest match)'"

def closestCss3colorName( RGB ):
	min_dist = float('inf')
	closestColorName = None
	R,G,B = RGB
	# Check against all CSS3 color names
	for hex_value, colorName in CSS3_HEX_TO_NAMES.items():
		r, g, b = hex_to_rgb(hex_value)
		dist = ( (r - R) ** 2 + (g - G) ** 2 + (b - B) ** 2) ** 0.5
		if dist < min_dist:
			min_dist = dist
			closestColorName = colorName
	return closestColorName

updateRGBstripColors( )
# creating the appropriate sized image for use in updateGUI() : 
im = zeros((topStripsOffset + bottomMargin + 3 * (heightColorStrip + verticalSpacingBetweenStrips), 
			   widthColorStripColor * 256 + leftMargin + rightMargin,	3),	uint8 )
updateGUI(im)

namedWindow(wID, flags=(WINDOW_GUI_NORMAL ) )
setWindowProperty( wID , WND_PROP_FULLSCREEN, WINDOW_FULLSCREEN)
imShow(wID, im)
resizeWindow(wID, windowWidth, windowHeight)
moveWindow(wID, windowXpos, windowYpos)

setMouseCallback(wID, onMouse)

# Main execution loop
while True:
	key = waitKey(0)
	if key == 27 : # Esc ( or mouse click on color square ) EXITs
		break
	onKey(key )

destroyAllWindows()
