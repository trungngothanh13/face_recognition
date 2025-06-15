# src/processing/integrated_system.py
import cv2
import time
import numpy as np
from datetime import datetime
from .face_enrollment import EnhancedFaceProcessor


class IntegratedVideoProcessor:
    """
    Integrated video processor with motion detection and face recognition
    """
    def __init__(self, video_stream, motion_detector, face_database, known_encodings, known_names):
        self.video_stream = video_stream
        self.motion_detector = motion_detector
        self.face_processor = EnhancedFaceProcessor()
        self.face_database = face_database
        self.known_encodings = known_encodings
        self.known_names = known_names
        
        # Settings
        self.motion_cooldown = 3.0  # Seconds to continue face detection after motion stops
        self.recognition_threshold = 0.6
        self.last_motion_time = 0
        self.face_detection_active = False
        
        # Statistics
        self.stats = {
            'frames_processed': 0,
            'motion_detected': 0,
            'faces_detected': 0,
            'faces_recognized': 0,
            'recognition_events': 0
        }
    
    def process_frame(self, frame):
        """Process a single frame"""
        self.stats['frames_processed'] += 1
        current_time = time.time()
        
        # Motion detection
        motion_detected, motion_frame = self.motion_detector.detect(frame)
        
        if motion_detected:
            self.stats['motion_detected'] += 1
            self.last_motion_time = current_time
            self.face_detection_active = True
        elif current_time - self.last_motion_time > self.motion_cooldown:
            self.face_detection_active = False
        
        # Face detection and recognition
        if self.face_detection_active and self.known_encodings:
            processed_frame, recognition_results = self.face_processor.recognize_faces(
                frame, self.known_encodings, self.known_names, self.recognition_threshold
            )
            
            # Update statistics and record events
            for name, confidence, location in recognition_results:
                self.stats['faces_detected'] += 1
                if name != "Unknown":
                    self.stats['faces_recognized'] += 1
                    if confidence > self.recognition_threshold:
                        # Record to database
                        self.face_database.record_recognition_event(
                            name=name,
                            confidence=confidence,
                            location=location
                        )
                        self.stats['recognition_events'] += 1
            
            output_frame = processed_frame
        else:
            output_frame = motion_frame
        
        # Add status overlay
        self._add_status_overlay(output_frame, motion_detected, current_time)
        
        return output_frame
    
    def _add_status_overlay(self, frame, motion_detected, current_time):
        """Add status information to frame"""
        # Status text
        if self.face_detection_active:
            status = "ACTIVE: Motion + Face Recognition"
            color = (0, 255, 0) if motion_detected else (0, 255, 255)
        else:
            status = "STANDBY: Motion Detection Only"
            color = (128, 128, 128)
        
        # Add status text
        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Add statistics
        stats_text = [
            f"Frames: {self.stats['frames_processed']}",
            f"Motion: {self.stats['motion_detected']}",
            f"Faces: {self.stats['faces_detected']}",
            f"Recognized: {self.stats['faces_recognized']}",
            f"Events: {self.stats['recognition_events']}"
        ]
        
        for i, text in enumerate(stats_text):
            cv2.putText(frame, text, (10, 60 + i * 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    def get_stats(self):
        """Get current statistics"""
        return self.stats.copy()


class IntegratedSystem:
    """Complete integrated system wrapper"""
    
    def __init__(self):
        self.processor = None
        self.components = {}
        self.running = False
    
    def initialize(self):
        """Initialize all system components"""
        from ..data.video_stream import VideoStream
        from ..processing.motion_detector import MotionDetector
        from ..data.face_database import FaceDatabase
        from ..utils.config_loader import load_config
        
        print("🔧 Initializing system components...")
        
        # Load configuration
        config = load_config()
        
        # Video stream
        self.components['stream'] = VideoStream(config['video']['source']).start()
        stream = self.components['stream']
        print(f"   ✅ Video stream: {stream.width}x{stream.height} @ {stream.fps}fps")
        
        # Motion detector
        self.components['motion_detector'] = MotionDetector(
            threshold=config['motion_detection']['threshold'],
            min_area=config['motion_detection']['min_area']
        )
        print(f"   ✅ Motion detector initialized")
        
        # Face database and known faces
        self.components['face_db'] = FaceDatabase()
        face_db = self.components['face_db']
        
        all_faces = face_db.get_all_faces()
        known_names = [face[0] for face in all_faces]
        known_encodings = [face[1] for face in all_faces]
        
        print(f"   ✅ Face database: {len(all_faces)} face samples loaded")
        
        # Integrated processor
        self.processor = IntegratedVideoProcessor(
            video_stream=self.components['stream'],
            motion_detector=self.components['motion_detector'],
            face_database=face_db,
            known_encodings=known_encodings,
            known_names=known_names
        )
        print(f"   ✅ Integrated processor ready")
        print(f"\n🚀 System initialized with {len(known_encodings)} known faces!")
        
        return True
    
    def run(self, duration=None):
        """
        Run the integrated system
        
        Args:
            duration: Run for specific duration in seconds (None = indefinite)
        """
        if not self.processor:
            print("❌ System not initialized. Call initialize() first.")
            return
        
        print("🎬 Starting integrated system...")
        print("📋 Instructions:")
        print("   - Move to trigger motion detection")
        print("   - Face recognition activates when motion detected")
        print("   - Press 'q' to quit, 's' for stats")
        print("\n⏰ Starting in 3 seconds...")
        time.sleep(3)
        
        self.running = True
        start_time = time.time()
        
        try:
            while self.running:
                # Check duration limit
                if duration and (time.time() - start_time) > duration:
                    print(f"\n⏰ Duration limit ({duration}s) reached")
                    break
                
                # Read frame
                ret, frame = self.components['stream'].read()
                if not ret:
                    print("❌ Failed to read frame")
                    break
                
                # Process frame
                processed_frame = self.processor.process_frame(frame)
                
                # Display result
                cv2.imshow("Integrated Face Recognition System", processed_frame)
                
                # Check for user input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):  # Show stats
                    self._print_stats(time.time() - start_time)
                    
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
            
        finally:
            self.running = False
            cv2.destroyAllWindows()
            
            # Final statistics
            runtime = time.time() - start_time
            print(f"\n🏁 Session Complete ({runtime:.1f}s)")
            self._print_stats(runtime)
    
    def stop(self):
        """Stop the system"""
        self.running = False
    
    def cleanup(self):
        """Clean up all resources"""
        if 'stream' in self.components:
            self.components['stream'].stop()
        if 'face_db' in self.components:
            self.components['face_db'].close()
        cv2.destroyAllWindows()
        print("✅ System cleanup complete")
    
    def _print_stats(self, runtime):
        """Print current statistics"""
        if not self.processor:
            return
        
        stats = self.processor.get_stats()
        print(f"\n📊 Statistics ({runtime:.1f}s):")
        for stat, value in stats.items():
            print(f"   - {stat}: {value}")
    
    def get_recent_events(self, limit=10):
        """Get recent recognition events"""
        if 'face_db' in self.components:
            return self.components['face_db'].get_recent_events(limit)
        return []


# Convenience functions for notebook use
def quick_integrated_system(duration=30):
    """
    Quick function to run integrated system
    
    Args:
        duration: How long to run in seconds
    """
    system = IntegratedSystem()
    
    try:
        # Initialize
        system.initialize()
        
        # Run
        system.run(duration=duration)
        
        # Show recent events
        recent_events = system.get_recent_events(limit=10)
        print(f"\n📊 Recognition events: {len(recent_events)}")
        
        for i, event in enumerate(recent_events[:5], 1):
            timestamp = event['timestamp'].strftime('%H:%M:%S')
            print(f"   {i}. {event['name']} (confidence: {event['confidence']:.2f}) at {timestamp}")
        
        return system.processor.get_stats() if system.processor else {}
        
    finally:
        system.cleanup()


def quick_system_status():
    """Quick function to check system status"""
    from ..data.face_database import FaceDatabase
    
    face_db = FaceDatabase()
    try:
        face_count = face_db.faces_collection.count_documents({})
        event_count = face_db.events_collection.count_documents({})
        
        print(f"📊 System Status:")
        print(f"   - Face samples: {face_count}")
        print(f"   - Recognition events: {event_count}")
        
        if face_count > 0:
            from collections import Counter
            all_faces = face_db.get_all_faces()
            names = [face[0] for face in all_faces]
            name_counts = Counter(names)
            print(f"👥 Enrolled people:")
            for name, count in name_counts.items():
                print(f"   - {name}: {count} samples")
        else:
            print("⚠️ No faces enrolled")
        
        return {"faces": face_count, "events": event_count}
        
    finally:
        face_db.close()