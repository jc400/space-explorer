#cutscenes with aliens!

"""
have three sequences: Steal, rescue, return

When each is initialized, we need to set stop_movement to true, we need to create the
black bars on top and bottom, and we need to start cutscene loop in main.

There's also some gamestate updates to make--eg carrying June, rescue iteration, 
reload images, and so forth.

Maybe all of this can be handled in the collision_logic() if statement. Or maybe we 
should create a meta function that handles all the updates separated out. It's really 
simple logic, but there are a lot of necessary state changes.

If we set the clock value before we call the cutscene loop, we can put a "if clock==1" 
clause into the cutscene itself, and handle updates there. 

Note that we also need cutscene_loop to call the correct cutscene. maybe we should
pass it an argument? Which it passes to the cutscene function here? 
But the after() call doesn't take args, no?


"""


import tkinter
import os



class Cutscenes:

    def __init__(self, parent, screen):
    
        self.PARENT = parent
        self.SCR = screen
        
        self.load_images()
        
        #vars to hold cutscene images
        self.saucer = None
        self.cow = None
        
        
    def load_images(self):
        PATH =  os.path.join('images', 'stage', 'alien')
        self.images = {
            'saucer':tkinter.PhotoImage(file=os.path.join(PATH, 'saucer.png')),
            'tractor':tkinter.PhotoImage(file=os.path.join(PATH, 'tractor.png'))
        }
        
   
    def play(self, cutscene, clock):
        
        if cutscene == 'steal':
            self.steal(clock)
            
        elif cutscene == 'rescue':
            pass
            
        elif cutscene == 'return':
            pass
            

    def steal(self, clock):
        
        #create ship
        if clock == 5:
            self.saucer = self.SCR.create_image(-600, 150, 
                                  image=self.images['saucer'],
                                  tags=('cutscene', 'saucer'),
                                  anchor='nw')
                                  
            #self.cow = self.SCR.find_withtag('june')
            self.cow = self.SCR.create_image(550, 344, 
                                  image=self.PARENT.stage.farm_images['cow'],
                                  tags=('cutscene', 'june', 12),
                                  anchor='nw')
                                  
            self.PARENT.stage.spawn_farm()
                                  
                                  
        #move saucer over cow and use tractor
        elif clock > 5 and clock < 300:
            
            x_pos = self.SCR.coords(self.saucer)[0]
            y_pos = self.SCR.coords(self.saucer)[1]
            
            if x_pos < 500:
                self.SCR.coords(self.saucer, x_pos+4, y_pos)
                
                
        elif clock == 320:
            self.SCR.itemconfig(self.saucer, image=self.images['tractor'])
                
        
        #run away with cow.
        elif clock > 330 and clock < 450:
            x_pos = self.SCR.coords(self.saucer)[0]
            y_pos = self.SCR.coords(self.saucer)[1]
            
            cow_x = self.SCR.coords(self.cow)[0]
            cow_y = self.SCR.coords(self.cow)[1]
            
            self.SCR.coords(self.saucer, x_pos+8, y_pos)
            self.SCR.coords(self.cow, cow_x+8, cow_y)
        
        #end of cutscene, change june_at_home and delete cutscene images
        elif clock == 450:
            #self.PARENT.june_at_home = False
            self.SCR.delete(self.saucer)
            self.SCR.delete(self.cow)
            
            
        #----------CAPTIONS--------------#
        if clock == 100:
            text = "Another boring day on the space farm.."
            self.caption = self.SCR.create_text((200, 45),
                                  fill='black', anchor='n', text=text, tag=('cutscene', 'caption'),
                                  font=('arial, 18'))
        elif clock == 200:
            text = "When all of a sudden--"
            self.SCR.itemconfig(self.caption, text=text)
            
        elif clock == 320:
            text = "A cownapping! In broad starlight!"
            self.SCR.itemconfig(self.caption, text=text)
            
        elif clock == 380:
            text = "You better bring your cow back quick! To this here barn"
            self.SCR.itemconfig(self.caption, text=text)
        
        elif clock == 450:
            self.SCR.delete(self.caption)