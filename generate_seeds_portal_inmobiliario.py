
seeders =[]



#for i in range(0,41):
#    print(f"https://www.portalinmobiliario.com/venta/departamento/santiago-metropolitana/_Desde_{50*i + 1}_NoIndex_True_item*location_lat:-33.40223382604044*-33.27086510493097,lon:-70.84773929113038*-70.58166415685304")

ultimo_valor = 0  # Inicializar el último valor para el cálculo del índice

for i in range(0, 42):  # Se asume que el rango ya es adecuado para tu necesidad
    if i == 0:
        # Para i == 0, el valor ya es 0, no se necesita hacer nada extra
        pass
    elif i == 1:
        # En la primera iteración efectiva, incrementar en 49
        ultimo_valor += 49
    else:
        # Para todas las siguientes iteraciones, incrementar en 48
        ultimo_valor += 48
    # Imprimir la URL usando el último valor calculado para _Desde_
    print(f"https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/santiago-metropolitana/_Desde_{ultimo_valor}_NoIndex_True")
