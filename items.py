#items module

"""
Note RE seeker: current seeker implementation requires PIL library, because it is rotating the 
seeker image (and we can't do that with just tkinter). I want to remove the PIL dependency for ease 
of setup, so I will be removing the seeker from the regular game. But I'm leaving the seeker code
here, and maybe we can check for PIL and use it optionally. Will decide later.

Seeker needs: 
-images loaded here --> load_seeker_images() called when init() item factory
-seeker spawned --> stage.stairstep() -> stage.item_chooser() -> stage.spawn_items()
                -> spawn_seeker()
-seeker update: -> item.move -> seeker.move()


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

#from PIL import Image, ImageTk  # Required to rotate seeker image
SEEKER_ACTIVE = False


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
        self.images = {'seeker':{}, 'landmine':{}}
        
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

    def load_seeker_images(self):
        from PIL import Image, ImageTk
        PATH = os.path.join('images', 'item')
        self.images['seeker']['raw'] = Image.open(os.path.join(PATH, 'seeker', 'mini.png'))
        self.images['seeker']['temp'] = ImageTk.PhotoImage(self.images['seeker']['raw'])
        
    
    
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
                    
                    
            elif tag_tuple[1] == 'seeker':
                self.seeker_move(item)
                
                sx = self.SCR.coords(item)[0]
                sy = self.SCR.coords(item)[1]
                
                for col in self.SCR.find_overlapping(sx, sy, sx+10, sy+10):
                    try:
                        tag = self.SCR.gettags(col)[0]
                        if tag == 'ground' or tag == 'control':
                            self.explode((sx, sy), self.MINESIZE)
                            self.SCR.delete(item)
                            break
                    except IndexError:
                        print('couldnt retrieve tag for overlapping missile item. passing')
                        print(self.SCR.gettags(col), col)
                        
            elif tag_tuple[1] == 'shooter':
                self.shooter_move(item)
                
                sx = self.SCR.coords(item)[0]
                sy = self.SCR.coords(item)[1]
                
                for col in self.SCR.find_overlapping(sx, sy, sx+10, sy+10):
                    try:
                        tag = self.SCR.gettags(col)[0]
                        if tag == 'ground' or tag == 'control':
                            self.explode((sx, sy), self.MINESIZE)
                            self.SCR.delete(item)
                            break
                    except IndexError:
                        print('couldnt retrieve tag for overlapping shooter item. passing')
                        print(self.SCR.gettags(col), col)
                

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
                    
            elif tag_tuple[1] == 'seeker': 
                pass
               
            elif tag_tuple[1] == 'june':
                
                #this ends one leg of rescue.
                self.SCR.delete(item)
                
                #change image so we carry june
                self.PARENT.control.load_images(pth='spaceman\carryjune')
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
                
    
    def spawn_seeker(self, side):
        if not SEEKER_ACTIVE:
            return
        
        seeker_y = random.randint(100, self.PARENT.WINDOW_HEIGHT-100)
        if side == 'left':
            seeker_x = self.PARENT.control.position[0] - 1000
            angle = 0
        else:
            seeker_x = self.PARENT.control.position[0] + 1000
            angle = 3.14
        
        self.SCR.create_image(seeker_x, seeker_y, 
                              image=self.images['seeker']['temp'],
                              tags=('item', 'seeker', 12, angle),  #drift 12, angle in radians.
                              anchor='nw')
    

    def seeker_move(self, seeker):
        
        #------------GET INFO AND VARS--------------#
        
        #angle of direction (RADIANS) pulled from tag
        s_angle = float(self.SCR.gettags(seeker)[3])
        
        #current x/y coords of seeker
        sx = self.SCR.coords(seeker)[0]
        sy = self.SCR.coords(seeker)[1]
        
        #currnet x/y of target (eg control)
        tx = self.PARENT.control.position[0]
        ty = self.PARENT.control.position[1]
        
        #missile constants
        SPEED = 12
        TURN_RADIUS = math.radians(3)
        
        #print('/nSTART INFO:')
        #print('s_angle: ', s_angle, 'sx: ', sx, ' sy: ', sy)
        #print('tx: ', tx, ' ty: ', ty)
        
        
        #---------------CALCULATE IDEAL ANGLE TO TARGET---------#
        """Note that atan2() assumes 0 degrees is right. So 90 is 
        straight up, -90 is straight down. We want to convert this 
        to 360 degrees of clock, where 0 degrees is straight up. 
        
        top r bot left
        90  0 -90 180/-180 -- with atan2()
        0  -90-180 90      -- adjusted by -90. negative side becomes right.
        
        270 180 90 0       -- add 180
        90  0  270  180    -- add 360 mod 360. This is what we want. 
        0  
        """
        
        #calculate direct angle towards target
        perfect_angle = math.atan2(ty-sy, tx-sx)
        
        #translate to use 360 degrees.
        perfect_angle = (perfect_angle + math.radians(360)) % math.radians(360)

        #calculate difference in angle
        diff = math.degrees(s_angle - perfect_angle)
        
        #if seeker angle is close enough to perfect, slot it in
        if abs(diff) < 10: 
            s_angle = perfect_angle
            decision = 'Close enough'
            
        #otherwise, turn s_angle on fastest route towards perfect angle
        elif abs(diff) < 180:
            if diff > 0:
                s_angle = (s_angle - TURN_RADIUS) % math.radians(360)
                decision= 'under 180, subtrct turn'
            else:
                s_angle = (s_angle + TURN_RADIUS) % math.radians(360)
                decision= 'under 180, add turn'
        #this means that we've looped around, so reverse logic applies
        else:
            if diff > 0:
                s_angle = (s_angle + TURN_RADIUS) % math.radians(360)
                decision= 'over 180, add turn'
            else:
                s_angle = (s_angle - TURN_RADIUS) % math.radians(360)
                decision= 'over 180, subtract turn'
            
        #print("\n CALCULATE ANGLE")
        #print("perfect angle: ", perfect_angle, " diff: ", diff, "decision: ", decision)
        #print("New s_angle: ", s_angle)
        
        #----------------CALCULATE ACTUAL MOTION--------------#
        
        #slope, eg how much y needs to change for every 1 change of x
        #divisor, to adjust x/y delta to a percentage.
        slope = abs(math.tan(s_angle))
        divisor = abs(slope) + 1
        radian90 = 1.5707963267948966
        
        #here we ignroe the sign value of slope. Simply use quadrant to
        #determine correct signs for x/y deltas.
        if s_angle // radian90 == 0:
            x_delta = 1 / divisor * SPEED
            y_delta = slope / divisor * SPEED
            
        elif s_angle // radian90 == 1:
            x_delta = -1 / divisor * SPEED
            y_delta = slope / divisor * SPEED
            
        elif s_angle // radian90 == 2:
            x_delta = -1 / divisor * SPEED
            y_delta = -1 * slope / divisor * SPEED
            
        elif s_angle // radian90 == 3:
            x_delta = 1 / divisor * SPEED
            y_delta = -1 * slope / divisor * SPEED
        
        else:
            print('weird value for s_angle: ', s_angle)
                   
        #print('\nCalculate actual motion')
        #print('slope: ', slope, ' x delta: ', x_delta, ' y delta: ', y_delta)
        #print('quadrant: ', s_angle // radian90)
        #print('\n\n')
        
        
        #----------------ACTUALLY UPDATE MISSILE-------------#
        #now actually update the missile coords
        self.SCR.coords(seeker, sx+x_delta, sy+y_delta)
        
        #update image dict with rotated image of seeker
        temp = self.images['seeker']['raw'].rotate(math.degrees(s_angle) * -1, expand=1)
        self.images['seeker']['temp'] = ImageTk.PhotoImage(temp)
        
        #change image on screen with new angle tag and image.
        self.SCR.itemconfig(seeker, tags=('item', 'seeker', 12, s_angle),
                            image=self.images['seeker']['temp'])
         

    
    def spawn_shooter(self, side):
        seeker_y = random.randint(100, self.PARENT.WINDOW_HEIGHT-100)
        if side == 'left':
            seeker_x = self.PARENT.control.position[0] - 1000
            angle = 0
        else:
            seeker_x = self.PARENT.control.position[0] + 1000
            angle = 3.14
        
        self.SCR.create_image(seeker_x, seeker_y, 
                              image=self.images['seeker']['temp'],
                              tags=('item', 'shooter', 12, angle),  #drift 12, angle in radians.
                              anchor='nw')
    

    def shooter_move(self, seeker):
        
        #------------GET INFO AND VARS--------------#
        
        #angle of direction (RADIANS) pulled from tag
        s_angle = float(self.SCR.gettags(seeker)[3])
        
        #current x/y coords of seeker
        sx = self.SCR.coords(seeker)[0]
        sy = self.SCR.coords(seeker)[1]
        
        #currnet x/y of target (eg control)
        tx = self.PARENT.control.position[0]
        ty = self.PARENT.control.position[1]
        
        #missile constants
        SPEED = 40
        TURN_RADIUS = math.radians(0.5)
        
        #print('/nSTART INFO:')
        #print('s_angle: ', s_angle, 'sx: ', sx, ' sy: ', sy)
        #print('tx: ', tx, ' ty: ', ty)
        
        
        #---------------CALCULATE IDEAL ANGLE TO TARGET---------#
        """Note that atan2() assumes 0 degrees is right. So 90 is 
        straight up, -90 is straight down. We want to convert this 
        to 360 degrees of clock, where 0 degrees is straight up. 
        
        top r bot left
        90  0 -90 180/-180 -- with atan2()
        0  -90-180 90      -- adjusted by -90. negative side becomes right.
        
        270 180 90 0       -- add 180
        90  0  270  180    -- add 360 mod 360. This is what we want. 
        0  
        """
        
        #calculate direct angle towards target
        perfect_angle = math.atan2(ty-sy, tx-sx)
        
        #translate to use 360 degrees.
        perfect_angle = (perfect_angle + math.radians(360)) % math.radians(360)

        #calculate difference in angle
        diff = math.degrees(s_angle - perfect_angle)
        
        #if seeker angle is close enough to perfect, slot it in
        if abs(diff) < 10: 
            s_angle = perfect_angle
            decision = 'Close enough'
            
        #otherwise, turn s_angle on fastest route towards perfect angle
        elif abs(diff) < 180:
            if diff > 0:
                s_angle = (s_angle - TURN_RADIUS) % math.radians(360)
                decision= 'under 180, subtrct turn'
            else:
                s_angle = (s_angle + TURN_RADIUS) % math.radians(360)
                decision= 'under 180, add turn'
        #this means that we've looped around, so reverse logic applies
        else:
            if diff > 0:
                s_angle = (s_angle + TURN_RADIUS) % math.radians(360)
                decision= 'over 180, add turn'
            else:
                s_angle = (s_angle - TURN_RADIUS) % math.radians(360)
                decision= 'over 180, subtract turn'
            
        #print("\n CALCULATE ANGLE")
        #print("perfect angle: ", perfect_angle, " diff: ", diff, "decision: ", decision)
        #print("New s_angle: ", s_angle)
        
        #----------------CALCULATE ACTUAL MOTION--------------#
        
        #slope, eg how much y needs to change for every 1 change of x
        #divisor, to adjust x/y delta to a percentage.
        slope = abs(math.tan(s_angle))
        divisor = abs(slope) + 1
        radian90 = 1.5707963267948966
        
        #here we ignroe the sign value of slope. Simply use quadrant to
        #determine correct signs for x/y deltas.
        if s_angle // radian90 == 0:
            x_delta = 1 / divisor * SPEED
            y_delta = slope / divisor * SPEED
            
        elif s_angle // radian90 == 1:
            x_delta = -1 / divisor * SPEED
            y_delta = slope / divisor * SPEED
            
        elif s_angle // radian90 == 2:
            x_delta = -1 / divisor * SPEED
            y_delta = -1 * slope / divisor * SPEED
            
        elif s_angle // radian90 == 3:
            x_delta = 1 / divisor * SPEED
            y_delta = -1 * slope / divisor * SPEED
        
        else:
            print('weird value for s_angle: ', s_angle)
                   
        #print('\nCalculate actual motion')
        #print('slope: ', slope, ' x delta: ', x_delta, ' y delta: ', y_delta)
        #print('quadrant: ', s_angle // radian90)
        #print('\n\n')
        
        
        #----------------ACTUALLY UPDATE MISSILE-------------#
        #now actually update the missile coords
        self.SCR.coords(seeker, sx+x_delta, sy+y_delta)
        
        #update image dict with rotated image of seeker
        temp = self.images['seeker']['raw'].rotate(math.degrees(s_angle) * -1, expand=1)
        self.images['seeker']['temp'] = ImageTk.PhotoImage(temp)
        
        #change image on screen with new angle tag and image.
        self.SCR.itemconfig(seeker, tags=('item', 'shooter', 12, s_angle),
                            image=self.images['seeker']['temp'])
         



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
                             
       
                             
                             
                             