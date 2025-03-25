# import libraries
import os
import pickle
import re
from datetime import datetime
from .EMPData import User, EnergyConsumptionInfo, EnergyConsumptionHistory, Consumption, Util, EmpWrap
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

def singleton(cls):
    _instances = {}

    def get_instance(*args, **kwargs):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]

    return get_instance


@singleton
class BillAnalyzer:

    def __init__(self, endp:str, key:str):
        self.endpoint = endp
        self.key = key

    # helper functions
    @staticmethod
    def get_words(page, line):
        """
        Extract words from a given page that are within the spans of a specified line.

        Args:
            page (Page): The page object containing words to be extracted.
            line (Line): The line object containing spans to filter words.

        Returns:
            list: A list of words from the page that are within the spans of the line.
        """
        result = []
        for word in page.words:
            if BillAnalyzer._in_span(word, line.spans):
                result.append(word)
        return result
    

    @staticmethod
    def _in_span(word, spans):
        """
        Check if a word's span is within any of the given spans.

        Args:
            word: An object that has a `span` attribute with `offset` and `length` properties.
            spans: A list of objects, each having `offset` and `length` properties.

        Returns:
            bool: True if the word's span is within any of the given spans, False otherwise.
        """
        for span in spans:
            if word.span.offset >= span.offset and (
                word.span.offset + word.span.length
            ) <= (span.offset + span.length):
                return True
        return False


    def get_result_layout_url(self, formUrl:str, save_result:bool=False)->AnalyzeResult:
        """
        Analyzes the layout of a document from a given URL using Azure's Document Intelligence Client.
        Args:
            formUrl (str): The URL of the document to be analyzed.
            save_result (bool, optional): If True, saves the analysis result to a file named 'dato.pkl'. Defaults to False.
        Returns:
            AnalyzeResult: The result of the document layout analysis.
        """

        document_intelligence_client = DocumentIntelligenceClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        )

        poller = document_intelligence_client.begin_analyze_document(
            "prebuilt-layout", AnalyzeDocumentRequest(url_source=formUrl
        ))

        result: AnalyzeResult = poller.result()

        if save_result:
            with open('dato.pkl', 'wb') as file:
                pickle.dump(result, file)

        return result 

    def get_result_layout_bytes(self, bytes, save_result:bool=False)->AnalyzeResult:
        """
        Analyzes the layout of a document from bytes using Azure's Document Intelligence Client.
        Args:
            bytes (bytes): The document content in bytes to be analyzed.
            save_result (bool, optional): If True, the analysis result will be saved to a file named 'dato.pkl'. Defaults to False.
        Returns:
            AnalyzeResult: The result of the document layout analysis.
        """

        document_intelligence_client = DocumentIntelligenceClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        )

        poller = document_intelligence_client.begin_analyze_document(
            "prebuilt-layout", AnalyzeDocumentRequest(bytes_source=bytes
        ))

        result: AnalyzeResult = poller.result()

        if save_result:
            with open('dato.pkl', 'wb') as file:
                pickle.dump(result, file)

        return result 

    def get_result_layout_dummy(self):
        """
        Reads a pickle file named 'dato.pkl' and returns its content.
        Returns:
            Any: The content of the 'dato.pkl' file.
        """
        result = None
        with open('dato.pkl', 'rb') as archivo:
            result = pickle.load(archivo)

        return result
    
    # TODO: Implement validatios for unknown formats
    def analyze_layout(self, result):
        """
        Analyzes the layout of a document and extracts relevant information from a energy bill.
        Args:
            result: The result object containing the document layout information.
        The function performs the following tasks:
        - Checks if the document contains handwritten content.
        - Extracts user information such as service address, contract number, client name, ID, stratum, billing address, and payment reference.
        - Extracts energy consumption information including product, constant, consumption units, date, consumption, unit cost, total value, subsidy value, and energy value.
        - Extracts and processes consumption history data from the document.
        - Prints the extracted user information, consumption information, and consumption history.
        Note:
            This function assumes the presence of certain keywords and structures in the document to extract the information.
        """
        
        if result.styles and any([style.is_handwritten for style in result.styles]):
            print("Document contains handwritten content")
        else:
            print("Document does not contain handwritten content")

        if result.languages:
            print(result.languages)

        user = User()
        consumption_info = EnergyConsumptionInfo()
        consumption_hist = EnergyConsumptionHistory()

        consumption_table = []

        for page in result.pages:

            if page.lines:

                for line_idx, line in enumerate(page.lines):

                    if  page.page_number == 1 and line_idx>=103 and line_idx<=130:
                        consumption_table.append({"idx":line_idx, "content":line.content , "polygon":line.polygon})

                    #extraccion informacion general
                    if "Dirección prestación servicio" in line.content:

                        data = line.content
                        user.direccion_servicio = data[data.index(":")+1:data.index("Municipio")].strip()
                        user.municipio_servicio = data[data.index("Municipio")+10:].strip()

                    if "Contrato" in line.content:
                        data = line.content
                        user.contrato = data.split(" ")[1].strip()
                        
                    if "Cliente:" in line.content:
                        data = line.content
                        user.nombre = data.split(":")[1].strip()       

                    if "CC/NIT:" in line.content:
                        data = line.content
                        user.id = data.split(":")[1].strip()                      

                    if "Estrato:" in line.content:
                        data = line.content
                        user.estrato = data.split(" ")[4].strip()

                    if "Dirección de cobro:" in line.content:
                        data = line.content
                        user.direccion_facturacion = data.split(":")[1].strip()

                    if "Referente de pago:" in line.content:
                        data = line.content
                        consumption_info.referencia = data.split(":")[1].strip()

                    if "Producto:" in line.content and line_idx >= 300:
                        data = line.content
                        consumption_hist.producto = data.split(":")[1].strip()

        #print(user)
        #print("----------------------------------------")

        consumption_hist.usr_contatro = user.contrato
        consumption_info.usr_contatro = user.contrato

        if result.tables:
            for table_idx, table in enumerate(result.tables):
                if table_idx == 2:
                    for cell in table.cells:
                        if cell.row_index == 0:
                            if cell.column_index == 2:
                                consumption_info.constante = str(cell.content).split(" ")[1].strip()
                                #consumption.constante = cell.content
                        if cell.row_index == 1:
                            if cell.column_index == 1:
                                consumption_info.consumo_unidades = cell.content
                        if cell.row_index == 2:
                            if cell.column_index == 0:
                                consumption_info.fecha = str(cell.content).split(" ")[1].strip()
                            if cell.column_index == 1:
                                consumption_info.consumo = cell.content
                            if cell.column_index == 2:
                                consumption_info.costo_unidad = cell.content
                            if cell.column_index == 3:
                                consumption_info.valor_total = cell.content
                        if cell.row_index == 3:
                            if cell.column_index == 3:
                                consumption_info.valor_subsidio = cell.content
                        if cell.row_index == 5:
                            if cell.column_index == 3:
                                consumption_info.valor_energia = cell.content
            
            #print(consumption_info)
            #print("----------------------------------------")
        
        xd = [d for d in consumption_table if d["idx"]>=103 and d["idx"]<=111]
        pxd = sorted([e['polygon'][0] for e in xd])

        x_values = []

        for idp in pxd:
            for dat in consumption_table:
                if dat['polygon'][0] == idp:
                    x_values.append(dat['content']) 

        yd = [d for d in consumption_table if re.match('[A-Z]{3}/[0-9]{2}.*',d["content"]) or "actual" in d["content"].lower() or "prom" in d["content"].lower()]
        pyd = sorted([e['polygon'][0] for e in yd])
    

        y_values = []
        for idp in pyd:
            for dat in consumption_table:
                if dat['polygon'][0] == idp:
                    y_values.append(dat['content']) 

        for i,date in enumerate(y_values):

            if re.match('[A-Z]{3}/[0-9]{2}.*',date):
                dat = date.split("/")
                date = str(Util.get_month_num(dat[0]))+"/"+dat[1]
                date = datetime.strptime(date, '%m/%y').strftime('%m/%Y')
                print(type(date))
                desc = "consumo"
            
            elif date.lower() == "actual" or date.lower() == "prom":
                dat = consumption_info.fecha.split("-")
                date = str(Util.get_month_num(dat[0]))+"/"+dat[1]
                date = datetime.strptime(date, '%m/%y').strftime('%m/%Y')
                if date.lower() == "actual":
                    desc = "consumo"
                elif date.lower() == "prom":
                    desc = "promedio"

            cons = Consumption(date,desc,x_values[i]) 
            consumption_hist.set_consumo(cons)
            print(cons)

        #print("----------------------------------------")
        #print(consumption_hist)

        warp = EmpWrap(user,consumption_info,consumption_hist)
        return warp.__to_json__()

