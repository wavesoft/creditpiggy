################################################################
# CreditPiggy - Volunteering Computing Credit Bank Project
# Copyright (C) 2015 Ioannis Charalampidis
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
################################################################

from PIL import Image
import urllib, cStringIO

def image_colors(url, default=("#000", "#fff")):
	"""
	Download image from the specified URL and return
	color specifications, such as background average
	and suggested foreground color.
	"""

	try:
		# Download image from URL
		file = cStringIO.StringIO(urllib.urlopen(url).read())
		img = Image.open(file)
	except Exception as e:
		# Re-raise exception if we don't have default
		if default is None:
			raise
			
		# Otherwise return default
		return default

	# Calculate image average
	width, height = img.size

	# Initialize averages
	r = 0
	g = 0
	b = 0
	counter = 0
 
	# Process pixels
	pixels = img.load()
	data = []
	for x in range(width):
		for y in range(height):
			cpixel = pixels[x, y]

			# Skip transparent pixels
			if (len(cpixel) > 3) and (cpixel[3] <= 200):
				continue

			# Average RGB values
			r+=cpixel[0]
			g+=cpixel[1]
			b+=cpixel[2]
			counter+=1

	# compute average RGB values
	rAvg = r/counter
	gAvg = g/counter
	bAvg = b/counter

	# Convert to hex
	b_color = "#%s" % format(rAvg<<16 | gAvg<<8 | bAvg, '06x')
 
	# Get luminance
	o = round( ((rAvg * 299) + (gAvg * 587) + (bAvg * 114)) / 1000 )

	# Pick foreground
	f_color = '#fff'
	if o > 125:
		f_color = '#000'

	# Return fore/back combination
	return (b_color, f_color)
