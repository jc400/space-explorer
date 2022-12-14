#Platformer

import control
import stage
import cutscenes
import tkinter
import time
import os


class Game:
    
    #-----------INIT & SETUP ----------------------#
    def __init__(self):
        
        self.ROOT = tkinter.Tk()
        self.ROOT.title('Space Explorer')
        icon = tkinter.PhotoImage(file='icon.png')
        self.ROOT.tk.call('wm', 'iconphoto', self.ROOT._w, icon)
        
        #constants
        self.WINDOW_WIDTH = self.ROOT.winfo_screenwidth()           #1200 *2
        self.WINDOW_HEIGHT = self.ROOT.winfo_screenheight() - 100   # 700 *2
        self.FRAMERATE = 30
        self.BLOCKSIZE = 2000
        self.RESCUE_SCALE_FACTOR = 5 #cow spawns at rescue_iter * scale_factor + 2
        
        #in-game variables
        self.clock = 0
        self.block_number = 0       #used in stage_updated() to determine spawning
        self.rescue_iter = 1        
        self.hold_june = False
        self.stop_movement = False  #checked in control.move(), used to stop motion on death
        self.paused = False         #check in frame_loop()
        self.game_over = False      #check in frame_loop(), also in move()
        self.cutscene = None        #fed into cutscenes.play(). steal, rescue, return?
        

        #bind keypress to callback func
        #ubuntu has weird key events, may need Settings --> Universal Access --> Repeat Keys --> Off
        self.ROOT.bind_all('<KeyPress>', self.on_keypress)
        self.ROOT.bind_all('<KeyRelease>', self.on_keyrelease)

        #create display elements 
        self.create_HUD()        
        self.scr = tkinter.Canvas(self.ROOT,
                                  width=self.WINDOW_WIDTH,
                                  height=self.WINDOW_HEIGHT,
                                  bg='black',
                                  highlightbackground='black',
                                  scrollregion=(0, 0, self.WINDOW_WIDTH, self.WINDOW_HEIGHT),
                                  confine=False,
                                 )
        self.scr.pack(side='top')
        

        #create and spawn child objects
        self.control = control.Control(self, self.scr)
        self.stage = stage.Stage(self, self.scr)
        self.cutscenes = cutscenes.Cutscenes(self, self.scr)
        
        #reset() spawns all the stage adn items and initializes everything
        self.reset()
        
        #start cutscene
        self.cutscene = 'steal'
        
        #start frame loop.
        time.sleep(.5)
        self.frame_loop()
        
        # Switch for profiling
        if False:
            import cProfile
            cProfile.runctx('self.ROOT.mainloop()', globals=globals(), locals=locals())          
        else: 
            self.ROOT.mainloop()
        
        
    def create_HUD(self):
    
        self.frame1 = tkinter.Frame(self.ROOT, bg='black')
        self.frame1.pack(side='top', fill='x')
        
        #speed
        tkinter.Label(self.frame1, text='Speed: ', bg='black', fg='white').pack(side='left')
        self.speed_var = tkinter.IntVar()
        self.speed_var.set(0)
        tkinter.Label(self.frame1, textvar=self.speed_var, bg='black', fg='white', width=3).pack(side='left')

        #distance
        tkinter.Label(self.frame1, text='           Distance: ', bg='black', fg='white').pack(side='left')
        self.dist_var = tkinter.IntVar()
        self.dist_var.set(0)
        tkinter.Label(self.frame1, textvar=self.dist_var, bg='black', fg='white', width=5).pack(side='left')

        #jetpack fuel
        tkinter.Label(self.frame1, text='           Fuel: ', bg='black', fg='white').pack(side='left')
        self.fuel_var = tkinter.StringVar()
        self.fuel_var.set('|||||')
        tkinter.Label(self.frame1, textvar=self.fuel_var, bg='black', fg='white', width=5, justify='left').pack(side='left')
        

    def on_keypress(self, event):
        """Callback. Translates key to direction, updates xdir/ydir"""
        kp = event.keysym.lower()
        direction_dict = {'a':'left',
                          'd':'right',
                          'w':'jump',
                          's':'jetpack',
                          }
                        
        if kp == 'a' or kp == 'd':
            self.control.xdir = direction_dict[kp] 
        if kp == 'w' or kp == 's':
            self.control.ydir = direction_dict[kp]
            
        if kp == 'p':
            self.paused = not self.paused

    def on_keyrelease(self, event):
        """Ensures direction continues until let go"""
        kr = event.keysym.lower()
        if (kr == 'a' and self.control.xdir == 'left') or (kr == 'd' and self.control.xdir == 'right'):
            self.control.xdir = None
        if kr == 'w' or kr == 's':
            self.control.ydir = None
       

    #----------------GAME ACTUALLY RUNNING---------#

    def frame_loop(self):
        """Runs each frame. This is mostly meta--call functionality from stage/control.
        
        Most of the processing here is either logic, or directly updating our view
        
        Each frame we:
        -drift every stage element, and slide
        -calculate control state/movement, update image, move position
        -handle collisions (mostly killbox rn)
        -move our screenview based on control movement.
        -update clock, HUD stuff.
        -check for new block, handle staircase/deletion if threshold hits
        """
        
        if self.game_over:
            self.death_loop()
            return
        
        if self.paused:
            self.scr.create_rectangle((self.control.position[0]-self.WINDOW_WIDTH, 
                                       0,
                                       self.control.position[0]+self.WINDOW_WIDTH,
                                       self.WINDOW_HEIGHT),
                                       fill='gray',
                                       stipple='gray50',
                                       tag=('pause'))
            self.pause_loop()
            return
            
        if self.cutscene:
            self.clock = 1
            self.cutscene_loop()
            return
      
        #catchall functions, bundles everything control/stage need to update
        self.control.update()
        self.stage.update()
        
        #update screen view according to control position.
        self.scr.xview_moveto((self.control.position[0] 
                               -(self.WINDOW_WIDTH / 2)) 
                               / self.WINDOW_WIDTH)
        
        #update clock, update HUD values.
        self.clock = (self.clock + 1) % 100
        if self.clock % 3 == 0:
            self.speed_var.set(float(format(self.control.move_state['x_mntm'], '.2f')))
            self.dist_var.set(float(format(self.control.position[0], '.1f')))
            self.fuel_var.set(int(self.control.char_state['fuel'])*'|')    

        #loop back on self
        self.scr.after(self.FRAMERATE, self.frame_loop)

    
    def pause_loop(self):
        if self.paused:
            self.scr.after(self.FRAMERATE, self.pause_loop)
        else:
            self.scr.delete('pause')
            self.frame_loop()
            

    def death_loop(self):
        #slow down and bring to halt.
        if self.control.move_state['x_mntm'] > 1:
            self.control.move_state['x_mntm'] -= 0.5

        elif self.control.move_state['x_mntm'] != 0:
            self.control.move_state['x_mntm'] = 0
        
        # calc score and display message. Only do once
        if self.clock == 120:
            score = self.calc_score(self.dist_var.get(), self.rescue_iter)
            text = "Your score: " + str(format(score, '.2f'))
            self.scr.create_text((self.control.position[0], self.WINDOW_HEIGHT // 2),
                                                fill='white', anchor='n', text=text, tag=('message'),
                                                font=('arial, 20'))

        #this stuff happens each loop, just like on frame_loop()
        self.stage.update()
        self.control.update()
        self.scr.xview_moveto((self.control.position[0] 
                           -(self.WINDOW_WIDTH / 2)) 
                           / self.WINDOW_WIDTH)
                           
        #clock is different, we're intentionally counting up to infinity 
        self.clock += 1
        
        #check for restart, hit reset(), then restart frame_loop()
        if self.control.ydir == 'jump' and self.clock > 121:
            self.reset()
            self.frame_loop()
            return
        
        #and we loop this whole function just like frame_loop
        self.scr.after(self.FRAMERATE, self.death_loop)

    
    def cutscene_loop(self):
        
        #I want to move the text with control, if player decides to scram
        if self.clock > 100:
            self.scr.coords(self.cutscenes.caption, (self.control.position[0], 45))
                
        #Cutscene ends at 451                  
        if self.clock == 451:
            self.cutscene = False
            self.scr.delete('cutscene')
            self.frame_loop()
            return
        
        #call cutscenes 
        self.cutscenes.play(self.cutscene, self.clock)
        
        # handle death
        if self.game_over:
            self.clock = 1
            self.death_loop()
            return
        
        #catchall functions, bundles everything control/stage need to update
        self.control.update()
        self.stage.update()
        
        #update screen view according to control position.
        self.scr.xview_moveto((self.control.position[0] 
                               -(self.WINDOW_WIDTH / 2)) 
                               / self.WINDOW_WIDTH)
        
        #clock is different, we're intentionally counting up to infinity 
        self.clock += 1
        
        # still update HUD though
        if self.clock % 3 == 0:
            self.speed_var.set(float(format(self.control.move_state['x_mntm'], '.2f')))
            self.dist_var.set(float(format(self.control.position[0], '.1f')))
            self.fuel_var.set(int(self.control.char_state['fuel'])*'|')    

        #loop back on self
        self.scr.after(self.FRAMERATE, self.cutscene_loop)

    #----------------GAMEOVER STUFF------------------#
    
    def reset(self):
       
        #delete current blocks and respawn chitza (make stage.reset()?
        self.stage.clear_all(self.block_number)
        self.stage.spawn_chitza()
        
        #reset game_state
        self.block_number = 0
        self.rescue_iter = 1
        self.hold_june = False
        
        self.game_over = False 
        self.stop_movement = False
        
        
        #reset player state and position
        self.control.reset()
        
    
    def calc_score(self, distance, r_iter):
        """With current gameflow, its like suicides. Go back and forth, back and 
        forth. So total distance is however far you've traveled on prev iterations, 
        plus however far you've traveled on the current lap.
        
        For a completed lap, it's this times 2 (there and back)
        
         cow offset in block     convert to px     iter     pasture triggered          actuatlly spawned 2 blocks ahead
        (1400 +                 (self.BLOCKSIZE * (i *      self.RESCUE_SCALE_FACTOR + 2)))
        """
        
        prev_dist = 0
        
        for i in range(1, r_iter):
            #for each rescue, calc the dist to cow * 2
            prev_dist += 2 * (1400 + (self.BLOCKSIZE * (i * self.RESCUE_SCALE_FACTOR + 2)))

        #if holding cow, we've been there and are heading back.
        if self.hold_june:
            cur_dist = (2 * (1400 + (self.BLOCKSIZE * ((r_iter * self.RESCUE_SCALE_FACTOR)+2)))) - distance
        else:
            cur_dist = distance 
            
        return prev_dist + cur_dist
 

test = Game()
