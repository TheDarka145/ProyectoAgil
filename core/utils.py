import bcchapi
import numpy as np
from datetime import datetime


def obtener_tasa_cambio():

    siete = bcchapi.Siete(file="core/credenciales.txt")


    fecha_hoy = datetime.today().strftime('%Y-%m-%d')


    tasa_cambio_df = siete.cuadro(
        series=["F073.TCO.PRE.Z.D"],  
        nombres=["tasa_cambio_usd_clp"],  
        desde=fecha_hoy,  
        hasta=fecha_hoy,  
        frecuencia="D",  
        observado={"tasa_cambio_usd_clp": np.mean}  
    )
    

    if tasa_cambio_df.empty:
        return "No disponible"
    

    return tasa_cambio_df['tasa_cambio_usd_clp'].iloc[0]
