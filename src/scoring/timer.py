import time
import config

class MatchTimer:
    """
    Countdown timer for competition matches.
    
    Provides precise timing with start/stop/reset functionality.
    """
    
    def __init__(self, duration=config.MATCH_DURATION):
        """
        Initialize timer.
        
        Args:
            duration (int): Match duration in seconds
        """
        self.duration = duration
        self.time_remaining = duration
        self.running = False
        self.start_time = None
        self.pause_time = None
    
    def start(self):
        """Start or resume the timer."""
        if not self.running:
            if self.pause_time is not None:
                # Resuming from pause
                pause_duration = time.time() - self.pause_time
                self.start_time += pause_duration
            else:
                # Starting fresh
                self.start_time = time.time()
            
            self.running = True
            self.pause_time = None
    
    def stop(self):
        """Pause the timer."""
        if self.running:
            self.running = False
            self.pause_time = time.time()
            self.update()
    
    def reset(self):
        """Reset timer to initial duration."""
        self.time_remaining = self.duration
        self.running = False
        self.start_time = None
        self.pause_time = None
    
    def update(self):
        """Update time remaining (call periodically)."""
        if self.running:
            elapsed = time.time() - self.start_time
            self.time_remaining = max(self.duration - elapsed, 0)
            
            if self.time_remaining == 0:
                self.running = False
    
    def get_time_remaining(self):
        """
        Get time remaining.
        
        Returns:
            float: Seconds remaining
        """
        self.update()
        return self.time_remaining
    
    def get_time_components(self):
        """
        Get time as minutes and seconds.
        
        Returns:
            tuple: (minutes, seconds)
        """
        self.update()
        minutes = int(self.time_remaining // 60)
        seconds = int(self.time_remaining % 60)
        return minutes, seconds
    
    def format_time(self):
        """
        Format time as MM:SS string.
        
        Returns:
            str: Formatted time string
        """
        minutes, seconds = self.get_time_components()
        return f"{minutes:02d}:{seconds:02d}"
    
    def is_expired(self):
        """
        Check if timer has expired.
        
        Returns:
            bool: True if time is up
        """
        self.update()
        return self.time_remaining <= 0
    
    def get_progress(self):
        """
        Get timer progress as percentage.
        
        Returns:
            float: Progress (0.0 to 1.0)
        """
        self.update()
        return 1.0 - (self.time_remaining / self.duration)