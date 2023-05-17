# m209 : The base Class of M209

import string

M209_ALPHABET_LIST = string.ascii_uppercase
M209_ALPHABET_SET = set(string.ascii_uppercase)
CIPHER_TABLE = list(reversed(string.ascii_uppercase))

# historically accurate
WHEEL_DATA = [
    ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 15),
    ("ABCDEFGHIJKLMNOPQRSTUVXYZ", 14),
    ("ABCDEFGHIJKLMNOPQRSTUVX", 13),
    ("ABCDEFGHIJKLMNOPQRSTU", 12),
    ("ABCDEFGHIJKLMNOPQRS", 11),
    ("ABCDEFGHIJKLMNOPQ", 10),
]


class Wheel:
    def __init__(self, letters, guide_offset, effective_pins=""):
        self.letters = letters
        self.size = len(self.letters)
        self.letter_offsets = {letters[i]: i for i in range(self.size)}
        self.pins = [0] * self.size
        self.effective_pins = ''
        self.guide_offset = guide_offset
        self.pos = 0

        self.set_pins(effective_pins)

    def reset_pins(self):
        self.pins = [0] * self.size
        self.effective_pins = ''

    def set_pins(self, effective_pins):
        self.reset_pins()

        for letter in effective_pins:
            n = self.letter_offsets[letter]
            self.pins[n] = 1

        self.effective_pins = effective_pins

    def rotate(self, steps=1):
        self.pos = (self.pos + steps) % self.size

    def display(self):
        return self.letters[self.pos]

    def guide_letter(self):
        n = (self.pos + self.guide_offset) % self.size
        return self.letters[n]

    def is_effective(self):
        n = (self.pos + self.guide_offset) % self.size
        return self.pins[n]

    def set_pos(self, c):
        self.pos = self.letter_offsets[c]


class Drum:
    # NUM_BARS = 27

    def __init__(self, lug_key=""):
        self.lugs = []
        self.set_lugs(lug_key)

    def set_lugs(self, lug_key):
        self.lugs = []
        for i in lug_key.split():
            repeat = 1
            lug_pair = i
            try:
                lug_pair, repeat = i.split('*')
            except:
                pass

            for j in range(int(repeat)):
                self.lugs.append(list(map(int, lug_pair.split('-'))))

    def rotate(self, pins):
        count = 0
        for lug_pair in self.lugs:
            for index in lug_pair:
                if index != 0 and pins[index - 1]:
                    count += 1
                    break

        return count


class M209:
    def __init__(self, lugs="", pin_list=None):
        self.wheels = [Wheel(*args) for args in WHEEL_DATA]
        self.drum = Drum(lugs)
        self.set_all_pins(pin_list)
        self.letter_counter = 0

    def set_pins(self, n, effective_pins):
        self.wheels[n].set_pins(effective_pins)

    def set_all_pins(self, pin_list):
        if pin_list is None:
            for wh in self.wheels:
                wh.set_pins("")
        else:
            for i in range(6):
                self.wheels[i].set_pins(pin_list[i])

    def set_key_wheel(self, n, c):
        self.wheels[n].set_pos(c)

    def set_key_wheels(self, s):
        for n in range(6):
            self.wheels[n].set_pos(s[n])

    def prepare(self, ext_key, letter):
        self.set_key_wheels(ext_key)
        tmp = self.encrypt(letter * 12)
        self.reset()
        wh_num = 0
        ind = 0
        while wh_num != 6:
            if WHEEL_DATA[wh_num][0].count(tmp[ind]) != 0:
                self.set_key_wheel(wh_num, tmp[ind])
                wh_num += 1
            ind += 1

    def encrypt(self, plaintext="A"):
        ciphertext = ""
        for p in plaintext:
            if p == ' ':
                p = 'Z'
            ciphertext += self._cipher(p)

        return ciphertext

    def decrypt(self, ciphertext):
        plaintext = ""
        for c in ciphertext:
            new_c = self._cipher(c)
            if new_c == 'Z':
                new_c = ' '
            plaintext += new_c
        return plaintext

    def _cipher(self, c):
        pins = [wh.is_effective() for wh in self.wheels]
        count = self.drum.rotate(pins)

        for wh in self.wheels:
            wh.rotate()

        self.letter_counter += 1

        return CIPHER_TABLE[(ord(c) - ord('A') - count) % 26]

    def reset(self):
        for wh in self.wheels:
            wh.rotate(-self.letter_counter)
        self.letter_counter = 0
