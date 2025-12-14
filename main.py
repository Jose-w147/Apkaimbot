"""
Auto-Aim Detector para Android com Kivy
Detecta cabeças em tempo real usando YOLOv8
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.garden.xcamera import XCamera
from kivy.graphics.texture import Texture
from kivy.clock import Clock
import cv2
import numpy as np
from ultralytics import YOLO
import math
from threading import Thread


class AutoAimDetector: 
    """Sistema de mira automática usando YOLOv8"""
    
    def __init__(self, confidence_threshold=0.5):
        try:
            self.model = YOLO('yolov8n.pt')
        except:
            self.model = None
        self.confidence_threshold = confidence_threshold
        self.target_center = None
        self.crosshair_size = 30
        
    def detect_heads(self, frame):
        """Detecta cabeças no frame"""
        if self.model is None:
            return []
        
        try:
            results = self.model(frame, conf=self.confidence_threshold, verbose=False)
            detections = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    confidence = float(box.conf[0])
                    
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    area = (x2 - x1) * (y2 - y1)
                    
                    detections.append({
                        'box': (x1, y1, x2, y2),
                        'center': (center_x, center_y),
                        'confidence': confidence,
                        'area': area
                    })
            
            return detections
        except Exception as e:
            print(f"Erro na detecção: {e}")
            return []
    
    def get_closest_target(self, detections, frame_center):
        """Seleciona o alvo mais próximo"""
        if not detections: 
            return None
        
        def distance_to_center(det):
            cx, cy = det['center']
            fx, fy = frame_center
            return math.sqrt((cx - fx)**2 + (cy - fy)**2)
        
        return min(detections, key=distance_to_center)
    
    def draw_crosshair(self, frame, center, size=30, color=(0, 255, 0), thickness=2):
        """Desenha mira no frame"""
        x, y = center
        cv2.line(frame, (x - size, y), (x - size // 2, y), color, thickness)
        cv2.line(frame, (x + size // 2, y), (x + size, y), color, thickness)
        cv2.line(frame, (x, y - size), (x, y - size // 2), color, thickness)
        cv2.line(frame, (x, y + size // 2), (x, y + size), color, thickness)
        cv2.circle(frame, center, 3, color, -1)
    
    def process_frame(self, frame):
        """Processa frame com detecções"""
        height, width = frame.shape[:2]
        frame_center = (width // 2, height // 2)
        
        detections = self.detect_heads(frame)
        
        for det in detections:
            x1, y1, x2, y2 = det['box']
            cv2.rectangle(frame, (x1, y1), (x2, y2), (100, 100, 255), 2)
        
        cv2.circle(frame, frame_center, 2, (255, 255, 255), -1)
        
        target = self.get_closest_target(detections, frame_center)
        target_info = {'found': False}
        
        if target: 
            self.target_center = target['center']
            x1, y1, x2, y2 = target['box']
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            self.draw_crosshair(frame, self.target_center, size=30, color=(0, 255, 0))
            cv2.line(frame, frame_center, self.target_center, (255, 255, 0), 2)
            
            target_info = {
                'found': True,
                'center': self.target_center,
                'confidence': target['confidence']
            }
        
        cv2.putText(frame, f"Deteccoes: {len(detections)}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        if target_info['found']:
            cv2.putText(frame, f"Conf: {target_info['confidence']:.2f}", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return frame, target_info


class AutoAimApp(App):
    """Aplicação principal do Auto-Aim para Android"""
    
    def build(self):
        self.detector = AutoAimDetector()
        self.is_running = True
        
        layout = BoxLayout(orientation='vertical')
        
        # Câmera
        self.camera = XCamera(
            resolution=(640, 480),
            play=True
        )
        layout.add_widget(self.camera)
        
        # Status
        self.status_label = Label(
            text='Iniciando...',
            size_hint_y=0.1,
            color=(0, 1, 0, 1)
        )
        layout.add_widget(self.status_label)
        
        # Botão
        btn_layout = BoxLayout(size_hint_y=0.1)
        stop_btn = Button(text='Sair')
        stop_btn.bind(on_press=self.stop_app)
        btn_layout.add_widget(stop_btn)
        layout.add_widget(btn_layout)
        
        Clock.schedule_interval(self.update_camera, 1.0 / 30.0)
        
        return layout
    
    def update_camera(self, dt):
        """Atualiza a câmera"""
        if not self.is_running:
            return
        
        try:
            # Capturar frame
            texture = self.camera.texture
            if texture:
                frame = texture.pixels
                frame_array = np.frombuffer(frame, np.uint8).reshape(480, 640, 4)
                frame_bgr = cv2.cvtColor(frame_array, cv2.COLOR_RGBA2BGR)
                
                # Processar
                frame_processed, info = self.detector.process_frame(frame_bgr)
                
                # Atualizar status
                if info['found']:
                    self.status_label.text = f"Alvo detectado! Confiança: {info['confidence']:.2f}"
                else:
                    self.status_label.text = "Nenhum alvo detectado"
        
        except Exception as e: 
            self.status_label.text = f"Erro: {str(e)}"
    
    def stop_app(self, instance):
        """Encerra a aplicação"""
        self.is_running = False
        App.get_running_app().stop()


if __name__ == '__main__':
    AutoAimApp().run()