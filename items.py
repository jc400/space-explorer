#items module

"""
current image tag structure:
-stage debris has first label of 'ground', 'mg', 'bg'. Next label is drift factor, used by drift()
    -also note that control uses 'ground' tag to determine collisions, in move()
    
-currently killboxes are 'killbox' tag. Handled in control.collision_logic() 

New structure:
-all interactive images should have 'item' as first tag, so item_move() knows what to look for.
-next tag should be the specific item name. 
-then drift, if relevant. USE 12 FOR STATIONARY
-then the frame, used for animations. 

"""

import tkinter
import os
import random
import math



class Item_factory:
    
#---------------INIT AND SETUP-----------------#

    def __init__(self, parent, screen):
    
        self.PARENT = parent
        self.SCR = screen
        
        self.MINESIZE = 100
        
        self.load_images()
        

    def load_images(self):
        
        def get_img(filename):
            """Uses tkinter.photoImage to create & return an image"""
            return tkinter.PhotoImage(file=os.path.join(PATH, filename))
            
        # define dict to hold item images
        self.images = {'landmine':{}}
        
        # load regular mine image
        PATH = os.path.join('images', 'item')
        self.images['mine'] = get_img('mine.png')
        
        # landmine images
        PATH = os.path.join('images', 'item', 'landmine')
        self.images['landmine']['dormant'] = get_img('dormant.png')
        self.images['landmine']['blank'] = get_img('blank.png')
        self.images['landmine']['three'] = get_img('three.png')
        self.images['landmine']['two'] = get_img('two.png')
        self.images['landmine']['one'] = get_img('one.png')

    
#---------------INSIDE FRAMELOOP--------------# 
    
    def update_items(self, block_offset):
    
        #access every img within the offset aread
        for item in self.SCR.find_overlapping(block_offset-self.PARENT.WINDOW_WIDTH, -200, 
                                              block_offset+self.PARENT.WINDOW_WIDTH, 
                                              self.PARENT.WINDOW_HEIGHT+200):
            
            tag_tuple = self.SCR.gettags(item)
            
            #skip processing for non-items
            if tag_tuple[0] != 'item':
                continue
             
            #if drift on item, calculate and apply it.
            if tag_tuple[2] != '12':        
                #pull out drift factor (0-25 digit)
                drift_factor = int(self.SCR.gettags(item)[2])
            
                #calculate drift via stage item on parent.
                x_delta = self.PARENT.stage.calc_x_drift(drift_factor)
                y_delta = self.PARENT.stage.calc_y_drift(drift_factor)
                
                #pull current coordinates for this item
                current = self.SCR.coords(item)
                
                #if debris near top or bottom, wrap it around.
                if current[1] < -180:
                    y_delta = self.PARENT.WINDOW_HEIGHT + 330
                elif current[1] > self.PARENT.WINDOW_HEIGHT + 180:
                    y_delta = -1 * (self.PARENT.WINDOW_HEIGHT + 330)
                
                #now update coords for this debris.
                self.SCR.coords(item, current[0]+x_delta, current[1]+y_delta)
    
            #now lets specifically handle certain cases
            if tag_tuple[1] == 'explosion':
                frame = int(tag_tuple[3])
                if frame > 0:
                    frame -= 1
                    self.SCR.itemconfig(item, tags=('item', 'explosion', 12, frame))
                else:
                    self.SCR.delete(item)
                  
                  
            elif tag_tuple[1] == 'landmine':
                frame = int(tag_tuple[3])
                if frame == 100:
                    pass    #dormant still
                elif frame // 8 == 5:
                    self.SCR.itemconfig(item, image=self.images['landmine']['three'],
                                        tags=('item', 'landmine', 12, frame-1))
                elif frame // 8 == 4:
                    self.SCR.itemconfig(item, image=self.images['landmine']['blank'],
                                        tags=('item', 'landmine', 12, frame-1))
                elif frame // 8 == 3:
                    self.SCR.itemconfig(item, image=self.images['landmine']['two'],
                                        tags=('item', 'landmine', 12, frame-1))
                elif frame // 8 == 2:
                    self.SCR.itemconfig(item, image=self.images['landmine']['blank'],
                                        tags=('item', 'landmine', 12, frame-1))
                elif frame // 8 == 1:
                    self.SCR.itemconfig(item, image=self.images['landmine']['one'],
                                        tags=('item', 'landmine', 12, frame-1))
                elif frame // 8 == 0:
                    if frame > 0:
                        self.SCR.itemconfig(item, image=self.images['landmine']['blank'],
                                            tags=('item', 'landmine', 12, frame-1))
                    else:
                        self.explode(self.SCR.coords(item), self.MINESIZE * 2)
                        self.SCR.delete(item)
                      

    def collision_logic(self):
        """Performs logic for anything control collides with.
        
        Find_overlapping() returns a tuple of item IDs. Use gettags(ID) to return tuple
        of that items tags (which we can actually use).
        Can you call function from within dict? Eg to save massive if/else loop?

        """
        
        x1 = self.PARENT.control.position[0]
        y1 = self.PARENT.control.position[1]
        x2 = x1+self.PARENT.control.char_size_x
        y2 = y1+self.PARENT.control.char_size_y 
        
        
        #just check y height instead of relying on killbox under stage.
        if y1 > self.PARENT.WINDOW_HEIGHT + 200:
            self.death_updates()
            return
        
        
        for item in self.SCR.find_overlapping(x1, y1, x2, y2):
        
            tag_tuple = self.SCR.gettags(item)
            
            if tag_tuple[0] != 'item':         #case of non-interactive image
                continue
        
            elif tag_tuple[1] == 'killbox':    #killbox, usually falls.
                self.death_updates()
                return
                
            elif tag_tuple[1] == 'explosion':    
                self.PARENT.control.position = (self.PARENT.control.position[0],
                                                self.PARENT.control.position[1] + 2000)
                                                
                self.death_updates()
                return
                
            elif tag_tuple[1] == 'mine': 
                coordinates = self.SCR.coords(item)
                self.SCR.delete(item)
                self.explode(coordinates, self.MINESIZE)
                
            elif tag_tuple[1] == 'landmine': 
                if tag_tuple[3] == '100':
                    self.SCR.itemconfig(item, tags=('item', 'landmine', 12, 47))
                else:
                    pass
                                
            elif tag_tuple[1] == 'june':
                
                #this ends one leg of rescue.
                self.SCR.delete(item)
                
                #change image so we carry june
                newpath = os.path.join('spaceman', 'carryjune')
                self.PARENT.control.load_images(pth=newpath)
                self.PARENT.hold_june = True
                            
            elif tag_tuple[1] == 'home':
                
                if self.PARENT.hold_june:
                    self.PARENT.control.load_images()
                    
                    #update state
                    self.PARENT.hold_june = False
                    self.PARENT.rescue_iter += 1
                    
                              
                    self.PARENT.cutscene = 'steal'
       
            else:
                print('item name not recognized by collision_logic: ', tag_tuple[1])

               
    def death_updates(self):
        self.PARENT.game_over = True
        self.PARENT.stop_movement = True
        
        

#--------------ITEM SPECIFIC STUFF--------------#

    def spawn_mines(self, block_offset, density):
    
        for i in range(density):
            drift_factor = str(random.randint(0, 25))
            
            try_x = block_offset+800
            try_y = 400
            while len(self.SCR.find_overlapping(try_x, try_y, try_x+400, try_y+100)) > 1:
                try_x = random.randint(block_offset, block_offset+self.PARENT.BLOCKSIZE)
                try_y = random.randint(150, self.PARENT.WINDOW_HEIGHT-80)
            
            self.SCR.create_image(try_x,
                              try_y,
                              image=self.images['mine'],
                              tags=('item', 'mine', drift_factor),
                              anchor='nw')
            
    
    def spawn_landmines(self, block_offset, density):
    
        count = density
        
        #access all fg. Up to density count, spawn a landmine on each.
        for img in self.SCR.find_overlapping(block_offset, 0, block_offset+self.PARENT.BLOCKSIZE, 
                                                self.PARENT.WINDOW_HEIGHT):
            if count == 0:
                break
            
            if self.SCR.gettags(img)[0] == 'ground':
                x = self.SCR.coords(img)[0] + random.randint(0, 80)
                y = self.SCR.coords(img)[1] - 50
                drift_factor = self.SCR.gettags(img)[1]
                self.SCR.create_image(x, y, image=self.images['landmine']['dormant'],
                                      tags=('item', 'landmine', drift_factor, 100),
                                      anchor='nw')
                                      
                count -= 1
                

    def explode(self, coord_tuple, size):
    
        x1 = coord_tuple[0] - size
        y1 = coord_tuple[1] - size
        x2 = coord_tuple[0] + size
        y2 = coord_tuple[1] + size
        self.SCR.create_oval((x1, y1, x2, y2), 
                             fill='light green',
                             outline='green',
                             width=50, 
                             #stipple='gray50',      #stipple only works for rectangle                      
                             tags=('item', 'explosion', 12, 3))
                             
       
                             
                             
                             