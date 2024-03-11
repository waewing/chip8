import logging
import pygame

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

#Initiliaze components
def initialize(self):
  self.clear()

  self.memory = [0]*4096
  self.registers = [0]*16
  self.keyInputs = [0]*16
  self.display = [0]*64*32
  self.delayTimer = 0
  self.soundTimer = 0
  self.shouldDraw = False
  
  self.index = 0
  self.opcode = 0
  
  #Program Counter Starts at 0x200 of memory
  self.pc = 0x200
  self.sp = 0
  self.stack = []

  self.fonts = [
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

  self.memory[:len(self.fonts)] = self.fonts

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
