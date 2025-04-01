# Import the Game class from the 'game' module
from game import Game

# Main function to start the game
def main():
    # Create an instance of the Game class
    game = Game()
    
    # Start the game by calling the run() method of the Game class
    game.run()

# Ensure the script runs the main function if it's the entry point of the program
if __name__ == "__main__":
    main()  # Call the main function to begin the game
