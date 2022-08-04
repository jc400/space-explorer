#saucer

import os
import tkinter


class Saucer:

    def __init__(self, parent, screen):
        
        self.PARENT = parent
        self.SCR = screen
        
        self.ACCELERATION = 0.3
        self.TOP_SPEED = 15
               
        self.mntm = 0
        self.x_dir = 'still'
        self.position = (0,0)   #filled when we spawn
        
        self.lifespan = 0
        
        self.tkreference = None #assigned when we create tkinter image
        
        
        self.load_images()
        
        
    def load_images(self):
        
        PATH = os.path.join('images', 'stage', 'alien', 'saucer.png')
        self.img = tkinter.PhotoImage(file=PATH)
        
       
    def spawn(self):
        
        x = self.PARENT.control.position[0] - 1000
        y = 200
        
        self.lifespan = 1000
        
        self.tkreference = self.SCR.create_image(x, y, 
            image=self.img, tags=('saucer', ), anchor='nw')
       
    
    
    def move(self, control_x):
        
        x_mapping = {'left':-1, 'right':1, 'still':0}
        
            
        #check position relative to control. Accelerate towards control_x - 350
        if self.position[0] < (control_x-350):
        
            if self.x_dir == 'right':
                self.mntm += self.ACCELERATION
                
            elif self.x_dir == 'left':
                
                if self.mntm > self.ACCELERATION*4:
                    self.mntm -= self.ACCELERATION*4
                else:
                    self.mntm = 0
                    self.x_dir = 'still'
            
            else:
                self.x_dir = 'right'
                self.mntm = self.ACCELERATION
                
                
        elif self.position[0] > (control_x-350):
            
            if self.x_dir == 'left':
                self.mntm += self.ACCELERATION
                
            elif self.x_dir == 'right':
                
                if self.mntm > self.ACCELERATION*4:
                    self.mntm -= self.ACCELERATION*4
                else:
                    self.mntm = 0
                    self.x_dir = 'still'
            
            else:
                self.x_dir = 'left'
                self.mntm = self.ACCELERATION
                
                
        
        x_delta = self.mntm * x_mapping[self.x_dir]
        self.position = (self.position[0]+x_delta, self.position[1])
        
        self.SCR.coords(self.tkreference, self.position[0], self.position[1])
        
        
    def update(self, pos):
        
        if self.lifespan > 1:
        
            self.lifespan -= 1
            self.move(pos)
            
        elif self.lifespan == 1:
            
            self.SCR.delete(self.tkreference)
            self.lifespan = 0
            
        else:
            return
        
        