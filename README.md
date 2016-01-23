# Griddage

## Overview

Griddage is played by two or more players taking turns 
placing a card on a 5x5 grid until the grid is filled. 
Scoring then proceeds based on cribbage rules, treating 
each row and column as a separate hand. One player scores 
the rows, the other the columns. Play continues until one 
player reaches the predetermined limit, usually 61 or 121 
points.

## Implemented

 - Animate cards moving from hand to chosen grid tile.


## Wishlist

 - Animate deck shuffling.
 - Implement scoring and restarting game, as well as keeping 
   track of total score. First boring scoring, then pretty 
   scoring.
 - Allow for different scoring options. Include auto vs 
   manual and also difficulty level of 'muggsy' rule.
 - Generalize functions to allow for solitaire mode, player 
   vs computer, player vs player, and 2 vs 2.
 - Especially the show_card function.
 - Consider placement of decks to allow for above use cases, 
   e.g. player1 has deck on bottom and player2 has deck on 
   top, but only bottom deck appears in one player game, as  
   well as a corresponding change for four player mode.
 - Add option to change card backs.
 - Add multiple screens using screen manager, such as title 
   screen, options screen, credits screen, game screen, game 
   over screen, and possible a scoring screen.
 - Perhaps a 'chessmaster' can be added to top of screen in 
   player vs computer mode? And avatars for player vs player.