"""
Main Entry Point

This file serves as the entry point for the GitaSending application,
demonstrating functionality in adherence to the project rules.
"""

from bot import run_bot


def example_gitasending_bot():
    """
    Example function to showcase the GitaSending functionality.
    
    This function delegates to the distinct functionality defined in
    the bot module, starting the Telegram polling loop.
    """
    print("Showcasing GitaSending Telegram Bot...")
    run_bot()


def main():
    """
    The main method of the application.
    
    This acts as the entry point, calling example functions to 
    demonstrate features.
    """
    example_gitasending_bot()


if __name__ == "__main__":
    main()
