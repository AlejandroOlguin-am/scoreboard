# src/core/tracker.py

import math

class ObjectTracker:
    """Clase que asigna un ID a cada objeto detectado y rastrea su posición."""
    
    def __init__(self):
        # Almacena las posiciones centrales de los objetos: {id: (cx, cy)}
        self.center_points = {}
        # Contador global para asignar IDs únicos
        self.id_count = 1

    def rastreo(self, bounding_boxes: list) -> list:
        """
        Rastrea objetos basándose en la distancia a los centros previamente conocidos.

        Args:
            bounding_boxes: Lista de bounding boxes detectados [[x, y, w, h], ...].

        Returns:
            Lista de objetos con su ID asignado [[x, y, w, h, id], ...].
        """
        
        objects_with_id = []

        for rect in bounding_boxes:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2

            object_detected = False
            
            # 1. Buscar si el objeto ya existe (cerca de un centro conocido)
            for obj_id, pt in self.center_points.items():
                # Calcula la distancia euclidiana entre el centro actual y el centro conocido
                dist = math.hypot(cx - pt[0], cy - pt[1])

                if dist < 300: # Umbral de distancia para considerarlo el mismo objeto
                    self.center_points[obj_id] = (cx, cy) # Actualiza la posición
                    objects_with_id.append([x, y, w, h, obj_id])
                    object_detected = True
                    break

            # 2. Si es un objeto nuevo, le asignamos un nuevo ID
            if not object_detected:
                self.center_points[self.id_count] = (cx, cy)
                objects_with_id.append([x, y, w, h, self.id_count])
                self.id_count += 1 

        # 3. Limpiar los puntos centrales: Eliminar IDs que ya no están visibles
        new_center_points = {}
        for obj_bb_id in objects_with_id:
            _, _, _, _, object_id = obj_bb_id
            center = self.center_points[object_id]
            new_center_points[object_id] = center
            
        self.center_points = new_center_points
        return objects_with_id
        
    def get_current_count(self) -> int:
        """Devuelve el número total de IDs únicos asignados hasta ahora."""
        return self.id_count - 1 # El contador se incrementa después de asignar el último ID