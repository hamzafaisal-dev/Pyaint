import pygame as pygame
import settings
import button

def draw_history_win(win, grid):
    win.fill(BG_COLOR)

    draw_grid(win, grid)

    buttons = [
        Button(WIDTH - 3 * button_space - 370, button_y_top_row, button_width - 5, button_height - 5, name="LEFT ARROW", image_url="C:/Users/Hamza/Downloads/Pyaint-master (ver-4)/assets/LEFT ARROW.png"),
        Button(WIDTH - 3 * button_space - 570, button_y_top_row, button_width - 5, button_height - 5, name="RIGHT ARROW", image_url="C:/Users/Hamza/Downloads/Pyaint-master (ver-4)/assets/RIGHT ARROW.png")
    ]

    for button in buttons:
        button.draw(win)

    pygame.display.update()

History_window = pygame.display.set_mode((WIDTH + RIGHT_TOOLBAR_WIDTH, HEIGHT))
pygame.display.set_caption("Viewing History")

draw_history_win(History_window, grid)
pygame.display.update()

running = True
  
# game loop
while running:
    
# for loop through the event queue  
    for event in pygame.event.get():
      
       # Check for QUIT event      
            if event.type == pygame.QUIT:
                running = False