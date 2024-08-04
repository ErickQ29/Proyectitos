import string
import random

longitud =  int(input("Ingrse el tamano de la contrasena: "))

caracteres = string.ascii_letters + string.digits + string.punctuation

contrasena = "".join(random.choice(caracteres) for i in range(longitud))

print("la contrasena generada es: " + contrasena)