import pygame
import pygame.freetype


# HOW TO UTILIZE THIS
# Every element has a position and a rect
# When the element is centered, the position is in the center of the element
# The rect continues being the same usually but some differences occur when calling some methods
# The get pos method return the element position within the container, not the screen space
# The get screen pos return the absolute screen position of the element
# The get rect also gets the bounding box of the element within the container
# When the element is centered, the rect is changed slightly to be more upward and left
# The get screen rect get the absolute bounding box of the element in the screen (and again, when centered the rect is slightly to the left and upwards)
# So, don't call self.rect directly and neither self.pos directly, call their respectives methods
# When customizing the update and handle_event method, always call back their respective super methods like _update and _handle_event
# It should be the first thing being called
# Every element can be used as container, for example, buttons are containers for text

# WARNING: When you're going to draw something on the screen, you generally want to use the rect x and y position and no the self.get_pos or self.get_screen_pos
# This is because the rect adjust for the center variable


def point_rect(point, rect):
    px, py = point[0], point[1]
    rx, ry, rw, rh = rect[0], rect[1], rect[2], rect[3]

    if (px >= rx and px <= rx + rw and py >= ry and py <= ry + rh):
        return True

    return False

# Base class of all gui elements
class BaseUI:

    def __init__(self, pos, id="generic") -> None:
        self.pos     = pygame.Vector2(pos)
        self.id      = id

        # Every ui element has a rect
        self.rect = [self.pos.x, self.pos.y, 0, 0]

        # Properties
        self.center  = False # Whether the element is centered or not
        self.image   = None

        # Mouse related properties
        self.hovering = False # Mouse is hovering over the element
        self.pressing = False # Mouse is pressing over element(It should have been clicked first)
        self.clicked = False # Just clicked over it
        self._selected = False # Whether it was selected by the mouse

        # Parent container
        self.parent_container = None

    def set_container(self, container):
        self.parent_container = container

    def get_pos(self):
        return self.pos
    
    def set_pos(self, pos):
        self.pos[0] = pos[0]
        self.pos[1] = pos[1]

    # Return screen position (ignoring container)
    def get_screen_pos(self):
        # Position returned is relative to the container (If there's any)
        if self.parent_container:
            container_x, container_y = self.parent_container.get_screen_pos()

            return [self.pos[0] + container_x, self.pos[1] + container_y]

        return self.pos

    def set_rect(self, rect):
        self.rect[0] = rect[0]
        self.rect[1] = rect[1]
        self.rect[2] = rect[2]
        self.rect[3] = rect[3]

    # Return screen position (ignoring container)
    def get_screen_rect(self):
        x, y = self.get_screen_pos()
        rect = [x, y, self.rect[2], self.rect[3]]

        if self.center:
            return [rect[0] - (rect[2] / 2), rect[1] - (rect[3] / 2), rect[2], rect[3]]

        return rect
    
    def get_rect(self):
        x, y = self.get_pos()
        rect = [x, y, self.rect[2], self.rect[3]]

        if self.center:
            return [rect[0] - (rect[2] / 2), rect[1] - (rect[3] / 2), rect[2], rect[3]]

        return rect

    # Special handle event method that is used by every element
    def _handle_event(self, event):
        if not self.hovering:
            self.pressing = False

            # Unselect when clicking elsewhere
            if event.type == pygame.MOUSEBUTTONDOWN:
                # LEFT CLICK
                if event.button == 1:
                    self._selected = False
            
            return

        # Check for mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            # LEFT CLICK
            if event.button == 1:
                self.pressing = True
                self._selected = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                # If mouse was pressing and now it's up then it clicked
                if self.pressing:
                    self.clicked = True
                    self.just_clicked = True

                self.pressing = False

    def _update(self):
        self.clicked = False

        rect = self.get_screen_rect()

        # Update mouse variables
        mx, my = pygame.mouse.get_pos()

        if point_rect((mx, my), rect):
            self.hovering = True
        else:
            self.hovering = False

    def handle_event(self, event):
        self._handle_event(event)

    def update(self):
        self._update()

    def render(self, surface: pygame.Surface) -> None:
        pass

# The container holds ui elements into relative positions
# It can also update and handle every single element
class Container(BaseUI):
    
    def __init__(self, pos, size, color=(45, 45, 45, 200), id="generic") -> None:
        super().__init__(pos, id)

        self.draw_container = True # Draw the container itself
        self.color = color

        # Child UI elements
        self.elements = []

        self.set_rect((pos[0], pos[1], size[0], size[1]))

    # Add ui element to the container
    def add(self, element):
        element.set_container(self)
        self.elements.append(element)

    def update(self):
        self._update()

        for element in self.elements:
            element.update()

    def handle_event(self, event):
        clicked = []
        self._handle_event(event)
        
        for element in self.elements:
            element.handle_event(event)

            if element.clicked:
                clicked.append(element)

        return clicked

    def render(self, surface: pygame.Surface) -> None:
        rect = self.get_screen_rect()

        # Render base container area
        if self.draw_container:
            pygame.draw.rect(surface, self.color, rect)
            pygame.draw.rect(surface, (0, 0, 0, 0), rect, 1)
        
        # Render elements
        for element in self.elements:
            element.render(surface)

class Text(BaseUI):
    
    def __init__(self, pos, text="", font_size=64, font_type='Consolas', color=(255, 255, 255), center=False) -> None:
        super().__init__(pos)
        self.text = text
        self.text_surface = None # Rendered in its own method
        self.font_size = font_size
        self.ft_font = pygame.freetype.SysFont(font_type, 24) # Font
        self.color = color
        self.center = center

        self.set_text(self.text)

    def set_text(self, text):
        self.text = text
        self.text_surface, rect = self.ft_font.render(self.text, self.color)

        # Define text rectangle size
        self.rect[2] = rect[2]
        self.rect[3] = rect[3]

        # Define rect x and y
        #self.rect[0] = rect[0]
        #self.rect[1] = rect[1]

    def render(self, surface: pygame.Surface) -> None:
        rect = self.get_screen_rect()
        surface.blit(self.text_surface, rect)

class Button(BaseUI):

    def __init__(self, pos, size=None, text="", color=(75, 75, 75), font_size=64, font_type='Consolas', text_color=(255, 255, 255), center=False, id="generic") -> None:
        super().__init__(pos, id)
        self.color = color
        self.center = center
        self.text_ui = Text([0, 0], text, font_size, font_type, text_color, center=True)
        self.text_ui.set_container(self) # Set this button as the text parent

        # Color
        self.original_color = color
        self.hovering_color = (color[0] * 0.75, color[1] * 0.75, color[2] * 0.75)
        self.pressing_color = (color[0] * 0.5, color[1] * 0.5, color[2] * 0.5)

        if size is None:
            # Get text width and make it the size of the button
            self.rect[2] = self.text_ui.rect[2] + 20
            self.rect[3] = self.text_ui.rect[3] + 20
        else:
            self.rect[2] = size[0]
            self.rect[3] = size[1]

        # Fix text position to be in the center of the button
        if not center:
            rect = self.get_rect()
            self.text_ui.pos[0] = rect[2] / 2
            self.text_ui.pos[1] = rect[3] / 2

    def render(self, surface: pygame.Surface) -> None:
        rect = self.get_screen_rect()
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, (0, 0, 0), rect, 1)
        self.text_ui.render(surface)

    def update(self):
        self._update()

        # If the mouse is hovering, it gets darker
        if self.hovering:
            self.color = self.hovering_color
        else:
            self.color = self.original_color

        # If the mouse is pressing it gets even darker
        if self.pressing:
            self.color = self.pressing_color


class ScrollBar(BaseUI):
    
    def __init__(self, pos, id="generic") -> None:
        super().__init__(pos, id)

        # ScrollBar maximum possible y down value
        self.current_y_value = 0
        self.max_y_value = 100

        # Scrollbar properties
        self.bar_width = 20
        self.bar_height = 0

# List
class ItemList(BaseUI):

    def __init__(self, pos, values=[], id="generic") -> None:
        super().__init__(pos, id)
        self.values = values
        self.selected_index = 0

# A Image selector
# This type of button when clicked stay in a selected state
# You can link it to a specific group, so that when another item is selected this one gets deselected (TO IMPELMENT)
class ImageButtonActive(BaseUI):
    
    def __init__(self, pos, image, group="none", id="generic") -> None:
        super().__init__(pos, id)
        self.image = image

        # Adjust rect
        self.rect[2] = image.get_width()
        self.rect[3] = image.get_height()

    def render(self, surface: pygame.Surface) -> None:
        rect = self.get_screen_rect()
        pos = (rect[0], rect[1])
        surface.blit(self.image, pos)


# Custom GUI Element (Texture Selector)
import textures
class TextureSelector(BaseUI):

    def __init__(self, pos, size, id="generic") -> None:
        super().__init__(pos, id)
        self.color = (200, 200, 200)
        
        # Every texture contained within here
        self.texture_buttons = []
        self.button_size = textures.TEX_WIDTH # texture size within this

        # Define size
        self.rect[2] = size[0]
        self.rect[3] = size[1]

        # Selected element index within this container
        self.selected_index = -1

        # Add the select buttons
        for texture in textures.texture:
            if texture is not None:
                btn = ImageButtonActive((0, 0), texture)
                btn.set_container(self)
                self.texture_buttons.append(btn)

        self.adjust_elements()

    def get_selected_index(self):
        return self.selected_index

    def update(self):
        self._update()

        for btn in self.texture_buttons:
            btn.update()

    def handle_event(self, event):
        self._handle_event(event)

        for i, btn in enumerate(self.texture_buttons):
            btn.handle_event(event)

            if btn.clicked:
                self.selected_index = i

    # Adjust button x and y positions within this container
    def adjust_elements(self):
        rect = self.get_rect()

        # Limits
        width  = rect[2]
        height = rect[3]

        # Maximum of textures in a line
        row_amount = int(width / self.button_size)

        for index, btn in enumerate(self.texture_buttons):
            x_pos = (index % row_amount) * self.button_size
            y_pos = (int(index/row_amount) * self.button_size)
            btn.set_pos((x_pos + 1, y_pos + 1))

    def render(self, surface: pygame.Surface) -> None:
        rect = self.get_screen_rect()
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, (0, 0, 0), rect, 1)

        # Render buttons
        for button in self.texture_buttons:
            button.render(surface)

        # Draw a bluish color on top of the selected button
        selected_color = (0, 0, 100, 100)
        if self.selected_index != -1:
            btn = self.texture_buttons[self.selected_index]

            btn_rect = btn.get_screen_rect()
            pygame.draw.rect(surface, selected_color, btn_rect)

