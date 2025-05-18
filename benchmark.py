import time
import os
import sys
from dea import DEA

def print_data(label, data, max_display=20, max_text=40):
    """Print data sample in hex and text format."""
    # Print hex representation
    print(f"{label} (hex): ", end="")
    display_length = min(len(data), max_display)
    for i in range(display_length):
        print(f"{data[i]:02X} ", end="")
    if len(data) > max_display:
        print("... (truncated)")
    else:
        print()
    
    # Print text representation
    print(f"{label} (text): \"", end="")
    display_length = min(len(data), max_text)
    for i in range(display_length):
        if 32 <= data[i] <= 126:  # Printable ASCII
            print(chr(data[i]), end="")
        else:
            print(".", end="")
    if len(data) > max_text:
        print("...\"")
    else:
        print("\"")

def run_basic_test():
    """Run the basic DEA test with a small message."""
    print("=== Basic DEA Test ===")
    
    # Initialize DEA
    dea = DEA()
    
    # Set 4 different keys
    print("Setting up 4 encryption keys...")
    dea.reset()
    dea.set_key(0xAA)
    dea.set_key(0xBB)
    dea.set_key(0xCC)
    dea.set_key(0xDD)
    
    # Data to encrypt
    message = b"AAAAAAAAAAAAAAAA!"
    print(f"\nOriginal message: \"{message.decode()}\"")
    print_data("Original", message)
    
    # Encrypt with timing - repeat many times for better timing
    print("\nEncrypting with key cycling (0xAA, 0xBB, 0xCC, 0xDD)...")
    dea.reset()
    
    # Do multiple iterations for small data to get measurable timing
    iterations = 100000
    start_time = time.time()
    encrypted = None
    for _ in range(iterations):
        dea.reset()
        encrypted = dea.encrypt_block(message)
    end_time = time.time()
    
    encrypt_time = (end_time - start_time) * 1000  # convert to ms
    encrypt_time_per_op = encrypt_time / iterations
    
    print_data("Encrypted", encrypted)
    print(f"Encryption time (total for {iterations} iterations): {encrypt_time:.3f} ms")
    print(f"Encryption time (per operation): {encrypt_time_per_op:.6f} ms")
    
    # Avoid division by zero
    if encrypt_time > 0:
        print(f"Encryption throughput: {(len(message) * iterations) / (encrypt_time / 1000):.2f} bytes/second")
    else:
        print("Encryption throughput: Very high (too fast to measure)")
    
    # Decrypt with timing - also repeat many times
    print("\nDecrypting...")
    dea.reset()
    
    start_time = time.time()
    decrypted = None
    for _ in range(iterations):
        dea.reset()
        decrypted = dea.decrypt_block(encrypted)
    end_time = time.time()
    
    decrypt_time = (end_time - start_time) * 1000  # convert to ms
    decrypt_time_per_op = decrypt_time / iterations
    
    print(f"Decrypted: \"{decrypted.decode()}\"")
    print_data("Decrypted", decrypted)
    print(f"Decryption time (total for {iterations} iterations): {decrypt_time:.3f} ms")
    print(f"Decryption time (per operation): {decrypt_time_per_op:.6f} ms")
    
    # Avoid division by zero
    if decrypt_time > 0:
        print(f"Decryption throughput: {(len(message) * iterations) / (decrypt_time / 1000):.2f} bytes/second")
    else:
        print("Decryption throughput: Very high (too fast to measure)")
    
    # Demonstrate individual byte encryption with key cycling
    print("\n=== Key Cycling Demonstration ===")
    dea.reset()
    
    test_data = [0x11, 0x22, 0x33, 0x44, 0x55]
    for i, data_byte in enumerate(test_data):
        result = dea.encrypt_byte(data_byte)
        # Calculate which key was used (for display purposes)
        key_idx = i % 4
        key_used = 0xAA if key_idx == 0 else 0xBB if key_idx == 1 else 0xCC if key_idx == 2 else 0xDD
        
        print(f"Input: 0x{data_byte:02X}, Key: 0x{key_used:02X}, Output: 0x{result:02X}")

def run_performance_test():
    """Run a comprehensive performance test with larger data and multiple iterations."""
    print("\n=== Performance Benchmark ===")
    
    # Test parameters
    test_size = 10 * 1024 * 1024  # 10MB
    num_iterations = 3  # Even fewer iterations in Python since it's much slower than C
    
    print(f"Test size: {test_size} bytes")
    print(f"Number of iterations: {num_iterations}")
    
    # Initialize DEA
    dea = DEA()
    
    # Set up 4 different keys
    dea.reset()
    dea.set_key(0xAA)
    dea.set_key(0xBB)
    dea.set_key(0xCC)
    dea.set_key(0xDD)
    
    # Create test data
    print("Creating test data...")
    large_data = bytearray(test_size)
    for i in range(test_size):
        large_data[i] = ord('A') + (i % 26)
    
    print_data("Original (sample)", large_data)
    
    # Warm-up run with smaller data to avoid long initial delay
    print("\nWarm-up run...")
    dea.reset()
    _ = dea.encrypt_block(large_data[:10240])  # Just encrypt the first 10KB
    
    # Start the benchmark
    print(f"\nStarting benchmark ({int(test_size / (1024 * 1024))} MB × {num_iterations} iterations)...")
    print("This may take a while in Python...")
    
    start_time = time.time()
    
    # Multiple iterations for more accurate timing
    for j in range(num_iterations):
        sys.stdout.write(f"\rIteration {j+1}/{num_iterations}...")
        sys.stdout.flush()
        dea.reset()
        encrypted = dea.encrypt_block(large_data)
    
    sys.stdout.write("\n")
    end_time = time.time()
    total_time = (end_time - start_time) * 1000  # convert to ms
    
    # Show a sample of the encrypted data
    print_data("Encrypted (sample)", encrypted)
    
    # Verify with decryption (just once, not in a loop)
    print("\nVerifying with decryption (single pass)...")
    dea.reset()
    
    decrypt_start = time.time()
    decrypted = dea.decrypt_block(encrypted)
    decrypt_end = time.time()
    decrypt_time = (decrypt_end - decrypt_start) * 1000  # convert to ms
    
    print_data("Decrypted (sample)", decrypted)
    
    # Verify correctness
    if decrypted == large_data:
        print("\nVerification SUCCESSFUL - The decrypted text matches the original!")
    else:
        print("\nVerification FAILED - The decrypted text does not match the original!")
    
    # Print performance metrics
    print(f"\n=== Performance Results ({int(test_size / (1024 * 1024))} MB Test, {num_iterations} iterations) ===")
    print(f"Total execution time: {total_time:.3f} ms")
    print(f"Average time per iteration: {total_time / num_iterations:.3f} ms")
    print(f"Total data processed: {test_size * num_iterations} bytes")
    
    # Avoid division by zero
    if total_time > 0:
        mb_per_second = ((test_size * num_iterations) / (1024 * 1024)) / (total_time / 1000)
        print(f"Throughput: {mb_per_second:.2f} MB/second")
    else:
        print("Throughput: Very high (too fast to measure)")
    
    # Additional information about decryption performance
    print("\nDecryption performance:")
    print(f"Single decryption time: {decrypt_time:.3f} ms")
    
    # Avoid division by zero
    if decrypt_time > 0:
        print(f"Decryption throughput: {(test_size / (1024 * 1024)) / (decrypt_time / 1000):.2f} MB/second")
    else:
        print("Decryption throughput: Very high (too fast to measure)")

if __name__ == "__main__":
    run_basic_test()
    run_performance_test()