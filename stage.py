#Stage


import items

import tkinter
import os
import random



class Stage:

    #----------SETUP-------------------#

    def __init__(self, parent, screen):
    
        self.PARENT = parent
        self.SCR = screen 
        
        self.WINDOW_WIDTH = self.PARENT.WINDOW_WIDTH
        self.WINDOW_HEIGHT = self.PARENT.WINDOW_HEIGHT
        self.BLOCKSIZE = self.PARENT.BLOCKSIZE 
        
        self.DEBRIS_DRIFT = 0.2    #default drift speed 
        self.DEBRIS_DENSITY = 6
       
        
        self.load_images()
        
        #items are part of stage. Attaching this here.
        self.item_factory = items.Item_factory(self.PARENT, self.SCR)
        
        
    def load_images(self):
        """Stuff"""
        def get_img(filename):
            """Uses tkinter.photoImage to create & return an image"""
            return tkinter.PhotoImage(file=os.path.join(PATH, filename))
        
        self.stage_images = {}
        self.mg_images = {} 
        self.farm_images = {}
        
        # load background and stage element images
        PATH = os.path.join('images', 'stage', 'space1')
        for filename in ['bg1.png', 'fg1.png', 'fg2.png', 
                         'fg3.png', 'fg4.png', 'fg5.png']:
            temp = get_img(filename)
            resized = temp.subsample(2,2)
            self.stage_images[filename] = temp
            self.mg_images[filename] = resized
            
        # load farm images
        PATH = os.path.join('images', 'stage', 'farm')
        self.farm_images['land'] = get_img('land2.png')
        self.farm_images['barn'] = get_img('barn.png')
        self.farm_images['field'] = get_img('field2.png')
        self.farm_images['fence'] = get_img('fence.png')
        self.farm_images['cow'] = get_img('june.png')

    #------------PRIMITIVES----------------#              
    
    def create_fg(self, block_offset):
        """Updating so that this only worries about spawning FG for given block. 
        
        This will also check for home to spawn spaceship, I suppose. And we'll leave killboxes here too.
        
        """
    
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
            
            try_x = random.randint(block_offset, block_offset+self.BLOCKSIZE)
            try_y = random.randint(150, self.WINDOW_HEIGHT-80)
            
            self.SCR.create_image(try_x,
                              try_y,
                              image=self.stage_images[dtype_map[debris_type]],
                              tags=('ground', drift_factor),
                              anchor='nw')
            
         
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
            

    def create_bg(self, block_offset):
        """Just making this a function to abstract, and to make consistent"""
        self.SCR.create_image(block_offset, 0, tags=('bg',), anchor='nw',
                          image=self.stage_images['bg1.png'],)
                          

   
   
   
    def delete_it(self, block_offset):
        #this doesn't delete killbox, since those are spawned at winheight + 205
        for item in self.SCR.find_overlapping(block_offset,
                                              -200,         #upper Y bound
                                              block_offset + self.BLOCKSIZE,
                                              self.WINDOW_HEIGHT + 200 #lower Y bound
                                              ):
            if self.SCR.gettags(item)[0] == 'item':
                self.SCR.delete(item)
     
    
    def delete_fg(self, block_offset):
        for item in self.SCR.find_overlapping(block_offset,
                                              -200,         #upper Y bound
                                              block_offset + self.BLOCKSIZE,
                                              self.WINDOW_HEIGHT + 200 #lower Y bound
                                              ):
            tag = self.SCR.gettags(item)[0]
            if tag == 'ground' or tag == 'farm' or tag == 'june':
                self.SCR.delete(item)
            
     
    def delete_mg(self, block_offset):
        for item in self.SCR.find_overlapping(block_offset,
                                              -200,         #upper Y bound
                                              block_offset + self.BLOCKSIZE,
                                              self.WINDOW_HEIGHT + 200 #lower Y bound
                                              ):
            if self.SCR.gettags(item)[0] == 'mg':
                self.SCR.delete(item)
               
               
    def delete_bg(self, block_offset):
        #note that this one's overlapping range may need to adjust. Since BG slides now,
        #we might accidentally delete neighboring bg on accidnet if overlap here.
        for item in self.SCR.find_overlapping(block_offset,
                                              -200,         #upper Y bound
                                              block_offset + self.BLOCKSIZE,
                                              self.WINDOW_HEIGHT + 210 #lower Y bound
                                              ):
            if self.SCR.gettags(item)[0] == 'bg':
                self.SCR.delete(item)
                

     
     
     
    def spawn_farm(self):
        """Farm tag on noninteractive background image stuff. home tag on barn, that's our
        goal. June tag on cow IN PASTURE, second goal.
        
        """
    
        #delete everything in radius around spawn.
        for item in self.SCR.find_overlapping(140, 40, 700, 700):
            tag = self.SCR.gettags(item)[0]
            if tag == 'ground' or tag == 'item' or tag == 'farm':
                self.SCR.delete(item)  
                          
        #first spawn the ground
        self.SCR.create_image(200, 400, image=self.farm_images['land'],
                              tags=('ground', 12),
                              anchor='nw')
          
          
        #respawn control
        self.SCR.delete('control')
        self.PARENT.control.print_scr()
          
          
        #then barn
        self.SCR.create_image(220, 197, image=self.farm_images['barn'],
                              tags=('item', 'home', 12),
                              anchor='nw')
                              
        #cow
        if False: #self.PARENT.june_at_home:
            self.SCR.create_image(550, 344, image=self.farm_images['cow'],
                                  tags=('item', 'june', 12),
                                  anchor='nw')
        
        #fence will go here
        self.SCR.create_image(240, 360, image=self.farm_images['fence'],
                              tags=('farm', 12),
                              anchor='nw')
        
        #now field over everything
        self.SCR.create_image(140, 40, image=self.farm_images['field'],
                              tags=('farm', 12),
                              anchor='nw')
                              
    
    def spawn_pasture(self, cur_block):
    
        reference = cur_block * self.PARENT.BLOCKSIZE 
    
        #delete everything in radius
        for item in self.SCR.find_overlapping(reference + 1140, 40, 
                                              reference + 1700, 700):
            tag = self.SCR.gettags(item)[0]
            if tag == 'ground' or tag == 'item':
                self.SCR.delete(item)  
                          
        #first spawn the ground
        self.SCR.create_image(reference + 1200, 400, image=self.farm_images['land'],
                              tags=('ground', 12),
                              anchor='nw')
                              
        #respawn control
        self.SCR.delete('control')
        self.PARENT.control.print_scr()
        
        #cow
        if not self.PARENT.hold_june:
            self.SCR.create_image(reference+1400, 344, image=self.farm_images['cow'],
                              tags=('item','june', 12),
                              anchor='nw')
        
        
        #fence will go here. 
        self.SCR.create_image(reference+1240, 360, image=self.farm_images['fence'],
                              tags=('farm', 12),
                              anchor='nw')
        

                              
                              
#------------META DADDY FUNCTIONS----------------#
   
    def spawn_chitza(self):
        """Meta function, creates stepped pyramid structure of blocks/layers at block 0.
        
        """
        #First we create 7 backgrounds.
        for i in range(7):
            coord = (i - 3) * self.BLOCKSIZE
            self.create_bg(coord)
            
        #next we create 5 mg. These are created 2nd, so they layer over the top
        for i in range(5):
            coord = (i - 2) * self.BLOCKSIZE
            self.create_mg(coord)
            
        #finally we create the 3 foregrounds
        for i in range(3):
            coord = (i - 1) * self.BLOCKSIZE
            self.create_fg(coord)
            
        #and the farm
        self.spawn_farm()
        
        
           
    def clear_all(self, cur_block):
        #test if positive or negative. Then delete everything up to current block.
        if cur_block >= 0:
            for i in range(-4, cur_block + 4):
                self.delete_bg(i * self.BLOCKSIZE)
                self.delete_mg(i * self.BLOCKSIZE)
                self.delete_fg(i * self.BLOCKSIZE)  
                self.delete_it(i * self.BLOCKSIZE)
        else:
            for i in range(-4, abs(cur_block) + 4):
                self.delete_bg(i * self.BLOCKSIZE * -1)
                self.delete_mg(i * self.BLOCKSIZE * -1)
                self.delete_fg(i * self.BLOCKSIZE * -1)
                self.delete_it(i * self.BLOCKSIZE * -1)
            
     
        
    def stairstep_w_zones(self, cur_block):
        """zone='none', 'mines', 'landmines', 'seekers', 'fastdrift'
        
        use if statements to do specific item handling for zone.
        
        For fastdrift, remember that this has nothing to do with FG imgs. 
        DRIFT_SPEED is ONLY used in calc_x_drift/calc_y_drift. So maybe we just 
        temporarily update that variable for the specific block(s)
        
        Remember that order of creation is important, to handle overlaps.
        
        ALSO note that we are re-creating the control image at the end of create_fg(), so that
        he doesn't fall behind stage images. Could also do that here, but eh
        """
        
        
        #create actual stage bg, mg and fg.
        self.create_bg((cur_block + 4) * self.BLOCKSIZE)
        self.create_mg((cur_block + 3) * self.BLOCKSIZE)
        self.create_fg((cur_block + 2) * self.BLOCKSIZE)
        
        #items 
        self.item_chooser(cur_block)
        
        #delete stuff from behind.
        self.delete_bg((cur_block - 3) * self.BLOCKSIZE)
        self.delete_mg((cur_block - 2) * self.BLOCKSIZE)
        self.delete_fg((cur_block - 1) * self.BLOCKSIZE)
        self.delete_it((cur_block - 1) * self.BLOCKSIZE)
        
        
    def spawn_back_stairstep(self, cur_block):
        """back is the same, just opposite. V satisfying lol."""
        self.create_bg((cur_block - 4) * self.BLOCKSIZE)
        self.create_mg((cur_block - 3) * self.BLOCKSIZE)
        self.create_fg((cur_block - 2) * self.BLOCKSIZE)
        
        self.item_chooser(cur_block)
        
        #and delete the same way
        self.delete_bg((cur_block + 3) * self.BLOCKSIZE)
        self.delete_mg((cur_block + 2) * self.BLOCKSIZE)
        self.delete_fg((cur_block + 1) * self.BLOCKSIZE)
        self.delete_it((cur_block + 1) * self.BLOCKSIZE)
        
    
    def item_chooser(self, cur_block):
        """Takes block as inputs. Decides what items to spawn and the 
    
        density, eg to set increasing difficulty over time.
    
        """
        #item functions want pixels. This is pixel of next block border.
        block_offset = (cur_block+2)*self.BLOCKSIZE
        
        
        #check if demo version
        if self.PARENT.RESCUE_SCALE_FACTOR == 1:
            self.item_factory.spawn_landmines(block_offset, 4)
            self.item_factory.spawn_mines(block_offset, 4)
            self.item_factory.spawn_seeker('right')
            
            
        #landmines
        if cur_block > 4:
            lm_density = cur_block // 4
            self.item_factory.spawn_landmines(block_offset, lm_density)
            
        #regular mines 
        if cur_block > 8:
            m_density = cur_block // 8
            self.item_factory.spawn_mines(block_offset, m_density)
    

    
#--------------DRIFT SCREEN UPDATING STUFF--------------#

    def update(self):
    
        #access current x position of control
        pos = self.PARENT.control.position[0]
        
        #drift debris, update items, handle collisions.
        self.drift(pos)
        
        self.item_factory.update_items(pos)
        self.item_factory.collision_logic()
        
        self.check_block(pos)
        
    
    
    def check_block(self, block_offset):
        """Check whether hit threshold for next block. Then run conditional 
        
        logic to choose what to spawn. If its a bookend block, spawn either pasture 
        or farm. if it's past bookend, spawn stairstep like normal, just delete the FG.
        
        """
        cur_block = self.PARENT.block_number
        
        if block_offset > (cur_block + 1) * self.BLOCKSIZE:
            
            self.stairstep_w_zones(cur_block) 
            
            #respawn control sigh.
            self.SCR.delete('control')
            self.PARENT.control.print_scr()
            
            #if this is pasture block, spawn pasture.
            if cur_block == self.PARENT.rescue_iter * self.PARENT.RESCUE_SCALE_FACTOR:
                self.spawn_pasture(cur_block+2)
                
            elif cur_block > self.PARENT.rescue_iter * self.PARENT.RESCUE_SCALE_FACTOR:
                self.delete_fg((cur_block+2)*self.BLOCKSIZE)
            
            #increment block
            self.PARENT.block_number += 1
            
            
        elif block_offset < (cur_block) * self.BLOCKSIZE:
        
            self.spawn_back_stairstep(cur_block)
            
            #respawn control sigh.
            self.SCR.delete('control')
            self.PARENT.control.print_scr()
            
            #if this is farm block, spawn farm.
            if cur_block == 2:
                self.spawn_farm()
                
            elif cur_block < 2:
                self.spawn_farm()
                self.delete_fg((cur_block-2) * self.BLOCKSIZE)
                
        
            #decrement block
            self.PARENT.block_number -= 1

 
 
    def drift(self, block_offset):
        """
        Looks like this is most expensive function within frame_loop(). Maybe worth
        optimizing.
        
        Right now, this accesses every overlapping img on screen, runs multiple
        tests, runs a few calculations, and updates. If we could streamline the
        data access and calculation for those inner loops, might be helpful. 
        
        idea:
        -lookup cache for the drift calculation, instead of making 2 function calls
        each time.
        -can we access everything from SCR at once, and then put everything at once?
        -is there a way to avoid plural tests?
        -can we shrink the amount of stuff we're trying to update here? 
        
        
        
        """
    
    
    
        if self.DEBRIS_DRIFT == 0:
            return
            
             
        #We're going to calculate how much the screen has shifted, to help mg and bg.
        #pull current info about control mntm and direction. Also using the mapping.
        x_mapping = {'left':-1, 'right':1, 'still':0}
        x_state = self.PARENT.control.move_state['x_state']
        x_mntm = self.PARENT.control.move_state['x_mntm']    
            
        #this is, in pixels, the amount that control (and therefore the screen, has moved)
        x_shift = x_mapping[x_state] * x_mntm 
        
        
        
        #access and identify each image within this block
        for debris in self.SCR.find_overlapping(block_offset-self.WINDOW_WIDTH, -200, 
                                                block_offset+self.WINDOW_WIDTH, 
                                                self.WINDOW_HEIGHT+200):
            
            tag_tuple = self.SCR.gettags(debris)
        
            if tag_tuple[0] == 'ground':
                #pull out drift factor (0-25 digit)
                drift_factor = int(self.SCR.gettags(debris)[1])
            
                #calculate movement based on drift constant, and drift_factor
                x_delta = self.calc_x_drift(drift_factor)
                y_delta = self.calc_y_drift(drift_factor)
                
                #pull current coordinates
                current = self.SCR.coords(debris)
                
                #test where this specific debris is vertically
                if current[1] < -180:
                    #debris at very top of screen. Lets move to bottom.
                    y_delta = self.WINDOW_HEIGHT + 330
                elif current[1] > self.WINDOW_HEIGHT + 180:
                    #debris at very bottom of screen, lets move to top 
                    y_delta = -1 * (self.WINDOW_HEIGHT + 330)
                
                #now update coords for this debris.
                self.SCR.coords(debris, current[0]+x_delta, current[1]+y_delta)
    
    
            elif tag_tuple[0] == 'mg':
                #pull out drift factor (0-25 digit)
                drift_factor = int(self.SCR.gettags(debris)[1])
            
                #calculate movement based on drift constant, and drift_factor
                x_delta = self.calc_x_drift(drift_factor)
                y_delta = self.calc_y_drift(drift_factor)
                
                #for mg, we factor in (slightly) control movement.
                x_delta += x_shift * 0.3
                
                #pull current coordinates
                current = self.SCR.coords(debris)
                
                #test where this specific debris is vertically
                if current[1] < -180:
                    #debris at very top of screen. Lets move to bottom.
                    y_delta = self.WINDOW_HEIGHT + 330
                elif current[1] > self.WINDOW_HEIGHT + 180:
                    #debris at very bottom of screen, lets move to top 
                    y_delta = -1 * (self.WINDOW_HEIGHT + 330)
                
                #now update coords for this debris.
                self.SCR.coords(debris, current[0]+x_delta, current[1]+y_delta)
                
                 
            elif tag_tuple[0] == 'bg':
                
                #pull out x coord for bg currently
                bg_x = self.SCR.coords(debris)[0]  

                #add in x shift and slide bg
                self.SCR.coords(debris, bg_x + x_shift*0.6, 0)
                
                
    def calc_x_drift(self, drift_factor):
        return self.DEBRIS_DRIFT * ((drift_factor % 5) - 2) 
    
    
    def calc_y_drift(self, drift_factor):
        return self.DEBRIS_DRIFT * ((drift_factor // 5) - 2) 