"""
Serial Communication Handler
Manages UART communication with PIC18F4550 microcontroller.
Protocol: 9600 baud, 8N1
"""

import serial
import serial.tools.list_ports
import struct
import threading
import time
from enum import Enum


class CommandType(Enum):
    """Command types for PIC communication."""
    UPDATE_SCORE = 0x01
    UPDATE_TIMER = 0x02
    START_MATCH = 0x03
    STOP_MATCH = 0x04
    RESET_MATCH = 0x05
    PING = 0x06
    SET_LED = 0x07


class AllianceColor(Enum):
    """Alliance identifiers."""
    RED = 0x01
    BLUE = 0x02


class SerialHandler:
    """
    Handles serial communication with PIC18F4550.
    
    Protocol Format:
    [START_BYTE][CMD][DATA_LEN][DATA...][CHECKSUM][END_BYTE]
    
    START_BYTE: 0xAA
    END_BYTE: 0x55
    CHECKSUM: XOR of all bytes
    """
    
    START_BYTE = 0xAA
    END_BYTE = 0x55
    
    def __init__(self, port=None, baudrate=9600, timeout=1):
        """
        Initialize serial handler.
        
        Args:
            port (str): Serial port (e.g., 'COM3' or '/dev/ttyUSB0')
            baudrate (int): Communication speed (default: 9600)
            timeout (float): Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        self.connected = False
        self.lock = threading.Lock()
        
        # Statistics
        self.packets_sent = 0
        self.packets_received = 0
        self.errors = 0
    
    def connect(self):
        """
        Establish serial connection.
        
        Returns:
            bool: True if connection successful
        """
        try:
            # Auto-detect port if not specified
            if self.port is None:
                self.port = self._auto_detect_port()
                if self.port is None:
                    print("Error: No serial ports found")
                    return False
            
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            
            time.sleep(2)  # Wait for PIC to initialize
            
            # Test connection with ping
            if self._ping():
                self.connected = True
                print(f"Connected to PIC on {self.port}")
                return True
            else:
                print("Device found but no response from PIC")
                return False
                
        except serial.SerialException as e:
            print(f"Serial connection error: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.connected = False
            print("Disconnected from PIC")
    
    def send_scores(self, red_score, blue_score):
        """
        Send alliance scores to PIC.
        
        Args:
            red_score (int): Red alliance score (0-99)
            blue_score (int): Blue alliance score (0-99)
            
        Returns:
            bool: True if sent successfully
        """
        if not self.connected:
            return False
        
        red_score = max(0, min(99, red_score))
        blue_score = max(0, min(99, blue_score))
        
        data = bytes([red_score, blue_score])
        return self._send_packet(CommandType.UPDATE_SCORE, data)
    
    def send_timer(self, minutes, seconds):
        """
        Send timer value to PIC.
        
        Args:
            minutes (int): Minutes remaining (0-99)
            seconds (int): Seconds remaining (0-59)
            
        Returns:
            bool: True if sent successfully
        """
        if not self.connected:
            return False
        
        minutes = max(0, min(99, minutes))
        seconds = max(0, min(59, seconds))
        
        data = bytes([minutes, seconds])
        return self._send_packet(CommandType.UPDATE_TIMER, data)
    
    def start_match(self):
        """Signal PIC to start match (turn on LEDs, buzzer, etc.)."""
        return self._send_packet(CommandType.START_MATCH, bytes())
    
    def stop_match(self):
        """Signal PIC to stop match."""
        return self._send_packet(CommandType.STOP_MATCH, bytes())
    
    def reset_match(self):
        """Reset PIC displays and counters."""
        return self._send_packet(CommandType.RESET_MATCH, bytes())
    
    def set_led(self, alliance, state):
        """
        Control alliance LED indicator.
        
        Args:
            alliance (AllianceColor): RED or BLUE
            state (bool): True = ON, False = OFF
        """
        data = bytes([alliance.value, 1 if state else 0])
        return self._send_packet(CommandType.SET_LED, data)
    
    def _send_packet(self, command, data):
        """
        Send data packet to PIC.
        
        Args:
            command (CommandType): Command to send
            data (bytes): Data payload
            
        Returns:
            bool: True if sent successfully
        """
        with self.lock:
            try:
                # Build packet
                packet = bytearray()
                packet.append(self.START_BYTE)
                packet.append(command.value)
                packet.append(len(data))
                packet.extend(data)
                
                # Calculate checksum (XOR of all bytes except START/END)
                checksum = 0
                for byte in packet[1:]:
                    checksum ^= byte
                packet.append(checksum)
                packet.append(self.END_BYTE)
                
                # Send
                self.serial_conn.write(packet)
                self.serial_conn.flush()
                self.packets_sent += 1
                
                return True
                
            except serial.SerialException as e:
                print(f"Error sending packet: {e}")
                self.errors += 1
                return False
    
    def _ping(self):
        """
        Test connection with ping command.
        
        Returns:
            bool: True if PIC responds
        """
        return self._send_packet(CommandType.PING, bytes())
    
    @staticmethod
    def _auto_detect_port():
        """
        Auto-detect PIC serial port.
        
        Returns:
            str: Port name or None if not found
        """
        ports = serial.tools.list_ports.comports()
        
        # Look for common PIC programmer/adapter identifiers
        pic_keywords = ['usb', 'serial', 'uart', 'ch340', 'cp210', 'ftdi']
        
        for port in ports:
            port_lower = port.description.lower()
            if any(keyword in port_lower for keyword in pic_keywords):
                print(f"Found potential PIC device: {port.device} - {port.description}")
                return port.device
        
        # If no match, return first available port
        if ports:
            print(f"Using first available port: {ports[0].device}")
            return ports[0].device
        
        return None
    
    def get_statistics(self):
        """
        Get communication statistics.
        
        Returns:
            dict: Statistics (packets sent, received, errors)
        """
        return {
            'packets_sent': self.packets_sent,
            'packets_received': self.packets_received,
            'errors': self.errors,
            'connected': self.connected
        }
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


# Simulation mode for testing without hardware
class MockSerialHandler(SerialHandler):
    """Mock serial handler for testing without hardware."""
    
    def __init__(self):
        super().__init__()
        self.connected = True
        self.last_scores = (0, 0)
        self.last_timer = (0, 0)
    
    def connect(self):
        print("[MOCK] Connected to virtual PIC")
        self.connected = True
        return True
    
    def disconnect(self):
        print("[MOCK] Disconnected from virtual PIC")
        self.connected = False
    
    def send_scores(self, red_score, blue_score):
        self.last_scores = (red_score, blue_score)
        print(f"[MOCK] Scores sent - Red: {red_score}, Blue: {blue_score}")
        self.packets_sent += 1
        return True
    
    def send_timer(self, minutes, seconds):
        self.last_timer = (minutes, seconds)
        print(f"[MOCK] Timer sent - {minutes:02d}:{seconds:02d}")
        self.packets_sent += 1
        return True
    
    def start_match(self):
        print("[MOCK] Match started")
        return True
    
    def stop_match(self):
        print("[MOCK] Match stopped")
        return True
    
    def reset_match(self):
        print("[MOCK] Match reset")
        return True


if __name__ == "__main__":
    # Test serial communication
    print("Testing Serial Handler...")
    
    # Test with mock
    print("\n=== Mock Mode ===")
    with MockSerialHandler() as handler:
        handler.send_scores(10, 15)
        handler.send_timer(2, 30)
        handler.start_match()
        print(f"Statistics: {handler.get_statistics()}")
    
    # Test real connection (will fail without hardware)
    print("\n=== Real Mode ===")
    handler = SerialHandler()
    if handler.connect():
        handler.send_scores(5, 8)
        handler.send_timer(1, 45)
        handler.disconnect()
    else:
        print("No hardware connected - use MockSerialHandler for testing")