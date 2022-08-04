#asteroid stage


import stage

import os
from PIL import Image, ImageTk
import random

class Asteroids(stage.Stage):
    
    def __init__(self, parent, screen):
        
        super().__init__(parent, screen)
        
        self.DEBRIS_DENSITY = 5
        self.DEBRIS_DRIFT = 1
        
        
    def load_images(self):

        PATH = os.path.join('images', 'stage', 'asteroids')
      
        self.stage_images = {}
        self.mg_images = {}
        
        filenames = ['bg1.png','ship.png', 'fg1.png', 'fg2.png', 'fg3.png', 'fg4.png', 'fg5.png']
        
        for i in filenames:
            temp = Image.open(os.path.join(PATH, i))
            
            resized = temp.resize((round(temp.size[0]*.3), round(temp.size[1]*.3)))
            
            self.stage_images[i] = ImageTk.PhotoImage(temp)
            self.mg_images[i] = ImageTk.PhotoImage(resized)
           
    
    
    
    def create_fg(self, block_offset):
        """Updating so that this only worries about spawning FG for given block. 
        
        This will also check for home to spawn spaceship, I suppose. And we'll leave killboxes here too.
        
        """
    
        density = self.DEBRIS_DENSITY
        
        #create killbox.
        self.SCR.create_rectangle((block_offset, self.WINDOW_HEIGHT+100, 
                                   block_offset+self.BLOCKSIZE, 
                                   self.WINDOW_HEIGHT+200),
                                   fill='red',
                                   tags=('item', 'killbox', 12))

        
        #check if its home base
        if block_offset == 0:
            self.SCR.create_image(200, 300, image=self.stage_images['ship.png'],
                          tags=('ground', 12),
                          anchor='nw')
        
        
        #create debris
        dtype_map = {1:'fg1.png',
                     2:'fg2.png',
                     3:'fg3.png',
                     4:'fg4.png',
                     5:'fg5.png'
                     }
        for i in range(density):
            debris_type = random.randint(1, 5)
            drift_factor = str(random.randint(0, 25))
            
            try_x = block_offset+800
            try_y = 400
            while len(self.SCR.find_overlapping(try_x, try_y, try_x+400, try_y+100)) > 1:
                try_x = random.randint(block_offset, block_offset+self.BLOCKSIZE)
                try_y = random.randint(150, self.WINDOW_HEIGHT-80)
            
            self.SCR.create_image(try_x,
                              try_y,
                              image=self.stage_images[dtype_map[debris_type]],
                              tags=('ground', drift_factor),
                              anchor='nw')
            

        #respawn control sigh. DO I NEED THIS HERE??
        self.SCR.delete('control')
        self.PARENT.control.print_scr()
   
   
    def create_mg(self, block_offset):
        """This essentially functions just like create_fg() but only worries about mg"""
        
        density = self.DEBRIS_DENSITY
        
        #create debris
        dtype_map = {1:'fg1.png',
                     2:'fg2.png',
                     3:'fg3.png',
                     4:'fg4.png',
                     5:'fg5.png'}
        for i in range(density):
            debris_type = random.randint(1, 5)
            drift_factor = str(random.randint(0, 25))
            
            try_x = block_offset+800
            try_y = 400
            while len(self.SCR.find_overlapping(try_x, try_y, try_x+400, try_y+100)) > 1:
                try_x = random.randint(block_offset, block_offset+self.BLOCKSIZE)
                try_y = random.randint(150, self.WINDOW_HEIGHT-80)
            
            self.SCR.create_image(try_x,
                              try_y,
                              image=self.mg_images[dtype_map[debris_type]],
                              tags=('mg', drift_factor),
                              anchor='nw')