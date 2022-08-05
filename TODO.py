# RESCUSCITATING FOR UBUNTU SYSTEM
"""
-see if I can fix the issue with june the cow being outside the forcefield in cutscene. Maybe use lift method?

-simplify pause/death/cutscene loop. Can we abstract away things that happen *every* loop? And build on that?
Eg currently cutscene loop doesn't handle dying (until it ends). Maybe just fix that case.

-figure out what to do about seeker, PIL dependency 
  -could make non-rotating seeker
  -or do conditional seeker, if PIL detected
  -could create 8 images representing different directions, just have less fidelity
  -or just remove for simplicity
  
-simplify external files/paths
  -Can we simplify image naming? Eg maybe the dict key is the SAME as image name,
   and we just use a list of names in a loop.
  -could put all images in single dir. Then use os.walk to generate every filename in 
   that dir, and then use a loop to load all images. Single function to load everything.
 
-literally just go through code and see what can be condensed (or removed :)

"""









#META, GENERAL NOTES
"""
remember: itch.io to publish, pygame + sprite/graphics libraries, git for version control. 
PIL for image editing. Game jams.

Think about creating an .exe. Does pygame have tool for that? 
pyinstaller --windowed --onefile --add-data "complex syntax" myApp.py 


"""


#TODO
"""

NEED:


WORTHWHIlE POLISH:

-make demo version the default. If this is in portfolio, we need to front-load the 
cool shit. Definitely have at least 2 missiles in first blocks, have cow real close.
And make it EASY lol, nobody wants to just lose instantly
If anybody besides me ever gets into this, maybe then we can update it.

-better graphics/animations. Work on having a consistent aesthetic. Cartoony. Come up 
with good style for stage. And use those empty/clear backgrounds. Graphics style may involving 
resizing, eg a larger control, a relatively smaller stage, maybe different screen size. 
Redo wrapper information. Also eyecandy for control--jump animation, brake, grooving while 
standstill, etc. And may need to redo image handling within move()

-^with above, may also want to redo cutscenes. 

-Finish sound fx. Add rough draft sounds for different stuff, weave into move(). Also may 
want to polish move() as well, to update animations.


"""


#REACH STUFF (LOW PRIORITY)
"""
-create newinteresting stages/mechanics. Eg new backgrounds/debris images, for starters. 
With new config files. Or, subclass the stage class, and implement new functionality
like wall of flame or oxygen. Asteroid field stage. Falling debris.

-Think about constellations as well. Mix random with pre-set configurations.

-find intelligent solution to problem of stage flying away. Maybe detect if a block is completely
empty / nontraversible, and spawn new debris for it?

-also maybe make life mechanic, eg you get x lives and then its game over. Fine
tune HS calculations (or don't, enfore by not spawning blocks past the cow)


-use PIL to randomly resize debris when spawned

-create switch to change gamespeed, eg play in slowmo or lowgrav


-Finish alien saucer concept. It flies in top right trying to match control speed. 
shoots lasers and missiles and maybe dumb rockets or mines. Can be outrun, or 
just flies away after a bit.

-non-hazard items, eg coins/currency, or powerups + powerup mechanics.

-build a store interface, upgrade paths, loadout selector, etc. Maybe this can all
be CLI text interface, if thats easier??

-dynamic camera, eg it slides ahead slightly to show more screen when moving quickly
This is hard to right, so that its responsive but also not too jerky. We had it as a function
of speed, but then if you hit something and stop, the whole view jerks. Steady might
be better.
-SPEED! past certain threshold, slow-motion. Zoom out (with black bars on
top and bottom). Same Y view, but X gets stretched to see more. Should be subtle,
but give sense of speed. May need to update blocks, given further view.
This could also be zooming in at rest
Have to handle abrupt stops--maybe special case for those?
there is a canvas.scale() function, but its complicated, also I don't think it works with
images (only bitmaps, rectangles, etc). There's discussion on this online, but it seems like
and intensive type solution.
-test x_mntm in move. once speed threshold reached, use slowmo method (on game?) to slide
over screen view gradually, and increase Frame rate. Then have exit_slomo method as well. 
Three cases: collide and stop, gradual slowdown, or death.


-create different characters, with different movement characteristics. Eg one has jetpack, or 
hangglider, or double jump, or whatever. 
"""



#ADD SOUNDS
"""
Use playsound() module. Add a sound class in sound module, that gets referenced to play
sounds.

can multiple soundclips play on top of each other?

Control:
-run (record footsteps, shoes on wood). this should have logic to be slower or faster
tempo depending on mntm
-jump (maybe like a grunt? or a whoosh?)
-land (two shoes landing)
-jetpack (use either stove burner, or camp stove. Short soundbyte, but loops continuously
for long burns

items:
-explosion. This can maybe be regular explode soundclip? or something more scifi.
If it misses, should play full explosion. If it kills control though, just play the 
attack and then immediate silence
-landmine tick. use either a clock tick, or my alarm beeping
-seeker should be either rocket ala jetpack, or maybe something more scifi. Think
of the submarine sound in Phantom Menace. Later maybe update graphics to have purple
bubble trail, instead of flame exhaust. TBD.

aliens:
-eventually I will want sound clips for the flying saucers. Look to starwars ships 
for inspiration.

music? Maybe sporadic and calm, like minecraft? Or something more driving, like
metroid prime hunters? Or maybe like spacey lofi. 

remember theres technically no sound in space, so realistic soundscape would just be 
internal spacesuit sounds like breathing, grunts, footsteps, and rustling.



"""


#ADD TESTS
"""
BUGS:
-X collisions. Getting stuck inside block, getting launched. Whats appropriate way 
to handle each of many cases? Also, if you get crushed that should be death.



PERFORMANCE:
-test timing of frameloop(), figure out if there's stutter / what could cause it.
Can use timeit or similar, to get timing that frameloop() and subloops take to process.
Maybe output the timing for each of these to a file, eg for each single frame, make
a new row that contains overall frameloop timing, and a breakdown of how long sub loops took.
cProfile module, for "profiling"


cProfile:
 ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   13.442   13.442 {built-in method builtins.exec}
        1    0.000    0.000   13.442   13.442 <string>:1(<module>)
        1    0.000    0.000   13.442   13.442 C:\Users\User\AppData\Local\Programs\Python\Python39\lib\tkinter\__init__.py:1427(mainloop)
        1   12.371   12.371   13.442   13.442 {method 'mainloop' of '_tkinter.tkapp' objects}
      405    0.004    0.000    1.071    0.003 C:\Users\User\AppData\Local\Programs\Python\Python39\lib\tkinter\__init__.py:1887(__call__)
      325    0.003    0.000    1.017    0.003 C:\Users\User\AppData\Local\Programs\Python\Python39\lib\tkinter\__init__.py:812(callit)
      260    0.004    0.000    0.842    0.003 C:\Users\User\Documents\Python Projects\Space Explorer\stage.py:433(update)
      177    0.006    0.000    0.639    0.004 C:\Users\User\Documents\Python Projects\Space Explorer\Platformer 3.51.py:176(frame_loop)
    32375    0.587    0.000    0.590    0.000 {method 'call' of '_tkinter.tkapp' objects}
      260    0.019    0.000    0.513    0.002 C:\Users\User\Documents\Python Projects\Space Explorer\items.py:78(update_items)


 ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1   12.371   12.371   13.442   13.442 {method 'mainloop' of '_tkinter.tkapp' objects}
    32375    0.587    0.000    0.590    0.000 {method 'call' of '_tkinter.tkapp' objects}
      260    0.061    0.000    0.309    0.001 C:\Users\User\Documents\Python Projects\Space Explorer\stage.py:461(drift)
    10440    0.043    0.000    0.151    0.000 C:\Users\User\AppData\Local\Programs\Python\Python39\lib\tkinter\__init__.py:2761(coords)
    18250    0.038    0.000    0.186    0.000 C:\Users\User\AppData\Local\Programs\Python\Python39\lib\tkinter\__init__.py:2872(gettags)
      177    0.026    0.000    0.026    0.000 {method 'globalsetvar' of '_tkinter.tkapp' objects}
      249    0.019    0.000    0.411    0.002 C:\Users\User\Documents\Python Projects\Space Explorer\items.py:274(seeker_move)
      260    0.019    0.000    0.513    0.002 C:\Users\User\Documents\Python Projects\Space Explorer\items.py:78(update_items)
    30274    0.017    0.000    0.017    0.000 {method 'splitlist' of '_tkinter.tkapp' objects}
      260    0.017    0.000    0.084    0.000 C:\Users\User\Documents\Python Projects\Space Explorer\control.py:113(move)


Based on the above, it looks like move() is not that expensive. 
Biggest performance bottleneck as I see it is in stage_update(), but note that this
calls both drift() and item_update() as submethods. So yeah its expensive.
code specifically within drift takes most time, 3x as much as item_update or seeker or
move().


timeit on frameloop:
When I ran, I'm getting anywhere from 0.001 to 0.005 (mostly 0.003) seconds
per frameloop (this excludes after() wait). For comparison, each frame also
includes a 0.03 second wait. So calc adds anywhere from 3% to 18% of time
on our decided framerate. Obv this could be better, but premature optimization
is the enemy of good code.


I tried Dunlavey's stack trace method, but (1) you can't really interrupt the tkinter 
thing, and (2) I already know most of the time is spent waiting, rather than actually 
processing. And also interrupt callback doesn't give back any of my actual code, usually
it shows some weird interal aspect of tk.



FINAL THOUGHTS
So obviously if I want to optimize, the place to start is stuff that runs within 
frame_loop(). drift() is expensive, so is item_update(), so is seeker_move(), and 
move() should be updated if only for clarity. And at somepoint I'm going to go back
and put real effort into improving those algos. But RIGHT NOW its not a top priority--
everything is running for the most part, and I still have functionality to build, 
and the brief testing I did did not indicate massive problems with any of those.


"""



#IDEAS / STORYBOARDING
"""
BIG SCALE IDEA: SPace Explorer. Home base is a ship--you can replenish fuel, health, buy upgrades,
navigate to another world. From ship you venture out left or right, to collect coins etc, and to
find the objective which is hidden somewhere (your key to next world). But its like motherlode--
you have to survive the trip back, for it to count. You unlock new planets/worlds, with different
themes and hazards and concepts (can use scenarios for ideas). 
 
Need to build and implement the content: all the upgrades/gizmos/coins/etc in stage,
plus new worlds/scenarios for each, plus the graphics for each world. Also meta stuff, like
what the ship interface is, the store, the world selector. Plus storyline cutscenes (or at least 
dialog). and this will also require a beefier wrapper, with options to save game, settings, etc. 

Plot: youre a texan rancher chasing aliens that abducted your cow. You track them by finding a 
cowpie in every world. Paul Bunyon chasing bessie the blue cow. Except you're regular size, and its
misspelled or something.

World scenarios (may also be separate game ideas).
-run from a flame wall, or from aliens, or the army 
-oxygen is running out, you need to make it to the next canister.
-fetch, try to catch up to a ball (or drone or UFO) 
-race against another asteroid/drone/UFO (same as above).
-massive square, you have to traverse from one side to other to complete tasks
-themes: tunnel, asteroids, satellites (all moving fast in same direction), satellite debris/trash,
alien planets (with lava hazards)
-boss battle you just run away. Or get aliens to shoot each other somehow.

Rewards: collect coins (of different values, like blue studs?) in each level. Also maybe lives,
other gizmos trinkets, powerups (unlimited jetpack, hang glider, slow mo)
Can buy things at home ship. Upgrade jump, jetpack, oxygen, armor, speed. Buy skins/aesthetic stuff.
1 time use stuff (powerups, cowpie sonar, drone to jump on, hang glider)
buy new stages/bonus levels/worlds.
Unlock different movement options, ala zelda wind waker? Eg you start with base jump, but unlock jetpack, hang
glider/parachut, double-jump, gecko shoes, grapple hook, teleport. Like LOZ loadout, can only use 
one or two at a time.

Have a 'cargo hold' like in motherlode? Eg the more coins you collect, the heavier/slower you 
move. And you don't get any credit until you bring it all back to ship.
This gives you another thing to upgrade as well.
Motherlode gives good idea of upgrade train, plus its a kind of motivation lol.


PRIORITY:
-gameplay and basic core mechanics
-items, powerups, movement options
-new worlds, animations, world-specific mechanics
-menus, store, internal ship interface 
-cutscenes and story.


NEW CONCEPT (simpler)
just have aliens kidnap cow from space farm, and control goes and brings her back.
"""
