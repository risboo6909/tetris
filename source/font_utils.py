import os
import sys

import pygame


def load_font(size, base_dir):
	"""Use original TTF when possible, bitmap only as final fallback."""
	safe_size = max(10, int(size))
	font_candidates = []
	font_mode = os.environ.get("TETRIS_FONT_MODE", "auto").lower()
	prefer_bitmap = (font_mode == "bitmap") or (font_mode == "auto" and sys.platform == "darwin")

	def add_font(path):
		try:
			if path and os.path.exists(path):
				font_candidates.append(pygame.font.Font(path, safe_size))
		except Exception:
			pass

	# Original bundled font (preferred)
	add_font(str(base_dir / "font" / "freesansbold.ttf"))

	# Common Windows and macOS font files
	add_font("C:\\Windows\\Fonts\\arial.ttf")
	add_font("C:\\Windows\\Fonts\\segoeui.ttf")
	add_font("/System/Library/Fonts/Supplemental/Arial.ttf")
	add_font("/System/Library/Fonts/Helvetica.ttc")

	# Generic fallbacks
	try:
		match = pygame.font.match_font("arial")
		add_font(match)
	except Exception:
		pass
	try:
		font_candidates.append(pygame.font.Font(None, safe_size))
	except Exception:
		pass

	def is_usable_font(font_obj):
		"""Reject fonts that render every glyph as the same tofu rectangle."""
		try:
			a_surf = font_obj.render("A", 1, (255, 255, 255))
			b_surf = font_obj.render("B", 1, (255, 255, 255))
			if(a_surf.get_width() <= 0 or a_surf.get_height() <= 0):
				return(False)
			if(b_surf.get_width() <= 0 or b_surf.get_height() <= 0):
				return(False)
			return(pygame.image.tostring(a_surf, "RGBA") != pygame.image.tostring(b_surf, "RGBA"))
		except pygame.error:
			return(False)

	usable_fonts = []
	for f in font_candidates:
		if(font_mode == "original"):
			usable_fonts.append(f)
			continue
		if(is_usable_font(f)):
			usable_fonts.append(f)

	patterns = {
		"0": ["01110","10001","10011","10101","11001","10001","01110"],
		"1": ["00100","01100","00100","00100","00100","00100","01110"],
		"2": ["01110","10001","00001","00010","00100","01000","11111"],
		"3": ["11110","00001","00001","01110","00001","00001","11110"],
		"4": ["00010","00110","01010","10010","11111","00010","00010"],
		"5": ["11111","10000","10000","11110","00001","00001","11110"],
		"6": ["01110","10000","10000","11110","10001","10001","01110"],
		"7": ["11111","00001","00010","00100","01000","01000","01000"],
		"8": ["01110","10001","10001","01110","10001","10001","01110"],
		"9": ["01110","10001","10001","01111","00001","00001","01110"],
		"A": ["01110","10001","10001","11111","10001","10001","10001"],
		"B": ["11110","10001","10001","11110","10001","10001","11110"],
		"C": ["01110","10001","10000","10000","10000","10001","01110"],
		"D": ["11110","10001","10001","10001","10001","10001","11110"],
		"E": ["11111","10000","10000","11110","10000","10000","11111"],
		"F": ["11111","10000","10000","11110","10000","10000","10000"],
		"G": ["01110","10001","10000","10111","10001","10001","01110"],
		"H": ["10001","10001","10001","11111","10001","10001","10001"],
		"I": ["01110","00100","00100","00100","00100","00100","01110"],
		"J": ["00001","00001","00001","00001","10001","10001","01110"],
		"K": ["10001","10010","10100","11000","10100","10010","10001"],
		"L": ["10000","10000","10000","10000","10000","10000","11111"],
		"M": ["10001","11011","10101","10001","10001","10001","10001"],
		"N": ["10001","11001","10101","10011","10001","10001","10001"],
		"O": ["01110","10001","10001","10001","10001","10001","01110"],
		"P": ["11110","10001","10001","11110","10000","10000","10000"],
		"Q": ["01110","10001","10001","10001","10101","10010","01101"],
		"R": ["11110","10001","10001","11110","10100","10010","10001"],
		"S": ["01111","10000","10000","01110","00001","00001","11110"],
		"T": ["11111","00100","00100","00100","00100","00100","00100"],
		"U": ["10001","10001","10001","10001","10001","10001","01110"],
		"V": ["10001","10001","10001","10001","10001","01010","00100"],
		"W": ["10001","10001","10001","10001","10101","11011","10001"],
		"X": ["10001","10001","01010","00100","01010","10001","10001"],
		"Y": ["10001","10001","01010","00100","00100","00100","00100"],
		"Z": ["11111","00001","00010","00100","01000","10000","11111"],
		":": ["00000","00100","00100","00000","00100","00100","00000"],
		"!": ["00100","00100","00100","00100","00100","00000","00100"],
		" ": ["00000","00000","00000","00000","00000","00000","00000"],
	}

	class BitmapFont:
		def __init__(self, px_size):
			self.scale = max(1, int(px_size) // 7)
			self.char_w = 5 * self.scale
			self.char_h = 7 * self.scale
			self.gap = self.scale

		def size(self, text):
			text = str(text).upper()
			w = len(text) * (self.char_w + self.gap)
			return (max(1, w), self.char_h)

		def render(self, text, antialias, color):
			_ = antialias
			text = str(text).upper()
			width, height = self.size(text)
			surf = pygame.Surface((width, height), pygame.SRCALPHA)
			x = 0
			for ch in text:
				pat = patterns.get(ch, patterns[" "])
				for row in range(7):
					for col in range(5):
						if pat[row][col] == "1":
							pygame.draw.rect(
								surf,
								color,
								pygame.Rect(x + col * self.scale, row * self.scale, self.scale, self.scale),
							)
				x += self.char_w + self.gap
			return surf

	class SafeFont:
		def __init__(self, fonts, bitmap_font):
			self.fonts = fonts
			self.bitmap_font = bitmap_font

		def size(self, text):
			for fnt in self.fonts:
				try:
					w, h = fnt.size(str(text))
					if w > 0 and h > 0:
						return (w, h)
				except pygame.error:
					continue
			return self.bitmap_font.size(text)

		def render(self, text, antialias, color):
			for fnt in self.fonts:
				try:
					surf = fnt.render(str(text), antialias, color)
					if surf.get_width() > 0 and surf.get_height() > 0:
						return surf
				except pygame.error:
					continue
			return self.bitmap_font.render(text, antialias, color)

	if(prefer_bitmap):
		return BitmapFont(safe_size)

	return SafeFont(usable_fonts, BitmapFont(safe_size))
