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

class Emulator:
  def __init__(self):
    pygame.display.flip()

  def opCodes(self,opcode):

    pos1 = opcode[0]
    pos3 = opcode[2]
    pos4 = opcode[3]

    match pos1:
      case '0':
        #00E0 and 00EE

        match pos4:
           case '0':
            #00E0 - clear the display
            return
           
           case 'e':
            #00EE - return from a subroutine, set pc to top of stack then subtract 1 from stack pointer
            return
          
      case '1':
        #1nnn - jump to location at nnn, set pc to nnn
        return 
      
      case '2':
        #2nnn - call subroutine at nnn, increments the stack pointer, puts the current PC on top of the stack ,sets PC to nnn.
        return
      
      case '3':
        #3xkk - skip the next instruction if Vx = kk, checks if Vx = kk if so increment PC by 2
        return
      
      case '4':
        #4xkk - skip the next instruction if Vx != kk, checks if Vx != kk if so increment PC by 2
        return
      
      case '5':
        #5xy0 - skip the next instruction if Vx = Vy, checks if Vx = Vy if so increment PC by 2
        return
      
      case '6':
        #6xkk - puts the value kk in register Vx
        return

      case '7':
        #7xkk - adds value kk to value in register Vx, stores it in Vx
        return

      case '8': 
        #8xy0 8xy1 8xy2 8xy3 8xy4 8xy5 8xy6 8xy7 8xyE

        match pos4:
          case '0':
            #8xy0 - Set Vx = Vy, stores the value of register Vy in register Vx
            return

          case '1':
            #8xy1 - Set Vx = Vx OR Vy, Performs a bitwise OR on the values of Vx and Vy, then stores the result in Vx
            return
          
          case '2':
            #8xy2 - Set Vx = Vx AND Vy, Performs a bitwise AND on the values of Vx and Vy, then stores the result in Vx
            return

          case '3':
            #8xy3 - Set Vx = Vx XOR Vy, Performs a bitwise exclusive OR on the values of Vx and Vy, then stores the result in Vx
            return
          
          case '4':
            #8xy4 - Set Vx = Vx + Vy, set VF = carry, The values of Vx and Vy are added together If the result is greater than 8 bits (i.e., > 255,) VF is set to 1, otherwise 0 Only the lowest 8 bits of the result are kept, and stored in Vx
            return

          case '5':
            #8xy5 - Set Vx = Vx - Vy, set VF = NOT borrow, If Vx > Vy, then VF is set to 1, otherwise 0 Then Vy is subtracted from Vx, and the results stored in Vx
            return
          
          case '6':
            #8xy6 - Set Vx = Vx SHR 1, If the least-significant bit of Vx is 1, then VF is set to 1, otherwise 0. Then Vx is divided by 2.
            return

          case '7':
            #8xy7 - Set Vx = Vy - Vx, set VF = NOT borrow, If Vy > Vx, then VF is set to 1, otherwise 0. Then Vx is subtracted from Vy, and the results stored in Vx.
            return

          case 'e':
            #8xyE - Set Vx = Vx SHL 1, If the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0. Then Vx is multiplied by 2.
            return

      case '9':
        #9xy0 - Skip next instruction if Vx != Vy, The values of Vx and Vy are compared, and if they are not equal, the program counter is increased by 2.
        return 
      
      case 'a':
        #Annn - Set I = nnn, The value of register I is set to nnn
        return

      case 'b':
        #Bnnn - Jump to location nnn + V0, The program counter is set to nnn plus the value of V0
        return
      
      case 'c':
        #Cxkk - Set Vx = random byte AND kk, The interpreter generates a random number from 0 to 255, which is then ANDed with the value kk. The results are stored in Vx. See instruction 8xy2 for more information on AND 
        return
      
      case 'd':
        #Dxyn - Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.
        return

      case 'e':
        #Ex9E ExA1

        match pos4:

          case 'e':
            #Ex9E - Skip next instruction if key with the value of Vx is pressed
            return
          
          case '1':
            #ExA1 - Skip next instruction if key with the value of Vx is not pressed
            return

      case 'f':
        #Fx07 Fx0A Fx18 Fx1E Fx29 Fx33 Fx15 Fx55 Fx65

          match pos4:

            case '7':
              #Fx07 - Set Vx = delay timer value
              return
            
            case 'a':
              #Fx0A - Wait for a key press, store the value of the key in Vx.
              return
            
            case '8':
              #Fx18 - Set sound timer = Vx
              return
            
            case 'e':
              #Fx18 - Set I = I + Vx
              return
            
            case '9':
              #Fx29 - Set I = location of sprite for digit Vx
              return
            
            case '3':
              #Fx33 - Store BCD representation of Vx in memory locations I, I+1, and I+2
              return
            
            case '5':
              #Fx15 Fx55 Fx65

              match pos3:

                case '1':
                  #Fx15 - Set delay timer = Vx
                  return
            
                case '5':
                  #Fx55 - Store registers V0 through Vx in memory starting at location I
                  return
                
                case '6':
                  #Fx65 - Read registers V0 through Vx from memory starting at location I
                  return

      case _:
        print("Invalid OpCode")
      
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
