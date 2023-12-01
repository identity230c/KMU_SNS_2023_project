def convert_to_bytes(data, byteorder):
    int_data = int.from_bytes(data.encode('utf-8'), byteorder=byteorder)
    byte_length = int_data.bit_length() // 8
    buffer = [hex((int_data >> (i * 8)) & 0xFF) for i in range(byte_length, -1, -1)]
    return buffer

if __name__ == "__main__":
    data = input()
    print(f"big endian: {convert_to_bytes(data, 'big')}")
    print(f"little endian: {convert_to_bytes(data, 'little')}")
