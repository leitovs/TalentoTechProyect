import json

class Util:
    """
    A utility class for handling support-related operations.
    Attributes:
        months (dict): A dictionary mapping month abbreviations in Spanish to their corresponding numerical values.
    Methods:
        get_month_num(mname):
            Converts a month abbreviation to its corresponding numerical value.
            Args:
                mname (str): The month abbreviation (e.g., 'ENE' for enero).
            Returns:
                int: The numerical value of the month (e.g., 1 for enero), or None if the abbreviation is not found.
    """

    months = {
        "ENE": 1,
        "FEB": 2,
        "MAR": 3,
        "ABR": 4,
        "MAY": 5,
        "JUN": 6,
        "JUL": 7,
        "AGO": 8,
        "SEP": 9,
        "OCT": 10,
        "NOV": 11,
        "DIC": 12
    }


    @staticmethod
    def get_month_num(mname):
        """
        Convert a month name to its corresponding month number.
        Args:
            mname (str): The name of the month (e.g., 'ENE', 'FEB', etc.).
        Returns:
            int or None: The corresponding month number (1 for Enero, 2 for Febrero, etc.) if the month name is valid; 
                         otherwise, None.
        """
        if mname.upper() in Util.months:
            return Util.months[mname.upper()]
        else:
            return None
        
    @staticmethod
    def extract_data(data:str, sep:str = " ", pos:int=0)->str:
        """
        Extracts a specific part of a string by splitting it using a given separator.

        Args:
            data (str): The input string to be processed.
            sep (str, optional): The separator used to split the string. Defaults to a single space (" ").
            pos (int, optional): The zero-based index of the part to extract after splitting. Defaults to 0.

        Returns:
            str: The extracted part of the string, stripped of leading and trailing whitespace.
                    Returns None if the specified index is out of range.
        """
        try:
            return data.split(sep)[pos].strip()
        except IndexError:
            return None
        
class User:
    """
    A class used to represent a User.
    Attributes
    ----------
    nombre : str
        The name of the user.
    contrato : str
        The contract associated with the user.
    id : int
        The unique identifier for the user.
    direccion_servicio : str
        The service address of the user.
    municipio_servicio : str
        The municipality of the service address.
    direccion_facturacion : str
        The billing address of the user.
    estrato : int
        The socioeconomic stratum of the user.
    Methods
    -------
    __str__()
        Returns a string representation of the User object.
    """

    def __init__(self):
        self.nombre = None
        self.contrato = None
        self.id = None
        self.direccion_servicio = None
        self.municipio_servicio = None
        self.direccion_facturacion = None
        self.estrato = None

    def __str__(self):
        return (f"User(nombre={self.nombre}, contrato={self.contrato}, id={self.id}, "
                f"direccion_servicio={self.direccion_servicio}, municipio_servicio={self.municipio_servicio}, "
                f"direccion_facturacion={self.direccion_facturacion}, estrato={self.estrato})")

class EnergyConsumptionInfo:
    """
    A class to represent energy consumption information.
    Attributes
    ----------
    usr_contatro : str or None
        User contract information.
    referencia : str or None
        Reference information.
    fecha : str or None
        Date of the energy consumption record.
    constante : float or None
        Constant value used in calculations.
    consumo : float or None
        Amount of energy consumed.
    consumo_unidades : str or None
        Units of the energy consumption.
    costo_unidad : float or None
        Cost per unit of energy.
    valor_total : float or None
        Total value of the energy consumed.
    valor_subsidio : float or None
        Subsidy value applied to the total cost.
    valor_energia : float or None
        Total value of the energy without subsidies.
    Methods
    -------
    __str__()
        Returns a string representation of the energy consumption information.
    """

    def __init__(self):
        self.usr_contatro = None
        self.referencia = None
        self.fecha = None
        self.constante = None
        self.consumo = None
        self.consumo_unidades = None
        self.costo_unidad = None
        self.valor_total = None
        self.valor_subsidio = None
        self.valor_energia = None

    def __str__(self):
        return (f"EnergyConsumptionInfo(usr_contatro={self.usr_contatro}, referencia={self.referencia}, fecha={self.fecha}, "
                f"constante={self.constante}, consumo={self.consumo}, consumo_unidades={self.consumo_unidades}, "
                f"costo_unidad={self.costo_unidad}, valor_total={self.valor_total}, valor_subsidio={self.valor_subsidio})")


class EnergyConsumptionHistory:
    """
    A class to represent the energy consumption history of a user.
    Attributes
    ----------
    usr_contatro : str or None
        The user contract identifier.
    producto : str or None
        The product associated with the energy consumption.
    consumos : list
        A list to store consumption records.
    Methods
    -------
    set_consumo(consumo)
        Adds a consumption record to the consumos list.
    __str__()
        Returns a string representation of the EnergyConsumptionHistory object.
    """

    def __init__(self):
        self.usr_contatro = None
        self.producto = None
        self.consumos = []

    def set_consumo(self,consumo):
        self.consumos.append(consumo)
 
    def __str__(self):
        return (f"EnergyConsumptionHistory(usr_contatro={self.usr_contatro}, producto={self.producto}, "
                f"consumos={self.consumos})")


class Consumption:
    """
    A class to represent a consumption record.
    Attributes
    ----------
    fecha : str
        The date of the consumption.
    descripcion : str
        A description of the consumption.
    valor : float
        The value of the consumption.
    Methods
    -------
    __str__():
        Returns a string representation of the Consumption object.
    """
    
    def __init__(self, fecha:str, descripcion:str, valor:float):
        self.fecha = fecha
        self.descripcion = descripcion
        self.valor = valor

    def __str__(self):
        return f"Consumption(fecha={self.fecha}, valor={self.valor})"

class GeneralInfo:
    """
    Represents general information about detection and recognition percentages.
    Attributes:
        deteccion_escritura_manual (str): Indicates manual text detection information.
        poncentaje_rec_usuario (str): Percentage of recognition related to the user.
        poncentaje_rec_info (str): Percentage of recognition related to information.
        poncentaje_rec_consumos (str): Percentage of recognition related to consumptions.
    Methods:
    """
    def __init__(self, pru:str, pri:str, prc:str, txtm:str):
        """
        Initializes an instance of the GeneralInfo class.
        Args:
            pru (str): Percentage of recognition for the user.
            pri (str): Percentage of recognition for the information.
            prc (str): Percentage of recognition for the consumptions.
            txtm (str): Manual writing detection text.
        """
        self.deteccion_escritura_manual = txtm
        self.poncentaje_rec_usuario = pru
        self.poncentaje_rec_info = pri
        self.poncentaje_rec_consumos = prc

class EmpWrap:
    """
    A wrapper class for user-related data, encapsulating general information, user details, 
    energy consumption information, and energy consumption history.
    Attributes:
        general (GeneralInfo): General information about of the result of field extraction.
        usr (User): User-specific details of the user energy subscription.
        info (EnergyConsumptionInfo): Information about the user's energy consumption.
        consumos (EnergyConsumptionHistory): Historical data of the user's energy consumption.
    Methods:
        __to_json__(): Converts the EmpWrap object into a JSON-formatted string.
    """

    def __init__(self, general:GeneralInfo , usr:User, info:EnergyConsumptionInfo, consumos:EnergyConsumptionHistory):
        self.general = general
        self.usr = usr
        self.info = info
        self.consumos_hist = consumos

    def __to_json__(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
