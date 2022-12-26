import main
from utils import *
import copy
import pygame as pygame

WIN = pygame.display.set_mode((WIDTH + RIGHT_TOOLBAR_WIDTH, HEIGHT))
pygame.display.set_caption("Pyaint")

STATE = "COLOR"
Change = False

undo_count = 0
action_index = 0
animated_history_index = 0
undo_stack = []
redo_stack = []
actions_stack = []


def add_action(grid):
    actions_stack.append(copy.deepcopy(grid))


def init_grid(rows, columns, color):
    grid = []

    for i in range(rows):
        grid.append([])
        for _ in range(columns):  # use _ when variable is not required
            grid[i].append(color)

    return grid


undo_stack.append(init_grid(ROWS, COLS, BG_COLOR))
add_action(init_grid(ROWS, COLS, BG_COLOR))


def draw_grid(win, grid):
    for i, row in enumerate(grid):
        for j, pixel in enumerate(row):
            pygame.draw.rect(win, pixel, (j * PIXEL_SIZE, i * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))

    if DRAW_GRID_LINES:
        for i in range(ROWS + 1):
            pygame.draw.line(win, SILVER, (0, i * PIXEL_SIZE), (WIDTH, i * PIXEL_SIZE))
        for i in range(COLS + 1):
            pygame.draw.line(win, SILVER, (i * PIXEL_SIZE, 0), (i * PIXEL_SIZE, HEIGHT - TOOLBAR_HEIGHT))


def draw_mouse_position_text(win):
    pos = pygame.mouse.get_pos()
    pos_font = get_font(MOUSE_POSITION_TEXT_SIZE)
    try:
        row, col = get_row_col_from_pos(pos)
        text_surface = pos_font.render(str(row) + ", " + str(col), 1, BLACK)
        win.blit(text_surface, (5, HEIGHT - TOOLBAR_HEIGHT))
    except IndexError:
        for button in buttons:
            if not button.hover(pos):
                continue
            if button.text == "Clear":
                text_surface = pos_font.render("Clear Everything", 1, BLACK)
                win.blit(text_surface, (10, HEIGHT - TOOLBAR_HEIGHT))
                break
            if button.text == "Erase":
                text_surface = pos_font.render("Erase", 1, BLACK)
                win.blit(text_surface, (10, HEIGHT - TOOLBAR_HEIGHT))
                break
            if button.name == "FillBucket":
                text_surface = pos_font.render("Fill Bucket", 1, BLACK)
                win.blit(text_surface, (10, HEIGHT - TOOLBAR_HEIGHT))
                break
            if button.name == "Brush":
                text_surface = pos_font.render("Brush", 1, BLACK)
                win.blit(text_surface, (10, HEIGHT - TOOLBAR_HEIGHT))
                break
            if button.name == "ViewHistory":
                text_surface = pos_font.render("View History", 1, BLACK)
                win.blit(text_surface, (10, HEIGHT - TOOLBAR_HEIGHT))
                break
            if button.name == "ViewAnimatedHistory":
                text_surface = pos_font.render("View Animated History", 1, BLACK)
                win.blit(text_surface, (10, HEIGHT - TOOLBAR_HEIGHT))
                break
            if button.name == "UNDO":
                text_surface = pos_font.render("UNDO", 1, BLACK)
                win.blit(text_surface, (10, HEIGHT - TOOLBAR_HEIGHT))
                break
            if button.name == "REDO":
                text_surface = pos_font.render("REDO", 1, BLACK)
                win.blit(text_surface, (10, HEIGHT - TOOLBAR_HEIGHT))
                break
            if button.name == "Change":
                text_surface = pos_font.render("Swap Toolbar", 1, BLACK)
                win.blit(text_surface, (10, HEIGHT - TOOLBAR_HEIGHT))
                break
            r, g, b = button.color
            text_surface = pos_font.render("( " + str(r) + ", " + str(g) + ", " + str(b) + " )", 1, BLACK)

            win.blit(text_surface, (10, HEIGHT - TOOLBAR_HEIGHT))

        for button in brush_widths:
            if not button.hover(pos):
                continue
            if button.width == size_small:
                text_surface = pos_font.render("Small-Sized Brush", 1, BLACK)
                win.blit(text_surface, (10, HEIGHT - TOOLBAR_HEIGHT))
                break
            if button.width == size_medium:
                text_surface = pos_font.render("Medium-Sized Brush", 1, BLACK)
                win.blit(text_surface, (10, HEIGHT - TOOLBAR_HEIGHT))
                break
            if button.width == size_large:
                text_surface = pos_font.render("Large-Sized Brush", 1, BLACK)
                win.blit(text_surface, (10, HEIGHT - TOOLBAR_HEIGHT))
                break


def draw(win, grid, buttons):
    win.fill(BG_COLOR)

    draw_grid(win, grid)

    for button in buttons:
        button.draw(win)

    draw_brush_widths(win)
    draw_mouse_position_text(win)
    pygame.display.update()


def draw_history_win(win, grid):
    win.fill(BG_COLOR)

    draw_grid(win, grid)

    for button in history_buttons:
        button.draw(win)

    pygame.display.update()


def draw_animated_history_win(win, grid):
    win.fill(BG_COLOR)

    draw_grid(win, grid)

    for button in animated_history_buttons:
        button.draw(win)

    pygame.display.update()


def draw_brush_widths(win):
    brush_widths = [
        Button(rtb_x - size_small / 2, 480, size_small, size_small, drawing_color, None, None, "ellipse"),
        Button(rtb_x - size_medium / 2, 510, size_medium, size_medium, drawing_color, None, None, "ellipse"),
        Button(rtb_x - size_large / 2, 550, size_large, size_large, drawing_color, None, None, "ellipse")
    ]
    for button in brush_widths:
        button.draw(win)
        # Set border colour
        border_color = BLACK
        if button.color == BLACK:
            border_color = GRAY
        else:
            border_color = BLACK
        # Set border width
        border_width = 2
        if ((BRUSH_SIZE == 1 and button.width == size_small) or (BRUSH_SIZE == 2 and button.width == size_medium) or (
                BRUSH_SIZE == 3 and button.width == size_large)):
            border_width = 4
        else:
            border_width = 2
        # Draw border
        pygame.draw.ellipse(win, border_color, (button.x, button.y, button.width, button.height),
                            border_width)  # border


def get_row_col_from_pos(pos):
    x, y = pos
    row = y // PIXEL_SIZE
    col = x // PIXEL_SIZE

    if row >= ROWS:
        raise IndexError
    if col >= COLS:
        raise IndexError
    return row, col


def paint_using_brush(row, col, size):
    if BRUSH_SIZE == 1:
        grid[row][col] = drawing_color
    else:  # values greater than 1
        r = row - BRUSH_SIZE + 1
        c = col - BRUSH_SIZE + 1

        for i in range(BRUSH_SIZE * 2 - 1):
            for j in range(BRUSH_SIZE * 2 - 1):
                if r + i < 0 or c + j < 0 or r + i >= ROWS or c + j >= COLS:
                    continue
                grid[r + i][c + j] = drawing_color

    add_to_undo_stack(grid)
    add_action(grid)


# Checks whether the coordinated are within the canvas
def inBounds(row, col):
    if row < 0 or col < 0:
        return 0
    if row >= ROWS or col >= COLS:
        return 0
    return 1


def fill_bucket(row, col, color):
    # Visiting array
    vis = [[0 for i in range(101)] for j in range(101)]

    # Creating queue for bfs
    obj = [[row, col]]

    # Pushing pair of {x, y}

    # Marking {x, y} as visited
    vis[row][col] = 1

    # Until queue is empty
    while len(obj) > 0:

        # Extracting front pair
        coord = obj[0]
        x = coord[0]
        y = coord[1]
        preColor = grid[x][y]

        grid[x][y] = color

        # Popping front pair of queue
        obj.pop(0)

        # For Upside Pixel or Cell
        if inBounds(x + 1, y) == 1 and vis[x + 1][y] == 0 and grid[x + 1][y] == preColor:
            obj.append([x + 1, y])
            vis[x + 1][y] = 1

        # For Downside Pixel or Cell
        if inBounds(x - 1, y) == 1 and vis[x - 1][y] == 0 and grid[x - 1][y] == preColor:
            obj.append([x - 1, y])
            vis[x - 1][y] = 1

        # For Right side Pixel or Cell
        if inBounds(x, y + 1) == 1 and vis[x][y + 1] == 0 and grid[x][y + 1] == preColor:
            obj.append([x, y + 1])
            vis[x][y + 1] = 1

        # For Left side Pixel or Cell
        if inBounds(x, y - 1) == 1 and vis[x][y - 1] == 0 and grid[x][y - 1] == preColor:
            obj.append([x, y - 1])
            vis[x][y - 1] = 1
    add_to_undo_stack(grid)
    add_action(grid)

# Add a copy of the current state of the grid to the undo stack whenever the user makes a change                                     
def add_to_undo_stack(grid):
    undo_stack.append(copy.deepcopy(grid))


# redo function
def redo():
    add_to_undo_stack(main.grid)
    if not redo_stack:
        return

    temp = redo_stack.pop()

    main.grid = temp

# Undo function
def undo():
    # Push the current state of the grid to the redo stack
    redo_stack.append(copy.deepcopy(grid))

    # checks if stack is empty
    if not undo_stack:
        return

    if len(undo_stack) == 1:
        main.grid = init_grid(ROWS, COLS, BG_COLOR)
        return

    # Pop the top element from the undo stack and store it in a temporary variable
    if undo_count == 0:
        undo_stack.pop()
        temp = undo_stack.pop()
    else:
        temp = undo_stack.pop()

    main.undo_count = undo_count + 1

    # Set the current grid to the value stored in the temporary variable
    main.grid = temp

run = True

clock = pygame.time.Clock()
grid = init_grid(ROWS, COLS, BG_COLOR)
drawing_color = BLACK

button_width = 40
button_height = 40
button_y_top_row = HEIGHT - TOOLBAR_HEIGHT / 2 - button_height - 1
button_y_bot_row = HEIGHT - TOOLBAR_HEIGHT / 2 + 1
button_space = 42

size_small = 25
size_medium = 35
size_large = 50

history_buttons = [
    Button(WIDTH - 3 * button_space - 450, button_y_top_row, button_width - 5, button_height - 5, name="LEFT ARROW",
           image_url="assets/LEFT ARROW.jpg"),
    Button(WIDTH - 3 * button_space - 200, button_y_top_row, button_width - 5, button_height - 5, name="RIGHT ARROW"
           , image_url="assets/RIGHT ARROW.jpg")
]

animated_history_buttons = [
    Button(WIDTH - 3 * button_space - 840, button_y_top_row,
           button_width + 5, button_height, WHITE, "START", BLACK)
]

rtb_x = WIDTH + RIGHT_TOOLBAR_WIDTH / 2
brush_widths = [
    Button(rtb_x - size_small / 2, 480, size_small, size_small, drawing_color, None, "ellipse"),
    Button(rtb_x - size_medium / 2, 510, size_medium, size_medium, drawing_color, None, "ellipse"),
    Button(rtb_x - size_large / 2, 550, size_large, size_large, drawing_color, None, "ellipse")
]

# Adding Buttons
buttons = []

for i in range(int(len(COLORS) / 2)):
    buttons.append(Button(100 + button_space * i, button_y_top_row, button_width, button_height, COLORS[i]))

for i in range(int(len(COLORS) / 2)):
    buttons.append(
        Button(100 + button_space * i, button_y_bot_row, button_width, button_height, COLORS[i + int(len(COLORS) / 2)]))

# Right toolbar buttons
# need to add change toolbar button.
for i in range(10):
    if i == 0:
        buttons.append(
            Button(HEIGHT - 0.5 * button_width + 313, (i * button_height) + 5, button_width, button_height, WHITE,
                   name="Change"))  # Change toolbar buttons
    else:
        buttons.append(
            Button(HEIGHT - 0.5 * button_width + 313, (i * button_height) + 5, button_width, button_height, WHITE,
                   "B" + str(i - 1), BLACK))  # append tools

buttons.append(
    Button(WIDTH - button_space, button_y_top_row, button_width, button_height, WHITE, "Erase", BLACK))  # Erase Button
buttons.append(
    Button(WIDTH - button_space, button_y_bot_row, button_width, button_height, WHITE, "Clear", BLACK))  # Clear Button
# View History button border
buttons.append(
    Button(WIDTH - 2 * button_space - 10, button_y_top_row, button_width + 8, button_height + 28, WHITE, "", BLACK,
           name="ViewHistory"))
# View History Button
buttons.append(Button(WIDTH - button_space - 48, button_y_top_row + 4, button_width - 0.5, button_height + 18, WHITE,
                      name="ViewHistory",
                      image_url="assets/View_History_Vector.png"))
# View Animated History button border
buttons.append(
    Button(WIDTH - 2 * button_space - 67, button_y_top_row, button_width + 15, button_height + 28, WHITE, "", BLACK,
           name="ViewAnimatedHistory"))
# View Animated History Button
buttons.append(Button(WIDTH - button_space - 106, button_y_top_row + 4, button_width + 8, button_height + 20, WHITE,
                      name="ViewAnimatedHistory",
                      image_url="assets/Animated_History_Vector.png"))
# FillBucket
buttons.append(
    Button(WIDTH - 3 * button_space - 370, button_y_top_row, button_width - 5, button_height - 5, name="FillBucket",
           image_url="assets/paint-bucket.png"))
# Brush
buttons.append(
    Button(WIDTH - 3 * button_space - 330, button_y_top_row, button_width - 5, button_height - 5, name="Brush",
           image_url="assets/paint-brush.png"))
# REDO button
buttons.append(Button(WIDTH - 3 * button_space - 330, button_y_top_row + 45, button_width - 8, button_height - 9,
                      WHITE, name="REDO", image_url="assets/REDO.png"))
# UNDO button
buttons.append(
    Button(WIDTH - 3 * button_space - 370, button_y_top_row + 46.5, button_width - 8, button_height - 8.5,
           WHITE, name="UNDO", image_url="assets/UNDO.png"))

draw_button = Button(5, HEIGHT - TOOLBAR_HEIGHT / 2 - 30, 60, 60, drawing_color)
buttons.append(draw_button)

while run:
    clock.tick(FPS)  # limiting FPS to 60 or any other value

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # if user closed the program
            run = False

        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()

            try:
                row, col = get_row_col_from_pos(pos)

                if inBounds(row, col):
                    if len(redo_stack) > 0:
                        add_to_undo_stack(main.grid)
                        redo_stack.clear()

                if STATE == "COLOR":
                    paint_using_brush(row, col, BRUSH_SIZE)

                elif STATE == "FILL":
                    fill_bucket(row, col, drawing_color)

            except IndexError:
                for button in buttons:
                    if not button.clicked(pos):
                        continue
                    if button.text == "Clear":
                        grid = init_grid(ROWS, COLS, BG_COLOR)
                        drawing_color = BLACK
                        draw_button.color = drawing_color
                        STATE = "COLOR"
                        break

                    if button.name == "UNDO":
                        undo()
                        if grid == init_grid(ROWS, COLS, BG_COLOR):
                            main.undo_count = 0
                        add_action(main.grid)
                        break

                    if button.name == "REDO":
                        redo()
                        add_action(main.grid)
                        break

                    if button.name == "ViewHistory":
                        History_window = pygame.display.set_mode((WIDTH + RIGHT_TOOLBAR_WIDTH, HEIGHT))
                        pygame.display.set_caption("Viewing History")

                        draw_history_win(History_window, actions_stack[0])
                        pygame.display.update()

                        running = True

                        # game loop
                        while running:

                            # for loop through the event queue  
                            for event in pygame.event.get():

                                # Check for QUIT event      
                                if event.type == pygame.QUIT:
                                    action_index = 0
                                    running = False

                                if pygame.mouse.get_pressed()[0]:
                                    pos = pygame.mouse.get_pos()

                                    try:
                                        row, col = get_row_col_from_pos(pos)
                                    except IndexError:
                                        for button in history_buttons:
                                            if not button.clicked(pos):
                                                continue
                                            if button.name == "LEFT ARROW":
                                                if not actions_stack or len(actions_stack) == 1 or action_index == 0:
                                                    break
                                                action_index -= 1
                                                draw_history_win(History_window, actions_stack[action_index])
                                                pygame.display.update()
                                                break
                                            if button.name == "RIGHT ARROW":
                                                if action_index == len(actions_stack) - 1:
                                                    break
                                                action_index += 1
                                                draw_history_win(History_window, actions_stack[action_index])
                                                pygame.display.update()
                                                break
                        break

                    if button.name == "ViewAnimatedHistory":
                        Animated_history_window = pygame.display.set_mode((WIDTH + RIGHT_TOOLBAR_WIDTH, HEIGHT))
                        pygame.display.set_caption("Viewing Animated History")

                        draw_animated_history_win(
                            Animated_history_window, actions_stack[0])
                        pygame.display.update()

                        running = True

                        # game loop
                        while running:

                            # for loop through the event queue
                            for event in pygame.event.get():

                                # Check for QUIT event
                                if event.type == pygame.QUIT:
                                    animated_history_index = 0
                                    running = False

                                if pygame.mouse.get_pressed()[0]:
                                    pos = pygame.mouse.get_pos()

                                    try:
                                        row, col = get_row_col_from_pos(pos)
                                    except IndexError:
                                        for button in animated_history_buttons:
                                            if not button.clicked(pos):
                                                continue
                                            if button.text == "START":
                                                for i in range(len(actions_stack)):
                                                    if len(actions_stack) == animated_history_index:
                                                        break
                                                    draw_animated_history_win(Animated_history_window, actions_stack[animated_history_index])
                                                    pygame.display.update()
                                                    pygame.time.delay(500)  # delay for 500 milliseconds
                                                    animated_history_index += 1
                                            break
                        break

                    if button.name == "FillBucket":
                        STATE = "FILL"
                        break

                    if button.name == "Change":
                        Change = not Change
                        for i in range(10):
                            if i == 0:
                                buttons.append(Button(HEIGHT - 2 * button_width, (i * button_height) + 5, button_width,
                                                      button_height, WHITE, name="Change"))
                            else:
                                if Change == False:
                                    buttons.append(
                                        Button(HEIGHT - 2 * button_width, (i * button_height) + 5, button_width,
                                               button_height, WHITE, "B" + str(i - 1), BLACK))
                                if Change == True:
                                    buttons.append(
                                        Button(HEIGHT - 2 * button_width, (i * button_height) + 5, button_width,
                                               button_height, WHITE, "C" + str(i - 1), BLACK))
                        break

                    if button.name == "Brush":
                        STATE = "COLOR"
                        break

                    drawing_color = button.color
                    draw_button.color = drawing_color

                    break

                for button in brush_widths:
                    if not button.clicked(pos):
                        continue
                    # set brush width
                    if button.width == size_small:
                        BRUSH_SIZE = 1
                    elif button.width == size_medium:
                        BRUSH_SIZE = 2
                    elif button.width == size_large:
                        BRUSH_SIZE = 3

                    STATE = "COLOR"

    draw(WIN, grid, buttons)

pygame.quit()
