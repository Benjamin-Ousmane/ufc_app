
def convert_to_meters(height):
    if height=="":
        return 0
    feet, inches = height.split("'")
    inches= inches[:-1]
    total_inches = int(feet) * 12 + int(inches)
    return round(total_inches * 0.0254,2)

def inches_to_meters(height_inches):
    if height_inches=="":
        return 0
    # Convertir la hauteur en inches en float
    height_inches = float(height_inches.strip(' "'))
    # Calculer la hauteur en mètres
    height_meters = height_inches * 0.0254
    # Arrondir la hauteur à deux décimales
    height_meters = round(height_meters, 2)
    return height_meters

def lbs_to_kg(weight):
    weight_in_lbs = int(weight.split()[0])
    weight_in_kg = weight_in_lbs * 0.45359237
    return round(weight_in_kg, 2)

def percentage_to_float(string):
    if string=="":
        return 0
    return float(string.strip('%')) / 100