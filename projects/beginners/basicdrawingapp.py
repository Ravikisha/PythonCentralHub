# Basic Drawing App (Pygame)

import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)

class DrawingApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Basic Drawing App")
        self.clock = pygame.time.Clock()
        
        # Drawing state
        self.drawing = False
        self.brush_size = 5
        self.current_color = BLACK
        self.last_pos = None
        
        # Color palette
        self.colors = [BLACK, RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE, PINK]
        self.color_rects = []
        
        # Create color palette rectangles
        for i, color in enumerate(self.colors):
            rect = pygame.Rect(10 + i * 40, 10, 30, 30)
            self.color_rects.append((rect, color))
        
        # Control buttons
        self.clear_button = pygame.Rect(10, 50, 80, 30)
        self.save_button = pygame.Rect(100, 50, 80, 30)
        
        # Brush size controls
        self.brush_up_button = pygame.Rect(200, 50, 30, 15)
        self.brush_down_button = pygame.Rect(200, 65, 30, 15)
        
        # Clear the screen
        self.screen.fill(WHITE)
        self.draw_ui()
    
    def draw_ui(self):
        """Draw the user interface elements"""
        # Draw color palette
        for rect, color in self.color_rects:
            pygame.draw.rect(self.screen, color, rect)
            if color == self.current_color:
                pygame.draw.rect(self.screen, WHITE, rect, 3)
        
        # Draw control buttons
        font = pygame.font.Font(None, 24)
        
        # Clear button
        pygame.draw.rect(self.screen, (200, 200, 200), self.clear_button)
        clear_text = font.render("Clear", True, BLACK)
        text_rect = clear_text.get_rect(center=self.clear_button.center)
        self.screen.blit(clear_text, text_rect)
        
        # Save button
        pygame.draw.rect(self.screen, (200, 200, 200), self.save_button)
        save_text = font.render("Save", True, BLACK)
        text_rect = save_text.get_rect(center=self.save_button.center)
        self.screen.blit(save_text, text_rect)
        
        # Brush size controls
        pygame.draw.rect(self.screen, (200, 200, 200), self.brush_up_button)
        pygame.draw.rect(self.screen, (200, 200, 200), self.brush_down_button)
        
        up_text = font.render("+", True, BLACK)
        down_text = font.render("-", True, BLACK)
        
        self.screen.blit(up_text, (210, 50))
        self.screen.blit(down_text, (210, 65))
        
        # Brush size indicator
        size_text = font.render(f"Size: {self.brush_size}", True, BLACK)
        self.screen.blit(size_text, (240, 55))
        
        # Current color indicator
        color_indicator = pygame.Rect(350, 50, 30, 30)
        pygame.draw.rect(self.screen, self.current_color, color_indicator)
        pygame.draw.rect(self.screen, BLACK, color_indicator, 2)
        
        color_text = font.render("Current Color", True, BLACK)
        self.screen.blit(color_text, (390, 55))
    
    def handle_mouse_click(self, pos):
        """Handle mouse click events"""
        # Check color palette
        for rect, color in self.color_rects:
            if rect.collidepoint(pos):
                self.current_color = color
                return
        
        # Check clear button
        if self.clear_button.collidepoint(pos):
            self.clear_canvas()
            return
        
        # Check save button
        if self.save_button.collidepoint(pos):
            self.save_drawing()
            return
        
        # Check brush size buttons
        if self.brush_up_button.collidepoint(pos):
            self.brush_size = min(self.brush_size + 1, 20)
            return
        
        if self.brush_down_button.collidepoint(pos):
            self.brush_size = max(self.brush_size - 1, 1)
            return
    
    def draw_line(self, start_pos, end_pos):
        """Draw a line between two points"""
        if start_pos and end_pos:
            pygame.draw.line(self.screen, self.current_color, start_pos, end_pos, self.brush_size)
    
    def draw_circle(self, pos):
        """Draw a circle at the given position"""
        pygame.draw.circle(self.screen, self.current_color, pos, self.brush_size // 2)
    
    def clear_canvas(self):
        """Clear the drawing canvas"""
        self.screen.fill(WHITE)
        self.draw_ui()
    
    def save_drawing(self):
        """Save the current drawing"""
        try:
            # Create a surface without the UI elements
            drawing_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - 100))
            drawing_surface.fill(WHITE)
            
            # Copy the drawing area (below UI)
            drawing_area = pygame.Rect(0, 100, SCREEN_WIDTH, SCREEN_HEIGHT - 100)
            drawing_surface.blit(self.screen, (0, 0), drawing_area)
            
            # Save the image
            pygame.image.save(drawing_surface, "drawing.png")
            print("Drawing saved as 'drawing.png'")
        except Exception as e:
            print(f"Error saving drawing: {e}")
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        pos = pygame.mouse.get_pos()
                        
                        # Check if clicking on UI elements
                        if pos[1] < 90:  # UI area
                            self.handle_mouse_click(pos)
                        else:  # Drawing area
                            self.drawing = True
                            self.last_pos = pos
                            self.draw_circle(pos)
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left mouse button
                        self.drawing = False
                        self.last_pos = None
                
                elif event.type == pygame.MOUSEMOTION:
                    if self.drawing:
                        pos = pygame.mouse.get_pos()
                        if pos[1] >= 90:  # Only draw in drawing area
                            if self.last_pos:
                                self.draw_line(self.last_pos, pos)
                            self.draw_circle(pos)
                            self.last_pos = pos
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:  # Clear with 'C' key
                        self.clear_canvas()
                    elif event.key == pygame.K_s:  # Save with 'S' key
                        self.save_drawing()
                    elif event.key == pygame.K_EQUALS:  # Increase brush size with '+'
                        self.brush_size = min(self.brush_size + 1, 20)
                    elif event.key == pygame.K_MINUS:  # Decrease brush size with '-'
                        self.brush_size = max(self.brush_size - 1, 1)
            
            # Redraw UI (in case it was drawn over)
            ui_area = pygame.Rect(0, 0, SCREEN_WIDTH, 90)
            pygame.draw.rect(self.screen, WHITE, ui_area)
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

def main():
    """Main function to run the drawing app"""
    print("Basic Drawing App")
    print("=" * 30)
    print("Controls:")
    print("- Left click and drag to draw")
    print("- Click color palette to change colors")
    print("- Use +/- buttons or keys to change brush size")
    print("- Click 'Clear' or press 'C' to clear canvas")
    print("- Click 'Save' or press 'S' to save drawing")
    print("- Close window to exit")
    print()
    
    app = DrawingApp()
    app.run()

if __name__ == "__main__":
    main()
