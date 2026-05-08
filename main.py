"""
Main Entry Point

This file serves as the entry point for the GitaSending application,
demonstrating functionality in adherence to the project rules.
"""

import asyncio
from send_today import send_daily_gita


def example_gitasending():
    """
    Example function to showcase the GitaSending daily dispatch.
    This function delegates to the distinct functionality defined in
    send_today.py, which is optimized for cron scheduling.
    """
    print("Executing the one-shot daily GitaSending sequence...")
    asyncio.run(send_daily_gita())


def main():
    """
    The main method of the application.
    
    This acts as the entry point, calling example functions to 
    demonstrate features.
    """
    example_gitasending()


if __name__ == "__main__":
    main()
