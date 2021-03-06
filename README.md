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
 - Eliminate the show_card function.
 - Streamline CardImage, Hand, and Game classes for better 
   integration with rest of program. Makes generalizing the 
   game into other modes, card logic, and scoring function 
   easier to implement.
 - Generalize functions to allow for solitaire mode, player 
   vs computer, player vs player, and 2 vs 2.
 - Consider placement of decks to allow for above use cases, 
   e.g. player1 has deck on bottom and player2 has deck on 
   top, but only bottom deck appears in one player game, as  
   well as a corresponding change for four player mode.
 - Implement automatic, boring scoring (through console 
   text) for one deal for two players.

## Wishlist

 - Animate deck shuffling.
 - Implement restarting game while keeping track of total 
   score. 
 - Add pretty scoring.
 - Allow for different scoring options. Include auto vs 
   manual and also difficulty level of 'muggsy' rule.
 - Add option to change card backs.
 - Add multiple screens using screen manager, such as title 
   screen, options screen, credits screen, game screen, game 
   over screen, and possibly a scoring screen.
 - Perhaps a 'chessmaster' can be added to top of screen in 
   player vs computer mode? And avatars for player vs player.
 - Pegboard for keeping score along one side of the screen