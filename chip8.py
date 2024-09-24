import logging
import pygame
import time
import sys
import random
import os

#Chip 8 Specifications
#---------------------------------------------------------------------
#Memory: 4096 bytes
#Registers: 16 8bit registers
#Keyboard: 16 input keyboard
#Display: 64x32 pixel display
#Sound: 2 timers delay timer to 0 and sound timer to 0
#Index Counter to 0
#PC Counter to 0x200 since first 512 bytes are reserved
#Stack []

#0x000 (0) - 0x1FF (511) interpreter
#0x050 (80) - 0x0A0 (160) font set
#0x200 (512) - 0xFFF (4095) rom and ram

#---------------------------------------------------------------------


#Emulator Architecture

class Register:
    def __init__(self, bits):
        self.value = 0
        self.bits = bits
    
    def checkCarry(self):
        hexValue = hex(self.value)[2:]

        if len(hexValue) > self.bits / 4:
            self.value = int(hexValue[-int(self.bits / 4):], 16)
            return 1
        
        return 0
    
    def checkBorrow(self):
        if self.value < 0:
            self.value = abs(self.value)
            return 0
        
        return 1
    
    def readValue(self):
        return hex(self.value)
    
    def setValue(self, value):
        self.value = value

class DelayTimer:
  def __init__ (self):
    self.timer = 0

  def countDown(self):
    if self.timer > 0:
      self.timer-= 1
    
  def setTimer(self, value):
    self.timer = value

  def readTimer(self):
    return self.timer

class SoundTimer:
  def __init__ (self):
    DelayTimer.__init__(self)

  def beep(self):
    if self.timer > 1:
      os.system('play --no-show-progress --null --channels 1 synth %s triangle %f' % (self.timer / 60, 440))
      self.timer = 0

class Emulator:
  def __init__(self):
    self.clear()

    self.Memory = [0x0]*4096

    fonts = [
    0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
    0x20, 0x60, 0x20, 0x20, 0x70, # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
    0x90, 0x90, 0xF0, 0x10, 0x10, # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
    0xF0, 0x10, 0x20, 0x40, 0x40, # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90, # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
    0xF0, 0x80, 0x80, 0x80, 0xF0, # C
    0xE0, 0x90, 0x90, 0x90, 0xE0, # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
    0xF0, 0x80, 0xF0, 0x80, 0x80  # F
  ]
    
    for i in range(len(fonts)):
      self.Memory[i] = fonts[i]

    self.Registers = []
    for i in range(16):
          self.Registers.append(Register(8))

    self.KeyInputs = Register(16)

    self.pc = 0x200

    self.delayTimer = DelayTimer()
    self.soundTimer = SoundTimer()

    pygame.init()
    pygame.time.set_timer(pygame.USEREVENT+1, int(1000 / 60))

    #Userinput - 1(1), 2(2), 3(3), 4(C), q(4), w(5), e(6), r(D), a(7), s(8), d(9), f(E), z(a), x(0), c(B), v(F)
    self.keys = []
    for i in range(0, 16):
          self.keys.append(False)
    self.keyDict = {
        49 : 1,
        50 : 2,
        51 : 3,
        52 : 0xc,
        113 : 4,
        119 : 5,
        101 : 6,
        114 : 0xd,
        97 : 7,
        115 : 8,
        100 : 9,
        102 : 0xe,
        122 : 0xa,
        120 : 0,
        99 : 0xb,
        118 : 0xf
    }

    #64 x 32 display
    self.grid = []
    for i in range(32):
        line = []
        for j in range(64):
            line.append(0)
        self.grid.append(line)
    self.emptyGrid = self.grid[:]
    self.zeroColor = [0, 0, 50]
    self.oneColor = [255, 255, 255]

    self.size = 10
    width = 64
    height = 32
    self.screen = pygame.display.set_mode([width * self.size, height * self.size])
    self.screen.fill(self.oneColor)
    
    pygame.display.flip()

  def opCodes(self,opcode):

    pos1 = opcode[0]
    pos3 = opcode[2]
    pos4 = opcode[3]

    match pos1:
      #0 Complete
      case '0':
        #00E0 and 00EE

        match pos4:
           case '0':
            #00E0 - clear the display
            self.clear()
           
           case 'e':
            #00EE - return from a subroutine, set pc to top of stack then subtract 1 from stack pointer
            self.pc = self.stack.pop()

      #1 Complete    
      case '1':
        #1nnn - jump to location at nnn, set pc to nnn
        self.pc = int(opcode[1:],16) - 2 
      
      #2 Complete
      case '2':
        #2nnn - call subroutine at nnn, increments the stack pointer, puts the current PC on top of the stack ,sets PC to nnn.
        self.stack.append(self.pc)
        self.pc = int(opcode[1:],16) - 2 
        
      #Complete
      case '3':
        #3xnn - skip the next instruction if Vx = nn, checks if Vx = nn if so increment PC by 2
        vX = int(opcode[1],16)
        nn = int(opcode[2:],16)

        if self.Registers[vX].value == nn:
          self.pc += 2
      
      #Complete
      case '4':
        #4xkk - skip the next instruction if Vx != kk, checks if Vx != kk if so increment PC by 2
        vX = int(opcode[1],16)
        nn = int(opcode[2:],16)

        if self.Registers[vX].value != nn:
          self.pc += 2
      
      #Complete
      case '5':
        #5xy0 - skip the next instruction if Vx = Vy, checks if Vx = Vy if so increment PC by 2
        vX = int(opcode[1],16)
        vY = int(opcode[2],16)

        if self.Registers[vX].value == self.Registers[vY].value:
          self.pc += 2
      
      #Complete
      case '6':
        #6xnn - puts the value nn in register Vx
        vX = int(opcode[1],16)
        nn = int(opcode[2:],16)

        self.Registers[vX].value = nn

      #Complete
      case '7':
        #7xnn - adds value nn to value in register Vx, stores it in Vx
        vX = int(opcode[1],16)
        nn = int(opcode[2:],16)
        self.Registers[vX].value += vX
        self.Registers.checkCarry()

      #Complete
      case '8': 
        #8xy0 8xy1 8xy2 8xy3 8xy4 8xy5 8xy6 8xy7 8xyE

        match pos4:
          #Complete
          case '0':
            #8xy0 - Set Vx = Vy, stores the value of register Vy in register Vx
            vX = int(opcode[1],16)
            vY = int(opcode[2],16)
            self.Registers[vX].value = self.Registers[vY].value

          #Complete
          case '1':
            #8xy1 - Set Vx = Vx OR Vy, Performs a bitwise OR on the values of Vx and Vy, then stores the result in Vx
            vX = int(opcode[1],16)
            vY = int(opcode[2],16)

            self.Registers[vX].value = self.Registers[vX].value | self.Registers[vY].value
          
          #Complete
          case '2':
            #8xy2 - Set Vx = Vx AND Vy, Performs a bitwise AND on the values of Vx and Vy, then stores the result in Vx
            vX = int(opcode[1],16)
            vY = int(opcode[2],16)

            self.Registers[vX].value = self.Registers[vX].value & self.Registers[vY].value

          #Complete
          case '3':
            #8xy3 - Set Vx = Vx XOR Vy, Performs a bitwise exclusive OR on the values of Vx and Vy, then stores the result in Vx
            vX = int(opcode[1],16)
            vY = int(opcode[2],16)

            self.Registers[vX].value = self.Registers[vX].value ^ self.Registers[vY].value
          
          #Complete
          case '4':
            #8xy4 - Set Vx = Vx + Vy, set VF = carry, The values of Vx and Vy are added together If the result is greater than 8 bits (i.e., > 255,) VF is set to 1, otherwise 0 Only the lowest 8 bits of the result are kept, and stored in Vx
            vX = int(opcode[1],16)
            vY = int(opcode[2],16)

            self.Registers[vX].value += self.Registers[vY].value
            self.Registers[0xf].value = self.Registers[vX].checkCarry()

          #Complete
          case '5':
            #8xy5 - Set Vx = Vx - Vy, set VF = NOT borrow, If Vx > Vy, then VF is set to 1, otherwise 0 Then Vy is subtracted from Vx, and the results stored in Vx
            vX = int(opcode[1],16)
            vY = int(opcode[2],16)

            self.Registers[vX].value -= self.Registers[vY].value
            self.Registers[0xf].value = self.Registers[vX].checkBorrow()
          
          #Complete
          case '6':
            #8xy6 - Set Vx = Vx SHR 1, If the least-significant bit of Vx is 1, then VF is set to 1, otherwise 0. Then Vx is divided by 2.
            vX = int(opcode[1],16)
            minBit = int(bin(self.Registers[vX].value)[-1])

            self.Registers[vX].value = self.Registers[vX].value >> 1
            self.Registers[0xf].value = minBit
          
          #Complete
          case '7':
            #8xy7 - Set Vx = Vy - Vx, set VF = NOT borrow, If Vy > Vx, then VF is set to 1, otherwise 0. Then Vx is subtracted from Vy, and the results stored in Vx.
            vX = int(opcode[1],16)
            vY = int(opcode[2],16)

            self.Registers[vX].value = self.Registers[vY].value - self.Registers[vX].value 
            self.Registers[0xf].value = self.Registers[vX].checkBorrow()

          #Complete
          case 'e':
            #8xyE - Set Vx = Vx SHL 1, If the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0. Then Vx is multiplied by 2.
            vX = int(opcode[1],16)
            maxBit = int(bin(self.Registers[vX].value)[2])

            self.Registers[vX].value = self.Registers[vX].value << 1
            self.Registers[0xf].value = maxBit

      #Complete
      case '9':
        #9xy0 - Skip next instruction if Vx != Vy, The values of Vx and Vy are compared, and if they are not equal, the program counter is increased by 2.
        vX = int(opcode[1],16)
        vY = int(opcode[2],16)

        if self.Registers[vX].value != self.Registers[vY].value:
          self.pc += 2
      
      #Complete
      case 'a':
        #Annn - Set I = nnn, The value of register I is set to nnn
        nnn = int(opcode[1:],16)

        self.KeyInputs.value = nnn

      #Complete
      case 'b':
        #Bnnn - Jump to location nnn + V0, The program counter is set to nnn plus the value of V0
        nnn = int(opcode[1:],16)

        self.pc = self.Registers[0].value + nnn - 2
      
      #Complete
      case 'c':
        #Cxnn - Set Vx = random byte AND nn, The interpreter generates a random number from 0 to 255, which is then ANDed with the value nn. The results are stored in Vx. See instruction 8xy2 for more information on AND 
        vX = int(opcode[1],16)
        nnn = int(opcode[2:],16)

        rand = random.randint(0,255)

        self.Registers[vX].value = nnn & rand
      
      #Complete
      case 'd':
        #Dxyn - Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.
        vX = int(opcode[1],16)
        vY = int(opcode[2],16)
        n = int(opcode[3],16)

        I = self.KeyInputs.value
        sprite = self.Memory[I: I+n]

        for i in range(len(sprite)):
          if type(sprite[i]) == str:
            sprite[i] = int(sprite[i], 16)
        
        if self.draw(self.Registers[vX].value, self.Registers[vY].value, sprite):
          self.Registers[0xf].value = 1
        else:
          self.Registers[0xf].value = 0

      #Complete
      case 'e':
        #Ex9E ExA1

        match pos4:
          
          #Complete
          case 'e':
            #Ex9E - Skip next instruction if key with the value of Vx is pressed
            vX = int(opcode[1],16)
            key = self.Registers[vX].value
            if self.keys[key]:
              self.pc += 2
          
          #Complete
          case '1':
            #ExA1 - Skip next instruction if key with the value of Vx is not pressed
            vX = int(opcode[1],16)
            key = self.Registers[vX].value
            if not self.keys[key]:
              self.pc += 2

      #Complete
      case 'f':
        #Fx07 Fx0A Fx18 Fx1E Fx29 Fx33 Fx15 Fx55 Fx65

          match pos4:
            
            #Complete
            case '7':
              #Fx07 - Set Vx = delay timer value
              vX = int(opcode[1],16)
              self.Registers[vX].value = self.delayTimer.readTimer()
            
            #Complete
            case 'a':
              #Fx0A - Wait for a key press, store the value of the key in Vx.
              vX = int(opcode[1],16)
              key = None

              while True:
                self.keyHandler()
                isKeyPress = False
                
                for i in range(len(self.keys)):
                  if self.keys[i]:
                    key = i
                    isKeyPress = True

                if isKeyPress:
                  break

              self.Registers[vX].value = key
            
            #Complete
            case '8':
              #Fx18 - Set sound timer = Vx
              vX = int(opcode[1],16)
              val = self.Registers[vX].value
              self.soundTimer.setTimer(val)
            
            #Complete
            case 'e':
              #Fx1e - Set I = I + Vx
              vX = int(opcode[1],16)
              self.KeyInputs.value += self.Registers[vX].value
            
            #Complete
            case '9':
              #Fx29 - Set I = location of sprite for digit Vx
              vX = int(opcode[1],16)
              value = self.Registers[vX].value

              self.KeyInputs.value = value * 5
            
            #Complete
            case '3':
              #Fx33 - Store BCD representation of Vx in memory locations I, I+1, and I+2
              vX = int(opcode[1],16)
              val = str(self.Registers[vX].value)

              fillNum = 3 - len(val)
              val = '0' * fillNum + val

              for i in range(len(val)):
                self.Memory[self.KeyInputs.value + i] = int(val[i])
            
            #Complete
            case '5':
              #Fx15 Fx55 Fx65

              match pos3:
                
                #Complete
                case '1':
                  #Fx15 - Set delay timer = Vx
                  vX = int(opcode[1],16)
                  val = self.Registers[vX].value

                  self.delayTimer.setTimer(val)

                #Complete
                case '5':
                  #Fx55 - Store registers V0 through Vx in memory starting at location I
                  vX = int(opcode[1],16)
                  for i in range(0, vX + 1):
                    self.Memory[self.KeyInputs.value + i] = self.Registers[i].value
                
                #Complete
                case '6':
                  #Fx65 - Read registers V0 through Vx from memory starting at location I
                  vX = int(opcode[1],16)
                  for i in range(0, vX + 1):
                    self.Registers[i].value = self.Memory[self.KeyInputs.value + i]

      case _:
        print("Invalid OpCode")

    self.pc+=2 
  
  def execution(self):
    index = self.pc
    high = self.hexHandler(self.Memory[index])
    low = self.hexHandler(self.Memory[index + 1])

    opcode = high + low

    self.opCodes(opcode)

  
#read in a rom using binary bit by bit into memory
def loadGame(self,rom_path):
  logging.log("Loading %s..." % rom_path)
  binary = open("rom_path","rb").read()
  for i in range(len(binary)-1):
    self.memory[0x200 + i] = ord(binary[i])


def main(self):

  #create render system and input callbacks
  self.setupDisplay()
  self.setupInput()


  #initialize chip8 system and load game into memory
  self.initialize()
  print(initialize.memory)
  self.loadGame('pong')


  #Emulation loop
  while True:
    self.emulateCycle()

    if(self.drawFlag):
      self.drawGraphics()

    self.setKeys()
  
  return
