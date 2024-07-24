// Register map:
//   r0 -> player position;
//   r1 -> food position;
//   r2 -> temp player next position;

nop

light_screen:
sta 0
lda score

light_screen_loop:
    sta score
    gpu unset
    add 1
    lda score
    != 0
    jmp light_screen_loop

init_registers:
  sta rand
  lda r0     // Random player position
  gpu set
  sta rand
  lda r1     // Random player position
  gpu set

game_loop:
  sta key    // Read input

is_move_up:
  != 1
  jmp is_move_right
  sta r0  // Load player position into accumulator
  sub 4   // x = x - 1
  lda r2  // Store score in r2
  sta 1
  jmp refresh_screen

is_move_right:
  sta key    // Read input
  != 2
  jmp is_move_down
  sta r0  // Load player position into accumulator
  add 1   // y = y + 1
  lda r2  // Store score in r2
  sta 1
  jmp refresh_screen

is_move_down:
  sta key    // Read input
  != 4
  jmp move_left
  sta r0  // Load player position into accumulator
  add 4   // x = x + 1
  lda r2  // Store score in r2
  sta 1
  jmp refresh_screen

move_left:
  sta r0  // Load player position into accumulator
  sub 1   // y = y - 1
  lda r2  // Store score in r2

refresh_screen:
  sta r0
  gpu unset
  sta r2
  gpu set
  lda r0

check_score:
  != r1
  jmp game_loop
  sta score
  add 1
  lda score

update_food_pos:
  sta rand
  lda r1
  == r0
  jmp update_food_pos
  sta r1
  gpu set
  sta 1
  jmp game_loop
