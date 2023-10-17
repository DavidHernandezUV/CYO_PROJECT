import tkinter as tk
import tksheet
from minizinc import Instance, Model, Solver

def config_gui():
    
    #CONSTANTES
    MIN_VALUE_PER_CLIENT = 0.5
    PROD_COST_N = 15
    PROD_COST_H = 25
    PROD_COST_T = 23
    CAP_N = 1000
    CAP_H = 300
    CAP_T = 500

    input_window = tk.Tk()
    input_window.title("Problema de la empresa proveedora de energía")
    input_window.geometry("900x800")
    input_window.grid_columnconfigure(0, weight=1)
    input_window.grid_rowconfigure(0, weight=1)

    input_widgets = tk.Frame(input_window)
    input_widgets.pack()
    input_widgets.config(width=800)
    #****************************************************************************
    #Costos de producción
    cost_label = tk.Label(input_widgets,text="Costos de producción:")
    cost_label.grid(row=1,column=0,sticky="w",padx=10,pady=5)
    #Nuclear
    n_label = tk.Label(input_widgets, text=f"Nuclear:")
    n_label.grid(row=0, column=1, sticky="w", padx=10, pady=5)
    n_cost_input = tk.Entry(input_widgets,width=10)
    n_cost_input.insert(0,PROD_COST_N)
    n_cost_input.grid(row=1, column=1)
    #Hidroeléctrica
    h_label = tk.Label(input_widgets, text=f"Hidroeléctrica:")
    h_label.grid(row=0, column=3, sticky="w", padx=10, pady=5)
    h_cost_input = tk.Entry(input_widgets,width=10)
    h_cost_input.insert(0,PROD_COST_H)
    h_cost_input.grid(row=1, column=3)
    #Térmica
    t_label = tk.Label(input_widgets, text=f"Térmica:")
    t_label.grid(row=0, column=5, sticky="w", padx=10, pady=5)
    t_cost_input = tk.Entry(input_widgets,width=10)
    t_cost_input.insert(0,PROD_COST_T)
    t_cost_input.grid(row=1, column=5)
    #****************************************************************************
    #Capacidad de producción
    cap_label = tk.Label(input_widgets,text="Capacidad de producción:")
    cap_label.grid(row=2,column=0,sticky="w",padx=10,pady=5,)
    #Nuclear
    n_cap_input = tk.Entry(input_widgets,width=10)
    n_cap_input.insert(0,CAP_N)
    n_cap_input.grid(row=2, column=1)
    #Hidroeléctrica
    h_cap_input = tk.Entry(input_widgets,width=10)
    h_cap_input.insert(0,CAP_H)
    h_cap_input.grid(row=2, column=3)
    #Térmica
    t_cap_input = tk.Entry(input_widgets,width=10)
    t_cap_input.insert(0,CAP_T)
    t_cap_input.grid(row=2, column=5)

    #Matriz clientes*días (mxn)
    HEADERS = ["Cliente","Día 1","Día 2","Día 3","Día 4","Día 5","Día 6","Día 7"]
    DEFAULT_DATA=[
        ["Cliente 1", 110,  130,  150,  380,  420,  170,  220],
        ["Cliente 2", 130,  200,  180,  320,  450,  130,  290],
        ["Cliente 3", 160,  140,  140,  360,  480,  180,  270],
        ["Cliente 4", 190,  170,  120,  350,  520,  110,  260],
        ["Cliente 5", 170,  1150,  140,  400,  80,  190,  150],
    ]
    
    table = tksheet.Sheet(input_widgets,header=HEADERS,total_columns=4,width=550,height=200,header_align="w")
    table.enable_bindings(
    [
        "single_select",
        "row_select",
        "column_select",
        "arrowkeys",
        "right_click_popup_menu",
        "edit_cell",
        "edit_header",
        "rc_insert_row",
        "rc_delete_row",
        "rc_insert_column",
        "rc_delete_column",
        "copy",
        "cut",
        "delete",
        "undo",
    ]
    )
    table_label = tk.Label(input_widgets,text="TABLA DE DEMANDA DIARIA")
    table_label.grid(row=5, column=0, padx=5, pady=5, columnspan=7)
    table.grid(row=6, column=0, padx=5, pady=5, columnspan=7)
    table.set_sheet_data(DEFAULT_DATA)
    #****************************************************************************
    P_HEADERS = ["Cliente","Precio/MW"]
    P_DEFAULT_DATA=[
        ["Cliente 1",35],
        ["Cliente 2",32],
        ["Cliente 3",42],
        ["Cliente 4",51],
        ["Cliente 5",32],
    ]
    p_table = tksheet.Sheet(input_widgets,header=P_HEADERS,total_columns=2,width=300,height=200,header_align="w")
    p_table.enable_bindings(
    [
        "single_select",
        "row_select",
        "column_select",
        "arrowkeys",
        "right_click_popup_menu",
        "edit_cell",
        "rc_insert_row",
        "rc_delete_row",
        "copy",
        "cut",
        "delete",
        "undo",
    ]
    )
    p_table_label = tk.Label(input_widgets,text="TABLA DE PRECIOS POR MW PARA CADA CLIENTE")
    p_table_label.grid(row=7, column=0, padx=5, pady=5, columnspan=7)
    p_table.grid(row=8, column=0, padx=5, pady=5, columnspan=7)
    p_table.set_sheet_data(P_DEFAULT_DATA)
    #*******************************************************************************************
    #Venta mínima de energía para cada cliente
    v_min_label = tk.Label(input_widgets, text=f"Venta mínima (%):")
    v_min_label.grid(row=9,column=0,sticky="w",pady=5,)
    v_min = tk.Entry(input_widgets,width=10)
    v_min.insert(0,MIN_VALUE_PER_CLIENT)
    v_min.grid(row=9,column=1)
    #Ejecución del solver
    def solve():
        daily_demand_table = table.get_sheet_data(return_copy=True)
        mw_prices_per_client = p_table.get_sheet_data(return_copy=True)
        h_cap_input_value= int(h_cap_input.get())
        n_cap_input_value= int(n_cap_input.get())
        t_cap_input_value= int(t_cap_input.get())
        h_cost_input_value = int(h_cost_input.get())
        n_cost_input_value = int(n_cost_input.get())
        t_cost_input_value = int(t_cost_input.get())
        v_min_value = float(v_min.get())
        costs = [n_cost_input_value,h_cost_input_value,t_cost_input_value]
        capacities = [n_cap_input_value,h_cap_input_value,t_cap_input_value]
        apply_solver(costs,capacities,daily_demand_table,mw_prices_per_client,v_min_value)
        
    input_widgets.grid(row=0, column=0, padx=5, pady=5)
    #Botón de resolver
    button = tk.Button(input_widgets, text="Solve", command=solve)
    button.grid(row=9, column=2, padx=5, pady=5, columnspan=5, sticky="e")

    input_window.mainloop()
def apply_solver(costs,capacities,daily_demand_table,mw_prices_per_client,v_min_value):
    model = Model("../PlantaEnergiaSimple.mzn")
    solver = Solver.lookup("coin-bc")
    instance = Instance(solver, model)
    d_bi = [row[1:] for row in daily_demand_table]
    d = [item for sublist in d_bi for item in sublist]
    precio_bi = [row[1:] for row in mw_prices_per_client]
    precio = [item for sublist in precio_bi for item in sublist]
    m = len(d_bi) 
    n = len(d_bi[0]) 
    instance["C"]=costs #Costo de producir un MW para cada planta
    instance["CAP"]=capacities #Capacidad de producción diara en MW
    instance["m"] = m #Cantidad de clientes
    instance["n"] = n #Cantidad de días a planificar
    instance["d"] = d #Demanda diaria de cada cliente
    instance["Vmin"] = v_min_value #Venta mínima de energía a cada cliente si la producción no alcanza a cubrir la demanda
    instance["precio"] = precio  #Precio de MW para cada cliente
    result = instance.solve()
    print(result.solution.produccion)
    

if __name__ == "__main__":
    config_gui()
