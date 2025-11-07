import time
import config

class ScoreManager:
    """
    Manages scores for both alliances.
    
    Tracks points from ball detection and provides scoring logic.
    """
    
    def __init__(self):
        """Initialize score manager."""
        self.red_score = 0
        self.blue_score = 0
        self.red_balls = []  # List of (ball_id, color, points)
        self.blue_balls = []
        self.last_red_id = 0
        self.last_blue_id = 0
    
    def update_from_tracking(self, red_max_id, blue_max_id=0):
        """
        Update scores based on tracker max IDs.
        
        Args:
            red_max_id (int): Highest ID for red alliance
            blue_max_id (int): Highest ID for blue alliance
        """
        # Calculate new balls detected
        new_red_balls = red_max_id - self.last_red_id
        new_blue_balls = blue_max_id - self.last_blue_id
        
        if new_red_balls > 0:
            # For now, assume all balls are green (2 points)
            # In full implementation, track ball colors
            self.add_red_score(new_red_balls * config.POINTS_GREEN_BALL)
            self.last_red_id = red_max_id
        
        if new_blue_balls > 0:
            self.add_blue_score(new_blue_balls * config.POINTS_GREEN_BALL)
            self.last_blue_id = blue_max_id
    
    def add_red_score(self, points):
        """
        Add points to red alliance.
        
        Args:
            points (int): Points to add
        """
        self.red_score += points
    
    def add_blue_score(self, points):
        """
        Add points to blue alliance.
        
        Args:
            points (int): Points to add
        """
        self.blue_score += points
    
    def add_ball(self, alliance, ball_color, ball_id):
        """
        Record a ball score event.
        
        Args:
            alliance (str): 'RED' or 'BLUE'
            ball_color (str): Color of the ball
            ball_id (int): Tracking ID of the ball
        """
        # Determine points based on ball color
        if ball_color == 'black':
            points = config.POINTS_BLACK_BALL
        else:
            points = config.POINTS_GREEN_BALL
        
        # Record ball and update score
        if alliance.upper() == 'RED':
            self.red_balls.append((ball_id, ball_color, points))
            self.add_red_score(points)
        elif alliance.upper() == 'BLUE':
            self.blue_balls.append((ball_id, ball_color, points))
            self.add_blue_score(points)
    
    def get_red_score(self):
        """Get current red alliance score."""
        return self.red_score
    
    def get_blue_score(self):
        """Get current blue alliance score."""
        return self.blue_score
    
    def get_score_difference(self):
        """
        Get score difference (red - blue).
        
        Returns:
            int: Score difference
        """
        return self.red_score - self.blue_score
    
    def get_leader(self):
        """
        Get current leading alliance.
        
        Returns:
            str: 'RED', 'BLUE', or 'TIE'
        """
        diff = self.get_score_difference()
        if diff > 0:
            return 'RED'
        elif diff < 0:
            return 'BLUE'
        else:
            return 'TIE'
    
    def get_ball_counts(self):
        """
        Get number of balls scored by each alliance.
        
        Returns:
            tuple: (red_count, blue_count)
        """
        return len(self.red_balls), len(self.blue_balls)
    
    def get_match_summary(self):
        """
        Get detailed match summary.
        
        Returns:
            dict: Match statistics
        """
        return {
            'red_score': self.red_score,
            'blue_score': self.blue_score,
            'red_balls': len(self.red_balls),
            'blue_balls': len(self.blue_balls),
            'leader': self.get_leader(),
            'score_difference': abs(self.get_score_difference()),
            'red_ball_details': self.red_balls,
            'blue_ball_details': self.blue_balls
        }
    
    def reset(self):
        """Reset all scores to zero."""
        self.red_score = 0
        self.blue_score = 0
        self.red_balls = []
        self.blue_balls = []
        self.last_red_id = 0
        self.last_blue_id = 0
    
    def export_scores(self):
        """
        Export scores as CSV-formatted string.
        
        Returns:
            str: CSV data
        """
        lines = ["Alliance,Ball_ID,Color,Points"]
        
        for ball_id, color, points in self.red_balls:
            lines.append(f"RED,{ball_id},{color},{points}")
        
        for ball_id, color, points in self.blue_balls:
            lines.append(f"BLUE,{ball_id},{color},{points}")
        
        return "\n".join(lines)
