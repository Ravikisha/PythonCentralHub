class ZodiacSignPredictor:
    def __init__(self):
        self.signs = [
            (1, 20, 'Aquarius'), (2, 19, 'Pisces'), (3, 21, 'Aries'), (4, 20, 'Taurus'),
            (5, 21, 'Gemini'), (6, 21, 'Cancer'), (7, 23, 'Leo'), (8, 23, 'Virgo'),
            (9, 23, 'Libra'), (10, 23, 'Scorpio'), (11, 22, 'Sagittarius'), (12, 22, 'Capricorn')
        ]

    def predict(self, month, day):
        for m, d, sign in self.signs:
            if (month == m and day >= d) or (month == m % 12 + 1 and day < self.signs[m % 12][1]):
                print(f"Zodiac sign: {sign}")
                return sign
        print("Invalid date.")
        return None

    def demo(self):
        self.predict(3, 25)
        self.predict(7, 30)

if __name__ == "__main__":
    print("Zodiac Sign Predictor Demo")
    predictor = ZodiacSignPredictor()
    predictor.demo()
