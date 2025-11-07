"""
Object Tracker Module
Tracks detected objects across frames and assigns unique IDs.
Based on centroid tracking algorithm.
"""

import math
from collections import OrderedDict


class ObjectTracker:
    """
    Tracks multiple objects across video frames using centroid distance.
    
    Attributes:
        max_disappeared (int): Maximum frames an object can disappear before removal
        next_id (int): Counter for assigning unique IDs
        objects (OrderedDict): Active tracked objects {id: centroid}
        disappeared (OrderedDict): Frame count since last detection {id: count}
    """
    
    def __init__(self, max_disappeared=30):
        """
        Initialize the tracker.
        
        Args:
            max_disappeared (int): Maximum frames before removing lost object
        """
        self.next_id = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.max_disappeared = max_disappeared
        self.bbox = OrderedDict()  # Store bounding boxes
    
    def register(self, centroid, bbox):
        """
        Register a new object with unique ID.
        
        Args:
            centroid (tuple): (x, y) center coordinates
            bbox (list): [x, y, w, h] bounding box
        """
        self.objects[self.next_id] = centroid
        self.disappeared[self.next_id] = 0
        self.bbox[self.next_id] = bbox
        self.next_id += 1
    
    def deregister(self, object_id):
        """
        Remove an object from tracking.
        
        Args:
            object_id (int): ID of object to remove
        """
        del self.objects[object_id]
        del self.disappeared[object_id]
        del self.bbox[object_id]
    
    def update(self, detections):
        """
        Update tracked objects with new detections.
        
        Args:
            detections (list): List of [x, y, w, h] bounding boxes
            
        Returns:
            list: Tracked objects as [x, y, w, h, id]
        """
        # No detections case
        if len(detections) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.get_objects_info()
        
        # Calculate centroids from bounding boxes
        input_centroids = []
        input_bboxes = []
        
        for det in detections:
            x, y, w, h = det
            cx = int(x + w / 2.0)
            cy = int(y + h / 2.0)
            input_centroids.append((cx, cy))
            input_bboxes.append(det)
        
        # No objects being tracked yet
        if len(self.objects) == 0:
            for i in range(len(input_centroids)):
                self.register(input_centroids[i], input_bboxes[i])
        
        # Match existing objects with new detections
        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())
            
            # Calculate distance matrix
            distances = []
            for obj_centroid in object_centroids:
                row = []
                for inp_centroid in input_centroids:
                    dist = self._euclidean_distance(obj_centroid, inp_centroid)
                    row.append(dist)
                distances.append(row)
            
            # Find minimum distance matches
            rows = list(range(len(distances)))
            cols = list(range(len(distances[0])))
            
            used_rows = set()
            used_cols = set()
            
            # Sort by distance and match
            matches = []
            for row_idx in rows:
                for col_idx in cols:
                    if row_idx not in used_rows and col_idx not in used_cols:
                        matches.append((distances[row_idx][col_idx], row_idx, col_idx))
            
            matches.sort(key=lambda x: x[0])
            
            for (dist, row_idx, col_idx) in matches:
                if row_idx in used_rows or col_idx in used_cols:
                    continue
                
                # Maximum distance threshold for matching
                if dist < 100:  # pixels
                    object_id = object_ids[row_idx]
                    self.objects[object_id] = input_centroids[col_idx]
                    self.bbox[object_id] = input_bboxes[col_idx]
                    self.disappeared[object_id] = 0
                    
                    used_rows.add(row_idx)
                    used_cols.add(col_idx)
            
            # Handle unmatched objects (disappeared)
            unused_rows = set(range(len(object_centroids))) - used_rows
            for row_idx in unused_rows:
                object_id = object_ids[row_idx]
                self.disappeared[object_id] += 1
                
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            
            # Register new objects
            unused_cols = set(range(len(input_centroids))) - used_cols
            for col_idx in unused_cols:
                self.register(input_centroids[col_idx], input_bboxes[col_idx])
        
        return self.get_objects_info()
    
    def get_objects_info(self):
        """
        Get information about all tracked objects.
        
        Returns:
            list: List of [x, y, w, h, id] for each tracked object
        """
        info = []
        for object_id, bbox in self.bbox.items():
            x, y, w, h = bbox
            info.append([x, y, w, h, object_id])
        return info
    
    def get_object_count(self):
        """Get total count of tracked objects (for scoring)."""
        return len(self.objects)
    
    def get_max_id(self):
        """Get the highest ID assigned (cumulative count)."""
        return self.next_id
    
    @staticmethod
    def _euclidean_distance(point1, point2):
        """
        Calculate Euclidean distance between two points.
        
        Args:
            point1 (tuple): (x, y) coordinates
            point2 (tuple): (x, y) coordinates
            
        Returns:
            float: Distance between points
        """
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


# Compatibility with original code
class rastreador(ObjectTracker):
    """Legacy compatibility class with original naming."""
    
    def rastreo(self, detecciones):
        """
        Track detections (Spanish API for compatibility).
        
        Args:
            detecciones (list): List of [x, y, w, h] detections
            
        Returns:
            list: List of [x, y, w, h, id] tracked objects
        """
        return self.update(detecciones)


if __name__ == "__main__":
    # Test the tracker
    tracker = ObjectTracker()
    
    # Simulate detections
    frame1_detections = [[100, 100, 50, 50], [300, 200, 50, 50]]
    frame2_detections = [[105, 102, 50, 50], [305, 205, 50, 50]]
    frame3_detections = [[110, 105, 50, 50]]  # One object disappeared
    
    print("Frame 1:")
    result = tracker.update(frame1_detections)
    print(f"Tracked objects: {result}")
    
    print("\nFrame 2:")
    result = tracker.update(frame2_detections)
    print(f"Tracked objects: {result}")
    
    print("\nFrame 3:")
    result = tracker.update(frame3_detections)
    print(f"Tracked objects: {result}")
    print(f"Max ID (total count): {tracker.get_max_id()}")