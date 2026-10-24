edad = 20
completados = 3

if edad >= 18:
    print("Puedes crear tu cuenta y trabajar con el repositorio.")
else:
    print("Necesitas apoyo para la configuración de la cuenta.")

print("\nRepaso de comandos importantes:")

comandos = ["git status", "git add .", "git commit -m", "git push"]

for indice, comando in enumerate(comandos, start=1):
    print(f"{indice}. {comando}")

while completados > 0:
    print("Ejercicio completado.")
    completados -= 1

