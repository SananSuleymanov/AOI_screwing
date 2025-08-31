import random
import string

def generate_random_filename(input, length=8):
    # Define the characters that can be used in the random filename
    characters = string.ascii_letters + string.digits
    
    # Generate a random filename
    random_filename = str(input) + ''.join(random.choice(characters) for _ in range(length))
    
    return random_filename

