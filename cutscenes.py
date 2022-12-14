#cutscenes with aliens!

import tkinter
import os

class Cutscenes:

    def __init__(self, parent, screen):
        self.PARENT = parent
        self.SCR = screen
        self.load_images()
        
        
        
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
        
        
        #------------------OBJECTS --------------#
        
        # start cutscene, create saucer and cow, black bars at top and bottom
        if clock == 5:
            self.saucer = self.SCR.create_image(
                -600, 150, image=self.images['saucer'],tags=('cutscene', 'saucer'), anchor='nw'
            )     
            self.cow = self.SCR.create_image(
                550, 344, image=self.PARENT.stage.farm_images['cow'], tags=('cutscene', 'june', 12),
                anchor='nw'
            )
            
            #black bars
            self.SCR.create_rectangle(
                -1000, 0, 9000, 100,fill='grey',tags=('cutscene', 'bars')
            )     
            self.SCR.create_rectangle(
                -1000, self.PARENT.WINDOW_HEIGHT-100, 9000, self.PARENT.WINDOW_HEIGHT,
                fill='grey',tags=('cutscene', 'bars')
            )
            
            # can we raise force field
            self.SCR.lift('force-field')
                                                 
        #move saucer over cow and use tractor
        elif clock > 5 and clock < 300:
            x_pos = self.SCR.coords(self.saucer)[0]
            y_pos = self.SCR.coords(self.saucer)[1]
            
            if x_pos < 500:
                self.SCR.coords(self.saucer, x_pos+4, y_pos)
              
        #activate tractor  
        elif clock == 320:
            self.SCR.itemconfig(self.saucer, image=self.images['tractor'])
                
        #run away with cow.
        elif clock > 330 and clock < 450:
            x_pos = self.SCR.coords(self.saucer)[0]
            y_pos = self.SCR.coords(self.saucer)[1]
            
            cow_x = self.SCR.coords(self.cow)[0]
            cow_y = self.SCR.coords(self.cow)[1]
            
            speed = clock - 330
            
            self.SCR.coords(self.saucer, x_pos+speed, y_pos)
            self.SCR.coords(self.cow, cow_x+speed, cow_y)
        
            
        #----------CAPTIONS--------------#
        if clock == 100:
            text = "Another boring day on the space farm.."
            self.caption = self.SCR.create_text(
                (200, 45),fill='black', anchor='n', text=text, tag=('cutscene', 'caption'),
                font=('arial, 18')
            )
        elif clock == 200:
            text = "When all of a sudden--"
            self.SCR.itemconfig(self.caption, text=text)
            
        elif clock == 320:
            text = "A cownapping! In broad starlight!"
            self.SCR.itemconfig(self.caption, text=text)
            
        elif clock == 380:
            text = "You better bring your cow back quick! To this here barn"
            self.SCR.itemconfig(self.caption, text=text)