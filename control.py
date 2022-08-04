#CONTROL
import tkinter
import os


# MOVEMENT CONSTANTS
FALL_ACCELERATION = 1   #this is a rate of change.

JUMP_MOMENTUM = 10#8       #this is constant momentum through the jump
JUMP_FRAMES = 12#15
   
JETPACK_ACCELERATION = 1 #full accel applied when falling. Half applied when rising.
JETPACK_REGEN = 0.15
JETPACK_MAX = 24

RUN_ACCELERATION = 0.5
X_BRAKE_AIR = 1
X_BRAKE_GROUND = 2
X_FRICTION_GROUND = .4


class Control:
#----------INIT AND SETUP---------------#

    def __init__(self, parent, screen):
    
        self.PARENT = parent
        self.SCR = screen
        
        #initialize character's state
        self.move_state = {'y_state':'falling', #standing / jumping / hovering / falling
                           'y_mntm':0,
                           'y_frame':0,
                           'x_state':'right', #left, right only
                           'x_mntm':0,
                           'x_frame':0,
                           'stand_block':None,
                           'stand_block_df':0,
                           }
                        
        self.char_state = {'lives':5,
                           'fuel':15,
                           'coins':0,
                           }

        self.xdir = None
        self.ydir = None

        
        #load own images
        self.load_images()
        
        self.position = (250, 300-self.char_size_y)
        
        self.print_scr()
    
    def load_images(self, pth='spaceman'):
        """Load images. pth allows different characters to be loaded."""
        PATH = os.path.join('images', 'char', pth)
        self.images = {'left':{}, 'right':{}}
        
        def get_img(filename):
            """Uses tkinter.photoImage to create & return an image"""
            return tkinter.PhotoImage(file=os.path.join(PATH, filename))
        
        self.images['left']['standing'] = get_img('standleft.png')
        self.images['left']['stand_2'] = get_img('runleft.png')
        self.images['left']['jumping'] = get_img('standleft.png')
        self.images['left']['falling'] = get_img('fallleft.png')
        self.images['left']['jetpack'] = get_img('jetpackleft.png')
        self.images['right']['standing'] = get_img('standright.png')
        self.images['right']['stand_2'] = get_img('runright.png')
        self.images['right']['jumping'] = get_img('standright.png')
        self.images['right']['falling'] = get_img('fallright.png')
        self.images['right']['jetpack'] = get_img('jetpackright.png')
        
        # get width/height of character
        self.char_size_x = self.images['left']['standing'].width()
        self.char_size_y = self.images['left']['standing'].height()


#---------------RESETTING-----------------#

    def print_scr(self):
        x = self.move_state['x_state']
        y = self.move_state['y_state']
        self.SCR.create_image(self.position[0],
                              self.position[1],
                              image=self.images[x][y],
                              tag='control',
                              anchor='nw',
                              )


    def reset(self):
        self.position = (250, 300-self.char_size_y)
        
        self.move_state['x_state'] = 'right'
        self.move_state['x_mntm'] = 0
        self.move_state['y_mntm'] = 0
        self.char_state['fuel'] = 15
        
        self.load_images()
        
        
       

#-------------IN LOOP LOGIC--------------#

    def update(self):
        self.move()
        self.regen_fuel()
           
  
    def move(self):
    
        #pull state into function-local vars
        x_state = self.move_state['x_state']
        x_mntm = self.move_state['x_mntm']
        y_state = self.move_state['y_state']
        y_mntm = self.move_state['y_mntm']
        y_frame = self.move_state['y_frame']
        
        if self.PARENT.stop_movement == False:
            x_dir = self.xdir 
            y_dir = self.ydir
        else:
            x_dir = y_dir = 0
        
        #adjust for drift, if standing. Formula copied from drift()
        if y_state == 'standing': 
            DF = self.move_state['stand_block_df']
            self.position = (self.position[0] + self.PARENT.stage.calc_x_drift(DF),
                            self.position[1] + self.PARENT.stage.calc_y_drift(DF))
        
        #X AXIS 
        run_gearing = [RUN_ACCELERATION, 
                       RUN_ACCELERATION-.2, 
                       RUN_ACCELERATION-0.3, 
                       RUN_ACCELERATION-.4,
                       RUN_ACCELERATION-.4,
                       RUN_ACCELERATION-.4,
                       RUN_ACCELERATION-.4,
                       RUN_ACCELERATION]
        
        #process command and logic 
        if x_dir:
            if x_mntm == 0:
                x_state = x_dir 
                x_mntm += RUN_ACCELERATION
            elif x_state == x_dir:
                if y_state == 'standing':
                    x_mntm += run_gearing[int(x_mntm // 10)]
                else:
                    x_mntm += 0.7 * run_gearing[int(x_mntm // 10)]
            else:
                if y_state == 'standing':
                    x_mntm -= X_BRAKE_GROUND 
                else:
                    x_mntm -= X_BRAKE_AIR 
                if x_mntm < 1:
                    x_mntm = 0
        else:
            if y_state == 'standing': 
                x_mntm -= X_FRICTION_GROUND
                if x_mntm < 1:
                    x_mntm = 0
        
        #check for collisions (ACCESS GAME SCREEN)
        x_mapping = {'left':-1, 'right':1, 'still':0}
        x1 = self.position[0] + (x_mapping[x_state] * x_mntm)
        y1 = self.position[1]
        for item in self.SCR.find_overlapping(x1, y1, x1+self.char_size_x, y1+self.char_size_y-5):
            if self.SCR.gettags(item)[0] == 'ground':
                x_mntm = x_mntm // 5
                if x_state == 'right':
                    x_state = 'left'
                else:
                    x_state = 'right'
        
        #update new states
        self.move_state['x_state'] = x_state
        self.move_state['x_mntm'] = x_mntm
        
        
        #Y AXIS NEXT
        #process command and logic
        if y_dir == 'jump':
            if y_state == 'standing':
                y_state = 'jumping'
                y_mntm = -1 * JUMP_MOMENTUM
                y_frame = 1
            elif y_state == 'jumping':
                if y_frame < JUMP_FRAMES:
                    y_frame += 1
                else:
                    y_state = 'falling'
                    y_mntm += FALL_ACCELERATION
                    y_frame = 0
            elif y_state == 'falling':
                y_mntm += FALL_ACCELERATION
        elif y_dir == 'jetpack':
            if self.char_state['fuel'] > 0:
                y_state = 'jetpack'
                self.char_state['fuel'] -= 1
                if y_mntm > 0:
                    y_mntm -= JETPACK_ACCELERATION / 2
                else:
                    y_mntm -= JETPACK_ACCELERATION
            else:
                y_state = 'falling'
                y_mntm += FALL_ACCELERATION
        else:
            if y_state == 'standing':
                y_state = 'falling'
                y_mntm = 2
            else:
                y_state = 'falling'
                y_mntm += FALL_ACCELERATION
            
        #check for collisions (ACCESS SCR)
        x1 = self.position[0] + (x_mapping[x_state] * x_mntm)
        y1 = self.position[1] + y_mntm 
        for item in self.SCR.find_overlapping(x1, y1, x1+self.char_size_x, y1+self.char_size_y):
            if self.SCR.gettags(item)[0] == 'ground':
                if y_mntm >= -1:  #landed on a platform
                    y_state = 'standing'
                    
                    #adjust Y mntm to stand directly on item.
                    y_mntm = self.SCR.coords(item)[1] - self.position[1] - self.char_size_y - 0.9
                    
                    #save info for this item, so we can drift with it.
                    self.move_state['stand_block'] = item
                    try:
                        self.move_state['stand_block_df'] = int(self.SCR.gettags(item)[1])
                    except IndexError:
                        pass
 
                else:
                    y_state = 'falling'
                    y_mntm = 0
                    
        #update with new logiced/validated state
        self.move_state['y_state'] = y_state
        self.move_state['y_mntm'] = y_mntm
        self.move_state['y_frame']= y_frame
        
        #change position coordinates tuple
        self.position = (self.position[0] + (x_mapping[x_state] * x_mntm),
                        self.position[1] + y_mntm)
        
        
        #UPDATE ACTUAL SCREEN 
        #update control image 
        if y_state=='standing' and self.PARENT.clock % 10 > 5 and x_mntm > 0:
            if x_dir:
                self.SCR.itemconfig('control', image=self.images[x_dir]['stand_2'])
            else:
                self.SCR.itemconfig('control', image=self.images[x_state]['stand_2'])
        else:
            if x_dir:
                self.SCR.itemconfig('control', image=self.images[x_dir][y_state])
            else:
                self.SCR.itemconfig('control', image=self.images[x_state][y_state])
        
  
        #update image position
        self.SCR.coords('control', self.position[0], self.position[1])
        
        #update view THIS SHOULD MAYBE MOVE?
        """
        self.SCR.xview_moveto((self.position[0] 
                               -(self.PARENT.WINDOW_WIDTH / 2)) 
                               / self.PARENT.WINDOW_WIDTH)
        """
        
        
    def regen_fuel(self):
        #update fuel. this does not fit anywhere else.
        if self.char_state['fuel'] < JETPACK_MAX:
            self.char_state['fuel'] += JETPACK_REGEN

