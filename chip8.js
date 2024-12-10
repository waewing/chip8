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
    /*
    self.delayTimer = DelayTimer()
    self.soundTimer = SoundTimer()

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
    
      case '4':
        //4xkk - skip the next instruction if Vx != kk, checks if Vx != kk if so increment PC by 2
        vX = parseInt(opcode[1], 16)
        nn = parseInt(opcode.slice(2), 16)

        if(this.Registers[vX].value != nn){
          this.pc += 2
        }
    
      case '5':
        //5xy0 - skip the next instruction if Vx = Vy, checks if Vx = Vy if so increment PC by 2
        vX = parseInt(opcode[1], 16)
        vY = parseInt(opcode[2], 16)

        if(this.Registers[vX].value == this.Registers[vY].value){
          this.pc += 2
        }

      
    }
  }
}

// const test = new Array(32).fill(new Array(64).fill(0))

// console.log(test)

