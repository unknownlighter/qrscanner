import zbar
from PIL import Image, ImageFilter
from math import atan2, degrees

class RecognizedImage(object):
    def __init__(self, pil, symbol, is_modified=False):
        self.pil = pil
        self.symbol = symbol
        self.is_modified = is_modified
    
    def get_title_height(self):
        return max([y for x,y in self.symbol.location])
        
    def crop_title_by_qr(self):
        w, h = self.pil.size
        return self.pil.crop((0, self.get_title_height(), w, h))

class QRScannerError(Exception):
    pass

class QRScanner(object):
    def __init__(self):
        self.scanner = zbar.ImageScanner()
        self.scanner.parse_config('disable')
        self.scanner.set_config(zbar.Symbol.QRCODE, zbar.Config.ENABLE, 1)
    
    def recognize_from_pil(self, pil):
        width, height = pil.size
        raw = pil.tobytes()
        image = zbar.Image(width, height, 'Y800', raw)
        self.scanner.scan(image)
        return iter(image.symbols).next() if image.symbols else None
    
    def get_rotation_angle(self, symbol):
        x1, y1 = symbol.location[0]
        x2, y2 = symbol.location[1]
        return degrees(atan2(x1-x2, y2-y1))
    
    def rotate_image(self, pil, angle):
        return pil.rotate(angle, resample=Image.BILINEAR, expand=True).filter(ImageFilter.SHARPEN)
    
    def scan(self, image_path):
        pil = Image.open(image_path).convert('L')
        
        angle = 0
        symbol = self.recognize_from_pil(pil)
        while not symbol and angle<=150:
            angle += 30
            rotated_pil = self.rotate_image(pil, -angle)
            symbol = self.recognize_from_pil(rotated_pil)
            
        if not symbol:
            raise QRScannerError('could not recognize qr-code')
        
        rotatation_angle = self.get_rotation_angle(symbol) - angle
        up_oriented_pil = pil
        is_modified = False
        if abs(rotatation_angle) > 5:
            up_oriented_pil = self.rotate_image(pil, rotatation_angle)
            symbol = self.recognize_from_pil(up_oriented_pil)
            is_modified = True
        
        if not symbol:
            raise QRScannerError('could not orient image')
        
        return RecognizedImage(up_oriented_pil, symbol, is_modified)
