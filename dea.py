class DEA:
    """Data Encryption Accelerator implementation in Python."""
    
    def __init__(self):
        """Initialize the DEA with empty keys."""
        self.keys = [0, 0, 0, 0]  # Storage for up to 4 keys
        self.key_counter = 0      # Current key index
        self.num_keys = 0         # Number of keys stored
        self.initialized = True   # Initialization flag
    
    def reset(self):
        """Reset the DEA state (key counter)."""
        self.key_counter = 0
    
    def set_key(self, key):
        """Set an encryption key (8-bit value)."""
        if self.num_keys < 4:
            self.keys[self.num_keys] = key & 0xFF  # Ensure 8-bit
            self.num_keys += 1
        else:
            # If we already have 4 keys, start overwriting from the beginning
            self.keys[0] = key & 0xFF
            self.num_keys = 1
    
    def encrypt_byte(self, data_in):
        """Encrypt a single byte using the current key and advance to next key."""
        if self.num_keys == 0:
            return data_in  # No encryption if no keys are set
        
        # Get the current active key
        active_key = self.keys[self.key_counter]
        
        # XOR encryption
        result = data_in ^ active_key
        
        # Advance to the next key
        self.key_counter = (self.key_counter + 1) % self.num_keys
        
        return result
    
    def encrypt_block(self, data):
        """Encrypt a block of data (bytes or bytearray)."""
        result = bytearray(len(data))
        for i in range(len(data)):
            result[i] = self.encrypt_byte(data[i])
        return result
    
    def decrypt_block(self, data):
        """Decrypt a block of data (for XOR, this is the same as encrypt)."""
        # Save the current key counter
        saved_counter = self.key_counter
        
        # Reset key counter to ensure we start with the same key sequence
        self.key_counter = 0
        
        # For XOR encryption, encryption and decryption are the same operation
        result = self.encrypt_block(data)
        
        # We could restore the counter here if needed
        # self.key_counter = saved_counter
        
        return result