from typing import List, Callable
from collections import defaultdict
from PIL import Image

class signedPixel:
    def __init__(self, red: int, green: int, blue: int):
        self.red = red
        self.green = green
        self.blue = blue

class NonUniformQuantizer:
    def encode(self, image: List[signedPixel], bitsPerColor: int) -> List[signedPixel]:
        v1 = self.quantize(image, lambda p: p.red, bitsPerColor)
        v2 = self.quantize(image, lambda p: p.green, bitsPerColor)
        v3 = self.quantize(image, lambda p: p.blue, bitsPerColor)

        encodedImage = []
        for i in range(len(image)):
            p = image[i]
            encodedPixel = signedPixel(v1[i], v2[i], v3[i])
            encodedImage.append(encodedPixel)

        return encodedImage

    def quantize(self, image: List[signedPixel], cast: Callable[[signedPixel], int], bits: int) -> List[int]:
        if bits > 8:
            return []

        histogram = defaultdict(int)
        for pixel in image:
            quantizedPixel = cast(pixel)
            histogram[quantizedPixel] += 1

        numOfValues = (255 >> (8 - bits)) + 1

        quantizedImage = sorted(histogram.keys())

        newValues = {}

        expectedProbability = len(image) // numOfValues

        def findQuant(start, end):
            result = 0
            tempSum = 0

            for it in range(start, end):
                tempSum += histogram[quantizedImage[it]]
                result += quantizedImage[it] * histogram[quantizedImage[it]]
            if tempSum == 0:
                return 0
            return result // tempSum

        start = 0
        end = 0
        temp = 0

        while end < len(quantizedImage):
            temp += quantizedImage[end]
            if temp >= expectedProbability:
                result = findQuant(start, end + 1)

                for it in range(start, end + 1):
                    newValues[quantizedImage[it]] = result
                start = end + 1
                continue
            end += 1

        result = []
        for pixel in image:
            result.append(newValues[cast(pixel)])

        return result

    def decode(self, encoded: List[signedPixel]) -> List[signedPixel]:
        decoded = encoded
        return decoded

# Przykład użycia:
quantizer = NonUniformQuantizer()

# Wczytaj obraz TGA
image_path = "hp.tga"  # Ścieżka do obrazu TGA
img = Image.open(image_path)
img = img.convert("RGB")
width, height = img.size
pixels = list(img.getdata())

bitsPerColor = 6  # Liczba bitów na kanał koloru
encoded_image = quantizer.encode([signedPixel(r, g, b) for r, g, b in pixels], bitsPerColor)

# Możesz teraz przetwarzać "encoded_image" i wykonywać operacje na nim
