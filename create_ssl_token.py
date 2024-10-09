import base64


# Caesar Cipher Encryption
def encrypt_caesar_cipher(text, shift):
    encrypted_text = ""
    for char in text:
        if char.isalpha():  # Encrypt only alphabetic characters
            shift_base = 65 if char.isupper() else 97
            encrypted_char = chr((ord(char) - shift_base + shift) % 26 + shift_base)
            encrypted_text += encrypted_char
        else:
            encrypted_text += char  # Leave non-alphabetic characters unchanged
    return encrypted_text


# Caesar Cipher Decryption
def decrypt_caesar_cipher(text, shift):
    decrypted_text = ""
    for char in text:
        if char.isalpha():  # Decrypt only alphabetic characters
            shift_base = 65 if char.isupper() else 97
            decrypted_char = chr((ord(char) - shift_base - shift) % 26 + shift_base)
            decrypted_text += decrypted_char
        else:
            decrypted_text += char  # Leave non-alphabetic characters unchanged
    return decrypted_text


# Base64 encoding
def encrypt_with_base64(text):
    text_bytes = text.encode('utf-8')
    base64_bytes = base64.b64encode(text_bytes)
    return base64_bytes.decode('utf-8')


# Base64 decoding
def decrypt_with_base64(base64_text):
    base64_bytes = base64_text.encode('utf-8')
    text_bytes = base64.b64decode(base64_bytes)
    return text_bytes.decode('utf-8')


# Original sentence
sentence = "https://192.168.88.70:8000/get-certificate"
# sentence = "sc create 'Protonn' binPath='C:\\Windows\\System32\\Proton.exe' start=auto"
shift = 3  # Shift value for Caesar cipher

# Step 1: Caesar Cipher encryption
caesar_encrypted = encrypt_caesar_cipher(sentence, shift)

# Step 2: Base64 encoding
final_encrypted_sentence = encrypt_with_base64(caesar_encrypted)
print("Encrypted sentence:", final_encrypted_sentence)

# Decrypting the sentence
# Step 1: Base64 decoding
decoded_base64 = decrypt_with_base64(final_encrypted_sentence)

# Step 2: Caesar Cipher decryption
final_decrypted_sentence = decrypt_caesar_cipher(decoded_base64, shift)
source_file = "path_to_your_source_file\\Proton.exe"
f"C:\\Windows\\System32\\Proton.exe"
print("Decrypted sentence:", final_decrypted_sentence.format(source_file))
