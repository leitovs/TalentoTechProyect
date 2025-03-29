import requests
import json
import numpy as np

def obtener_gti_opta(direccion):
    """
    Obtiene el valor GTI_opta desde Global Solar Atlas usando la dirección.
    Retorna GTI_opta (kWh/m²/año) o None si no se encuentra la ubicación.
    """
    # Obtener coordenadas a partir de la dirección
    url_nominatim = f"https://nominatim.openstreetmap.org/search?q={direccion}&format=json"
    headers_nominatim = {"User-Agent": "MiAplicacion/1.0"}
    response = requests.get(url_nominatim, headers=headers_nominatim)
    
    data = response.json()
    if not data:
        print("No se encontraron resultados para la dirección.")
        return None
    
    location = data[0]
    lat = location['lat']
    lon = location['lon']
    
    # Consultar Global Solar Atlas con las coordenadas
    url_gsa = f"https://api.globalsolaratlas.info/data/lta?loc={lat},{lon}"
    headers_gsa = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Origin': 'https://globalsolaratlas.info',
        'Referer': 'https://globalsolaratlas.info/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url_gsa, headers=headers_gsa)
    
    if response.status_code != 200:
        print("Error consultando el Global Solar Atlas.")
        return None
    
    data_gsa = response.json()
    # Se ajusta la generación con un factor (0.96) según ejemplo original.
    gti_opta = data_gsa['annual']['data']['GTI_opta']
    return gti_opta

def calcular_presupuesto_realista(area_disponible_m2,
                                 consumo_mensual_kWh,
                                 gti_valor,
                                 costo_kwh,  # Costo del kWh en COP
                                 tipo_panel_m2=2.0,
                                 potencia_por_panel=300,  # en watts
                                 factor_utilizacion=0.8,
                                 costo_kw_instalado=1250,
                                 costo_fijo=1000,
                                 altura_superior_4m=False,
                                 acceso_dificil=False,
                                 distancia_mayor_20m=False,
                                 instalacion_rural=False):
    """
    Calcula:
      - El número de paneles a instalar (sin exceder el área disponible y sin sobredimensionar la generación)
      - La potencia total instalada
      - Los costos asociados (aplicando factores de corrección)
      
    Se basa en el consumo medio mensual (kWh) y en el valor de GTI (kWh/m²/año).
    """
    # Convertir GTI anual a generación mensual por m² y ajustar con el factor 0.96
    generacion_mensual_por_m2 = (gti_valor / 12) * 0.96  # kWh/m²/mes
    
    # Generación mensual de cada panel
    generacion_panel_mensual = generacion_mensual_por_m2 * tipo_panel_m2
    
    # Número de paneles necesarios para cubrir el consumo (sin sobredimensionar)
    num_paneles_necesarios = int(np.ceil(consumo_mensual_kWh / generacion_panel_mensual))
    
    # Número máximo de paneles permitidos por el área disponible
    area_utilizable = area_disponible_m2 * factor_utilizacion
    num_paneles_max = int(area_utilizable // tipo_panel_m2)
    
    # Se toma el menor: no se pueden instalar más paneles que los permitidos por el área
    # ni sobredimensionar la generación (que exceda el consumo mensual)
    num_paneles = min(num_paneles_necesarios, num_paneles_max)
    
    # Potencia total instalada (en kW)
    potencia_total_kw = (num_paneles * potencia_por_panel) / 1000.0
    
    # Cálculo de costos variables con factores de corrección
    multiplier = 1.0
    if altura_superior_4m:
        multiplier *= 1.15
    if acceso_dificil:
        multiplier *= 1.20
    if distancia_mayor_20m:
        multiplier *= 1.10
    
    extra_viaticos = 700 if instalacion_rural else 0
    costo_variable = potencia_total_kw * costo_kw_instalado * multiplier
    total_cost = costo_fijo + costo_variable + extra_viaticos
    
    conversion_factor = 4527.20  # Factor de conversión a COP
    return {
        "num_paneles": num_paneles,
        "potencia_total_kw": potencia_total_kw,
        "costo_variable": costo_variable * conversion_factor,
        "total_cost": total_cost * conversion_factor,
        "detalle": {
            "costo_fijo": costo_fijo * conversion_factor,
            "extra_viaticos": extra_viaticos * conversion_factor,
            "multiplier": multiplier,
            "generacion_por_panel_mensual": generacion_panel_mensual
        }
    }

def proyecto_solar(direccion, area_disponible_m2, consumo_mensual_kWh, costo_kwh,
                   altura_superior_4m=False,
                   acceso_dificil=False,
                   distancia_mayor_20m=False,
                   instalacion_rural=False):
    """
    Integra los cálculos:
      - Obtiene la generación estimada (kWh/m²/año) y la convierte a generación mensual
      - Calcula el presupuesto realista basándose en el área disponible y el consumo medio mensual.
      - Determina el número de paneles instalables sin sobredimensionar la generación.
      - Calcula el porcentaje de cobertura del consumo.
      - Estima el ROI (retorno de inversión) en meses, usando el costo del kWh.
    
    Parámetros:
      - direccion: Ubicación de la instalación.
      - area_disponible_m2: Área máxima disponible para la instalación (m²).
      - consumo_mensual_kWh: Consumo medio mensual en kWh.
      - costo_kwh: Costo del kWh en COP.
      - Los parámetros opcionales permiten ajustar condiciones especiales.
    
    Retorna un diccionario con:
      - generacion_anual_estimada_kWh
      - presupuesto_total (en COP)
      - num_paneles
      - porcentaje_cobertura_consumo
      - roi_meses
    """
    # 1. Obtener GTI desde Global Solar Atlas
    gti = obtener_gti_opta(direccion)
    if gti is None:
        return {"error": "No se pudo obtener la generación estimada para la dirección"}

    # 2. Calcular presupuesto y número de paneles según el área disponible y consumo mensual
    presupuesto = calcular_presupuesto_realista(
        area_disponible_m2,
        consumo_mensual_kWh,
        gti,
        costo_kwh,
        altura_superior_4m=altura_superior_4m,
        acceso_dificil=acceso_dificil,
        distancia_mayor_20m=distancia_mayor_20m,
        instalacion_rural=instalacion_rural
    )
    
    num_paneles = presupuesto["num_paneles"]
    total_cost = presupuesto["total_cost"]
    
    # Calcular generación mensual total basada en los paneles instalados
    tipo_panel_m2 = 2.0  # Área de cada panel (m²)
    generacion_panel_mensual = (gti / 12) * 0.96 * tipo_panel_m2
    generacion_total_mensual = num_paneles * generacion_panel_mensual
    
    # Convertir a generación anual estimada (para informar)
    generacion_anual = generacion_total_mensual * 12
    
    # 3. Calcular el porcentaje de cobertura del consumo:
    # Se garantiza que la generación mensual no exceda el consumo mensual.
    porcentaje = (generacion_total_mensual / consumo_mensual_kWh) * 100
    if porcentaje > 100:
        porcentaje = 100.0

    # 4. Estimar el ROI (retorno de inversión) en meses:
    # El ahorro anual se basa en el costo del kWh y el consumo mensual que se compensa.
    # Se asume que la energía compensada es la menor entre la generación y el consumo.
    energia_compensada_mensual = min(generacion_total_mensual, consumo_mensual_kWh)
    ahorro_anual = energia_compensada_mensual * costo_kwh * 12

    if ahorro_anual > 0:
        roi_meses = total_cost / (ahorro_anual / 12)
    else:
        roi_meses = None

    return {
        "generacion_anual_estimada_kWh": generacion_anual,
        "presupuesto_total": total_cost,
        "num_paneles": num_paneles,
        "porcentaje_cobertura_consumo": porcentaje,
        "roi_meses": roi_meses,
        "detalle_presupuesto": presupuesto["detalle"]
    }

"""

# Ejemplo de uso:
if __name__ == "__main__":
    direccion = "77A, Calle 45D, Medellín, Colombia"
    area_disponible = 20
    consumo_mensual = 20000 / 12
    costo_kwh = 800 
    
    resultado = proyecto_solar(direccion, area_disponible, consumo_mensual, costo_kwh,
                               altura_superior_4m=True,
                               acceso_dificil=False,
                               distancia_mayor_20m=True,
                               instalacion_rural=False)
    
    if "error" in resultado:
        print(resultado["error"])
    else:
        print(f"Generación anual estimada: {resultado['generacion_anual_estimada_kWh']:.2f} kWh")
        print(f"Presupuesto total estimado: COP {resultado['presupuesto_total']:.2f}")
        print(f"Número de paneles instalables: {resultado['num_paneles']}")
        print(f"Porcentaje de cobertura del consumo: {resultado['porcentaje_cobertura_consumo']:.2f}%")
        print(f"ROI estimado: {resultado['roi_meses']:.2f} meses")
        print("Detalle del presupuesto:", resultado["detalle_presupuesto"])


"""