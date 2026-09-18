# -*- coding: utf-8 -*-
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="API Marmoraria Helena")

# 1. TABELA DE PREÇOS ORIGINAL
material_prices_per_sq_meter = {
    'Amarelo Icaraí': 500.00, 'Andorinha': 450.00, 'Bege Bahia': 600.00,
    'Branco Dallas': 500.00, 'Branco Flameado': 600.00, 'Branco Fortaleza': 500.00,
    'Branco Itaunas Escovado': 650.00, 'Branco Itaúna': 600.00, 'Branco Paraná': 1500.00,
    'Corumbá': 400.00, 'Florença': 600.00, 'Mármore Branco': 500.00, 'Ocre': 400.00,
    'Ornamental': 500.00, 'Preto Indiano': 500.00, 'Preto São Gabriel': 600.00,
    'Preto São Gabriel Escovado': 700.00, 'Preto Via Láctea': 700.00, 'Quartzo': 1000.00,
    'Verde Ubatuba': 450.00, 'Pitaya': 1000.00, 'Branco Prime': 1000.00, 'Flameado Branco': 620.00
}

# 2. FUNÇÕES AUXILIARES DE ARREDONDAMENTO E MATERIAL
def round_up_to_nearest_0_or_5(value):
    remainder = value % 5
    return value if remainder == 0 else value + (5 - remainder)

def get_material_price(material_name: str):
    material_name_lower = material_name.lower().strip()
    for key, price in material_prices_per_sq_meter.items():
        if key.lower() == material_name_lower:
            return price, key
    possible_matches = [key for key in material_prices_per_sq_meter.keys() if material_name_lower in key.lower()]
    if len(possible_matches) == 1:
        return material_prices_per_sq_meter[possible_matches[0]], possible_matches[0]
    return None, None

def _get_lavatorio_cuba_cost(cliente_fornece_cuba, lavatorio_cuba_type=None):
    if cliente_fornece_cuba:
        return 100.00
    if lavatorio_cuba_type == 'embutir':
        return 150.00
    if lavatorio_cuba_type == 'sobrepor':
        return 400.00
    return 0.0

# 3. MODELOS DE ENTRADA PARA A IA
class SimpleSinkInput(BaseModel):
    length_m: float
    width_m: float
    material_name: str
    num_espelhos: int
    cliente_fornece_cuba: bool

class SinkWithApronInput(BaseModel):
    length_m: float
    width_m: float
    material_name: str
    num_espelhos: int
    cliente_fornece_cuba: bool
    aprons: List[dict]
    price_45_degree_finish_per_meter: float = 80.00

class LShapedCounterInput(BaseModel):
    length_main_sink_m: float
    width_main_sink_m: float
    length_l_counter_m: float
    width_l_counter_m: float
    material_name: str
    cliente_fornece_cuba: bool

class ShowerTrayStoneInput(BaseModel):
    length_m: float
    material_name: str

class CastelinhoInput(BaseModel):
    length_m: float
    customer_width_m: float
    material_name: str

class SimpleLavatorioInput(BaseModel):
    length_m: float
    width_m: float
    material_name: str
    num_espelhos: int
    cliente_fornece_cuba: bool
    lavatorio_cuba_type: Optional[str] = None

class LavatorioWithApronInput(BaseModel):
    length_m: float
    width_m: float
    material_name: str
    num_espelhos: int
    cliente_fornece_cuba: bool
    lavatorio_cuba_type: Optional[str] = None
    aprons: List[dict]
    price_45_degree_finish_per_meter: float = 80.00

@app.get("/")
def read_root():
    return {"status": "Rodando!", "mensagem": "API Completa da Marmoraria Helena Pronta."}

# 4. ROTAS DE CÁLCULO
@app.post("/calcular-pia-simples")
def api_calcular_pia_simples(data: SimpleSinkInput):
    price, mat = get_material_price(data.material_name)
    if not price: return {"erro": "Material não encontrado ou ambíguo."}
    total = data.length_m * data.width_m * price
    if data.num_espelhos == 1: total += (data.length_m * 0.10) * price
    elif data.num_espelhos == 2: total += ((data.length_m * 0.10) + (data.width_m * 0.10)) * price
    if data.num_espelhos == 2: total += ((data.length_m * 0.05) + (data.width_m * 0.05)) * price
    elif data.num_espelhos == 1: total += ((data.length_m * 0.05) + (2 * data.width_m * 0.05)) * price
    total += 100.00 if data.cliente_fornece_cuba else 300.00
    return {"preco_total": round_up_to_nearest_0_or_5(total), "material_confirmado": mat}

@app.post("/calcular-pia-saia")
def api_calcular_pia_saia(data: SinkWithApronInput):
    price, mat = get_material_price(data.material_name)
    if not price: return {"erro": "Material não encontrado ou ambíguo."}
    total = data.length_m * data.width_m * price
    if data.num_espelhos == 1: total += (data.length_m * 0.10) * price
    elif data.num_espelhos == 2: total += ((data.length_m * 0.10) + (data.width_m * 0.10)) * price
    if data.num_espelhos == 2: total += ((data.length_m * 0.05) + (data.width_m * 0.05)) * price
    elif data.num_espelhos == 1: total += ((data.length_m * 0.05) + (2 * data.width_m * 0.05)) * price
    total += 100.00 if data.cliente_fornece_cuba else 300.00
    for apron in data.aprons:
        total += (apron['length_m'] * (apron['height_cm'] / 100)) * price + (apron['length_m'] * data.price_45_degree_finish_per_meter)
    return {"preco_total": round_up_to_nearest_0_or_5(total), "material_confirmado": mat}

@app.post("/calcular-bancada-l")
def api_calcular_bancada_l(data: LShapedCounterInput):
    price, mat = get_material_price(data.material_name)
    if not price: return {"erro": "Material não encontrado ou ambíguo."}
    total = ((data.length_main_sink_m * data.width_main_sink_m) + (data.length_l_counter_m * data.width_l_counter_m)) * price
    total += (data.length_main_sink_m + data.length_l_counter_m + data.width_l_counter_m) * 0.10 * price
    total += (data.length_main_sink_m + data.width_main_sink_m) * 0.05 * price
    total += 100.00 if data.cliente_fornece_cuba else 300.00
    return {"preco_total": round_up_to_nearest_0_or_5(total), "material_confirmado": mat}

@app.post("/calcular-pedra-box")
def api_calcular_pedra_box(data: ShowerTrayStoneInput):
    price, mat = get_material_price(data.material_name)
    if not price: return {"erro": "Material não encontrado ou ambíguo."}
    total = data.length_m * 0.09 * price * 2
    return {"preco_total": round_up_to_nearest_0_or_5(total), "material_confirmado": mat}

@app.post("/calcular-castelinho")
def api_calcular_castelinho(data: CastelinhoInput):
    price, mat = get_material_price(data.material_name)
    if not price: return {"erro": "Material não encontrado ou ambíguo."}
    total = data.length_m * 0.21 * price
    return {"preco_total": round_up_to_nearest_0_or_5(total), "material_confirmado": mat}

@app.post("/calcular-lavatorio-simples")
def api_calcular_lavatorio_simples(data: SimpleLavatorioInput):
    price, mat = get_material_price(data.material_name)
    if not price: return {"erro": "Material não encontrado ou ambíguo."}
    total = data.length_m * data.width_m * price
    if data.num_espelhos == 1: total += (data.length_m * 0.10) * price
    elif data.num_espelhos == 2: total += ((data.length_m * 0.10) + (data.width_m * 0.10)) * price
    if data.num_espelhos == 2: total += ((data.length_m * 0.05) + (data.width_m * 0.05)) * price
    elif data.num_espelhos == 1: total += ((data.length_m * 0.05) + (2 * data.width_m * 0.05)) * price
    total += _get_lavatorio_cuba_cost(data.cliente_fornece_cuba, data.lavatorio_cuba_type)
    return {"preco_total": round_up_to_nearest_0_or_5(total), "material_confirmado": mat}

@app.post("/calcular-lavatorio-saia")
def api_calcular_lavatorio_saia(data: LavatorioWithApronInput):
    price, mat = get_material_price(data.material_name)
    if not price: return {"erro": "Material não encontrado ou ambíguo."}
    total = data.length_m * data.width_m * price
    if data.num_espelhos == 1: total += (data.length_m * 0.10) * price
    elif data.num_espelhos == 2: total += ((data.length_m * 0.10) + (data.width_m * 0.10)) * price
    if data.num_espelhos == 2: total += ((data.length_m * 0.05) + (data.width_m * 0.05)) * price
    elif data.num_espelhos == 1: total += ((data.length_m * 0.05) + (2 * data.width_m * 0.05)) * price
    total += _get_lavatorio_cuba_cost(data.cliente_fornece_cuba, data.lavatorio_cuba_type)
    for apron in data.aprons:
        total += (apron['length_m'] * (apron['height_cm'] / 100)) * price + (apron['length_m'] * data.price_45_degree_finish_per_meter)
    return {"preco_total": round_up_to_nearest_0_or_5(total), "material_confirmado": mat}
