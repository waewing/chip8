class Register {
  constructor(bits){
    this.value = 0
    this.bits = bits
  }

  checkCarry(){
    hexValue = this.value.toString(16)

    if(hexValue.length > this.bits/4){
      this.value = parseInt(hexValue.slice(-(this.bits / 4)), 16)
      return 1
    }

    return 0
  }

  checkBorrow(){
    if (this.value < 0){
      this.value = Math.abs(this.value)
      return 0
    }

    return 1
  }

  readValue(){
    return parseInt(this.value, 16)
  }

  setValue(value){
    this.value = value
  }
}

class DelayTimer {
  constructor(){
    this.timer = 0
  }

  countDown(){
    if( this.timer > 0){
      this.timer -= 1
    }
  }

  setTimer(value){
    this.timer = value
  }

  readTimer(){
    return this.timer
  }
}

class SoundTimer extends DelayTimer{
  constructor(){
    super()
  }

  beep(){
    if (this.timer > 1){
      //Need to add beep
      this.timer = 0
    }
  }
}
class Emulator {
  constructor(){
    this.Memory = new Array(4096).fill(0x0)
    
    fonts = [
        0xF0, 0x90, 0x90, 0x90, 0xF0, // 0
        0x20, 0x60, 0x20, 0x20, 0x70, // 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0, // 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0, // 3
        0x90, 0x90, 0xF0, 0x10, 0x10, // 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0, // 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0, // 6
        0xF0, 0x10, 0x20, 0x40, 0x40, // 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0, // 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0, // 9
        0xF0, 0x90, 0xF0, 0x90, 0x90, // A
        0xE0, 0x90, 0xE0, 0x90, 0xE0, // B
        0xF0, 0x80, 0x80, 0x80, 0xF0, // C
        0xE0, 0x90, 0x90, 0x90, 0xE0, // D
        0xF0, 0x80, 0xF0, 0x80, 0xF0, // E
        0xF0, 0x80, 0xF0, 0x80, 0x80  // F
        ]
    
    for (let i = 0; i < fonts.length; i++){
        this.Memory[i] = fonts[i]
    }
    
    this.Registers = new Array(16).fill(Register(8))

    this.KeyInputs = Register(16)

    this.pc = 0x200
    this.stack = []
    self.delayTimer = DelayTimer()
    self.soundTimer = SoundTimer()

    /*
    pygame.init()
    pygame.time.set_timer(pygame.USEREVENT+1, int(1000 / 60))
    */

    this.keys = new Array(16).fill(false)
    this.keyDict = {
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
    
    this.grid = new Array(32).fill(new Array(64).fill(0))
    this.emptyGrid = JSON.parse(JSON.stringify(this.grid))
    this.zeroColor = [0, 0, 50]
    this.oneColor = [255, 255, 255]

    this.size = 10
    width = 64
    height = 32
    /*
    self.screen = pygame.display.set_mode([width * self.size, height * self.size])
    self.screen.fill(self.oneColor)
    
    pygame.display.flip()
    */
    }
  
  opCodes(opcode){
    pos1 = opcode[0]
    pos3 = opcode[2]
    pos4 = opcode[3]

    switch(pos1){
      case '0':
        //00E0 and 00EE

        switch(pos4){
          case '0':
            //00E0 - clear the display
            this.clear()
            break;
        
          case 'e':
            //00EE - return from a subroutine, set pc to top of stack then subtract 1 from stack pointer
            this.pc = this.stack.pop()
            break;
        }
        break;
    
      case '1':
        //1nnn - jump to location at nnn, set pc to nnn
        this.pc = parseInt(opcode.slice(1), 16) - 2
        break;
    
      case '2':
        //2nnn - call subroutine at nnn, increments the stack pointer, puts the current PC on top of the stack ,sets PC to nnn.
        this.stack.append(this.pc)
        this.pc = parseInt(opcode.slice(1), 16) - 2
        break;
    
      case '3':
        //3xnn - skip the next instruction if Vx = nn, checks if Vx = nn if so increment PC by 2
        vX = parseInt(opcode[1], 16)
        nn = parseInt(opcode.slice(2), 16)

        if(this.Registers[vX].value == nn){
          this.pc += 2
        }
        break;
    
      case '4':
        //4xkk - skip the next instruction if Vx != kk, checks if Vx != kk if so increment PC by 2
        vX = parseInt(opcode[1], 16)
        nn = parseInt(opcode.slice(2), 16)

        if(this.Registers[vX].value != nn){
          this.pc += 2
        }
        break;
    
      case '5':
        //5xy0 - skip the next instruction if Vx = Vy, checks if Vx = Vy if so increment PC by 2
        vX = parseInt(opcode[1], 16)
        vY = parseInt(opcode[2], 16)

        if(this.Registers[vX].value == this.Registers[vY].value){
          this.pc += 2
        }
        break;
      
      case '6':
        //6xnn - puts the value nn in register Vx
        vX = parseInt(opcode[1], 16)
        nn = parseInt(opcode.slice(2),16)

        this.Registers[vX].value = nn
        break;
      
      case '7':
        //7xnn - adds value nn to value in register Vx, stores it in Vx
        vX = parseInt(opcode[1], 16)
        nn = parseInt(opcode.slice(2),16)
        this.Registers[vX].value += nn
        this.Registers[vX].checkCarry()
        break;
      
      case '8':
        //8xy0 8xy1 8xy2 8xy3 8xy4 8xy5 8xy6 8xy7 8xyE
        
        switch(pos4){

          case '0':
            //8xy0 - Set Vx = Vy, stores the value of register Vy in register Vx
            vX = parseInt(opcode[1], 16)
            vY = parseInt(opcode[2],16)

            this.Registers[vX].value = this.Registers[vY].value
            break;

          case '1':
            //8xy1 - Set Vx = Vx OR Vy, Performs a bitwise OR on the values of Vx and Vy, then stores the result in Vx
            vX = parseInt(opcode[1], 16)
            vY = parseInt(opcode[2],16)

            this.Registers[vX].value = this.Registers[vX].value | this.Registers[vY].value
            break;
          
          case '2':
            //8xy2 - Set Vx = Vx AND Vy, Performs a bitwise AND on the values of Vx and Vy, then stores the result in Vx
            vX = parseInt(opcode[1], 16)
            vY = parseInt(opcode[2],16)

            this.Registers[vX].value = this.Registers[vX].value & this.Registers[vY].value
            break;
          
          case '3':
            //8xy3 - Set Vx = Vx XOR Vy, Performs a bitwise exclusive OR on the values of Vx and Vy, then stores the result in Vx
            vX = parseInt(opcode[1],16)
            vY = parseInt(opcode[1], 16)

            this.Registers[vX].value = this.Registers[vX].value ^ this.Registers[vY].value
            break;
          
          case '4':
            //8xy4 - Set Vx = Vx + Vy, set VF = carry, The values of Vx and Vy are added together If the result is greater than 8 bits (i.e., > 255,) VF is set to 1, otherwise 0 Only the lowest 8 bits of the result are kept, and stored in Vx
            vX = parseInt(opcode[1],16)
            vY = parseInt(opcode[1], 16)

            this.Registers[vX].value += this.Registers[vY].value
            this.Registers[0xf].value = this.Registers[vX].checkCarry()
            break;
          
          case '5':
            //8xy5 - Set Vx = Vx - Vy, set VF = NOT borrow, If Vx > Vy, then VF is set to 1, otherwise 0 Then Vy is subtracted from Vx, and the results stored in Vx
            vX = parseInt(opcode[1],16)
            vY = parseInt(opcode[1], 16)

            this.Registers[vX].value -= this.Registers[vY].value
            this.Registers[0xf].value = this.Registers[vX].checkBorrow()
            break;

          case '6':
            //8xy6 - Set Vx = Vx SHR 1, If the least-significant bit of Vx is 1, then VF is set to 1, otherwise 0. Then Vx is divided by 2.
            vX = parseInt(opcode[1], 16)
            minBit = parseInt( parseInt( this.Registers[vX].value.at, 2).at(-1),10)

            this.Registers[vX].value = this.Registers[vX].value >> 1
            this.Registers[0xf].value = minBit 
            break; 
          
          case '7':
            //8xy7 - Set Vx = Vy - Vx, set VF = NOT borrow, If Vy > Vx, then VF is set to 1, otherwise 0. Then Vx is subtracted from Vy, and the results stored in Vx.
            vX = parseInt(opcode[1], 16)
            vY = parseInt(opcode[2], 16)
            
            this.Registers[vX].value = this.Registers[vY].value - this.Registers[vX].value
            this.Registers[vX].checkBorrow()
            break;
          
          case 'e':
            //8xyE - Set Vx = Vx SHL 1, If the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0. Then Vx is multiplied by 2.
            vX = parseInt(opcode[1], 16)
            maxBit = parseInt( parseInt( this.Registers[vX].value.at, 2).at(2),10)

            this.Registers[vX].value = this.Registers[vX].value << 1
            this.Registers[0xf].value = maxBit
            break;
        }
        break;

      case '9':
        //9xy0 - Skip next instruction if Vx != Vy, The values of Vx and Vy are compared, and if they are not equal, the program counter is increased by 2.
        vX = parseInt(opcode[1], 16)
        vY = parseInt(opcode[2], 16)

        if (this.Registers[vX].value != this.Registers[vY].value){
          this.pc += 2
        }
        break;
      
      case 'a':
        //Annn - Set I = nnn, The value of register I is set to nnn
        nnn = parseInt(opcode.slice(1),16)

        this.KeyInputs.value = nnn
        break;

      case 'b':
        //Bnnn - Jump to location nnn + V0, The program counter is set to nnn plus the value of V0
        nnn = parseInt(opcode.slice(1),16)

        this.pc = this.Registers[0].value + nnn -2
        break;
      
      case 'c':
        //Cxnn - Set Vx = random byte AND nn, The interpreter generates a random number from 0 to 255, which is then ANDed with the value nn. The results are stored in Vx. See instruction 8xy2 for more information on AND 
        vX = parseInt(opcode[1], 16)
        nnn = parseInt(opcode.slice(2), 16)

        rand = Math.floor(Math.random() * 256)

        this.Registers[vX].value = nnn & rand
        break;
      
      case 'd':
        //Dxyn - Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.
        vX = parseInt(opcode[1], 16)
        vY = parseInt(opcode[2], 16)
        n = parseInt(opcode[3], 16)

        I = this.KeyInputs.value
        sprite = this.Memory.slice(I, I+n)

        for(i = 0; i < sprite.length; i++){
          if( typeof(sprite[i]) == String){
            sprite[i] = parseInt(sprite[i], 16)
          }
        }

        if( this.draw(this.Registers[vX].value, this.Registers[vY].value, sprite)){
          this.Registers[0xf].value = 1
        }
        else{
          this.Registers[0xf].value = 0
        }
        break;
      
      case 'e':
        //Ex9E ExA1

        switch(pos4){

          case 'e':
            //Ex9E - Skip next instruction if key with the value of Vx is pressed
            vX = parseInt(opcode[1], 16)
            key = this.Registers[vX].value
            if (this.keys[key]){
              this.pc += 2
            }
            break;
          
          case '1':
            //ExA1 - Skip next instruction if key with the value of Vx is not pressed
            vX = parseInt(opcode[1], 16)
            key = this.Registers[vX].value
            if(!this.keys[key]){
              this.pc += 2
            }
            break;
        }
        break;
      
      case 'f':
        //Fx07 Fx0A Fx18 Fx1E Fx29 Fx33 Fx15 Fx55 Fx65

        switch(pos4){

          case '7':
            //Fx07 - Set Vx = delay timer value
            vX = parseInt(opcode[1], 16)
            this.Registers[vX].value = this.delayTimer.readTimer()
            break;
          
          case 'a':
            //Fx0A - Wait for a key press, store the value of the key in Vx.
            vX = parseInt(opcode[1],16)
            key = null

            while(True){
              this.keyHandler()
              isKeyPress = false

              for(i = 0; i < this.keys.length; i++){
                if (this.keys[i]){
                  key = I
                  isKeyPress = true
                }
              }
              
              if(isKeyPress){
                break;
              }
            }

            this.Registers[vX].value = key
            break;
          
          case '8':
            //Fx18 - Set sound timer = Vx
            vX = parseInt(opcode[1],16)
            val = this.Registers[vX].value
            this.soundTimer.setTimer(val)
            break;

          case 'e':
            //Fx1e - Set I = I + Vx
            vX = parseInt(opcode[1],16)
            this.KeyInputs.valuye += this.Registers[vX].value
            break;
          
          case '9':
            //Fx29 - Set I = location of sprite for digit Vx
            vX = parseInt(opcode[1],16)
            value = this.Registers[vX].value

            this.KeyInputs.value = value * 5
            break;
          
          case '3':
            //Fx33 - Store BCD representation of Vx in memory locations I, I+1, and I+2
            vX = parseInt(opcode[1],16)
            val = String(this.Registers[vX].value)

            fillNum = 3 - val.length
            val = '0'.repeat(fillNum + val)

            for(i = 0; i < val.length; i++){
              this.Memory[this.KeyInputs.value + i] = parseInt(val[i])
            }
            break;
          
          case '5':
            //Fx15 Fx55 Fx65
            
            switch(pos3){

              case '1':
                //Fx15 - Set delay timer = Vx
                vX = parseInt(opcode[1],16)
                val = this.Registers[vX].value

                this.delayTimer.setTimer(val)
                break;
              
              case '5':
                //Fx55 - Store registers V0 through Vx in memory starting at location I
                vX = parseInt(opcode[1],16)

                for(i = 0; i < vX + 1; i++){
                  this.Memory[this.KeyInputs.value + i] = this.Registers[i].value
                }
                break;
              
              case '6':
                //Fx65 - Read registers V0 through Vx from memory starting at location I
                vX = parseInt(opcode[1],16)
                
                for(i = 0; i < vX + 1; i++){
                  this.Registers[i].value = this.Memory[this.KeyInputs.value + i]
                }
                break;
            }
            break;
        }

        default:
          console.log("Invald opCode") 
    }

    this.pc += 2
  }

  execution(){
    index = this.pc
    high = this.hexHandler(this.Memory[index])
    low = this.hexHandler(this.Memory[index + 1])

    opcode = high + low

    this.opCodes(opcode)
  }
  
  // draw(){}

  clear(){
    for(i = 0; i < this.grid.length; i++){
      for(j = 0; j < this.grid[0].length; j++){
        this.grid[i][j] = 0
      }
    }
  }

  // readProg(filename) {}

  //convertProg (filename) {}

  hexHandler(Num){
    newHex = parseInt(Num, 16).slice(2)

    if (newHex.length == 1){
      newHex = '0' + newHex
    }

    return newHex
  }

  // keyHandler() {}

  //mainloop () {}

}