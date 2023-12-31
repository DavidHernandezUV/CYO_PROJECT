import tkinter as tk
import tksheet
from minizinc import Instance, Model, Solver
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.gridspec import GridSpec

matplotlib.use("TkAgg")
def config_gui():
    
    #CONSTANTES
    PROD_COST_N = 15
    PROD_COST_H = 25
    PROD_COST_T = 23
    CAP_N = 1000
    CAP_H = 300
    CAP_T = 500
    MIN_VALUE_PER_CLIENT = 0.5
    PRAH_VALUE_PER_CLIENT = 0.8
    DCH_VALUE_PER_CLIENT = 2
    

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
    #*******************************************************************************************
    #Porcentaje de capacidad del régimen alto en la hidroeléctrica
    prah_label = tk.Label(input_widgets, text=f"Capacidad de H (%):")
    prah_label.grid(row=9,column=2,sticky="w",pady=5,)
    prah = tk.Entry(input_widgets,width=10)
    prah.insert(0,PRAH_VALUE_PER_CLIENT)
    prah.grid(row=9,column=3)
    #*******************************************************************************************
    #Cantidad de días consecutivos que se prohíbe a H permanecer en régimen alto
    dch_label = tk.Label(input_widgets, text=f"Días consecutivos:")
    dch_label.grid(row=9,column=4,sticky="w",pady=5,)
    dch = tk.Entry(input_widgets,width=10)
    dch.insert(0,DCH_VALUE_PER_CLIENT)
    dch.grid(row=9,column=5)
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
        dch_value = int(dch.get())
        prah_value = float(prah.get())
        costs = [n_cost_input_value,h_cost_input_value,t_cost_input_value]
        capacities = [n_cap_input_value,h_cap_input_value,t_cap_input_value]
        apply_solver(costs,capacities,daily_demand_table,mw_prices_per_client,v_min_value,dch_value,prah_value)
    
        
    input_widgets.grid(row=0, column=0, padx=5, pady=5)
    #Botón de resolver
    button = tk.Button(input_widgets, text="Solve", command=solve)
    button.grid(row=9, column=6, padx=5, pady=5, columnspan=5, sticky="e")

    input_window.mainloop()
def apply_solver(costs,capacities,daily_demand_table,mw_prices_per_client,v_min_value,dch_value,prah_value):
    model = Model("../PlantaEnergia.mzn")
    solver = Solver.lookup("coin-bc")
    instance = Instance(solver, model)
    d_bi = [row[1:] for row in daily_demand_table]
    d = [item for sublist in d_bi for item in sublist]
    d = [int(x) for x in d]
    precio_bi = [row[1:] for row in mw_prices_per_client]
    precio = [item for sublist in precio_bi for item in sublist]
    precio = [int(x) for x in precio]
    m = len(d_bi) 
    n = len(d_bi[0])
    print(costs,capacities,m,n,d,v_min_value,precio,prah_value,dch_value)
    instance["C"]=costs #Costo de producir un MW para cada planta
    instance["CAP"]=capacities #Capacidad de producción diara en MW
    instance["m"] = m #Cantidad de clientes
    instance["n"] = n #Cantidad de días a planificar
    instance["d"] = d #Demanda diaria de cada cliente
    instance["Vmin"] = v_min_value #Venta mínima de energía a cada cliente si la producción no alcanza a cubrir la demanda
    instance["precio"] = precio  #Precio de MW para cada cliente
    instance["PRAH"] = prah_value #Porcentaje de capacidad del régimen alto en la hidroeléctrica (H).
    instance["DCH"] = dch_value #Cantidad de días consecutivos que se prohíbe a H permanecer en régimen alto.
    result = instance.solve()
    #print(result.solution.produccion)
    print(result)
    show_results(result)
    
def show_results(result):
    results_window = tk.Tk()
    results_window.title("Solución")
    results_window.configure(bg="white")

    # Crear una figura con una cuadrícula de 2x2
    figure = Figure(figsize=(10, 8), dpi=100)
    gs=GridSpec(3,4) # 2 rows, 3 columns
    #*********************************PRODUCTION*****************************************
    subplot1 = figure.add_subplot(gs[0,2:])
    production = result.solution.produccion
    days = list(range(1,len(production[0])+1))
    colors = ['b', 'g', 'r']
    labels = ['Nuclear', 'Hidroeléctrica', 'Térmica']
    for i, data in enumerate(production):
        subplot1.plot(days, data, label=labels[i], color=colors[i])
        for day, value in zip(days, data):
            subplot1.text(day, value, f"{value:.1f}", ha='center', va='bottom', fontsize=8)
    subplot1.legend()
    subplot1.set_xlabel('Días')
    subplot1.set_ylabel('MW')
    subplot1.set_title('Producción por día')
    #*********************************Main function*****************************************
    main_function_label = tk.Label(results_window, text='Máxima ganancia',bg="white",font=("Arial", 16))
    main_function_label.pack()
    f = tk.Label(results_window, text="$ "+str(round(result.solution.f,2)),bg="white",font=("Arial", 16))
    f.pack()
    #*********************************daily total cost*****************************************
    subplot3 = figure.add_subplot(gs[0,0])
    daily_cost = result.solution.costo_total_diario
    days = list(range(1, len(daily_cost) + 1))
    bars = subplot3.bar(days, daily_cost, align='center')
    subplot3.set_xlabel('Día')
    subplot3.set_ylabel('Costo')
    subplot3.set_title('Costo Total Diario')
    for bar, cost in zip(bars, daily_cost):
        height = bar.get_height()
        subplot3.annotate(f'{cost:.1f}', xy=(bar.get_x() + bar.get_width() / 2, height+4),
                        xytext=(0, 3), textcoords='offset points', ha='center', va='bottom', fontsize=7)

    #*********************************daily total income*****************************************
    subplot4 = figure.add_subplot(gs[0,1])
    daily_income = result.solution.ingresos_diarios
    days = list(range(1, len(daily_income) + 1))
    bars = subplot4.bar(days, daily_income, align='center')
    subplot4.set_xlabel('Día')
    subplot4.set_ylabel('Ingresos')
    subplot4.set_title('Ingresos Diarios')
    for bar, cost in zip(bars, daily_income):
        height = bar.get_height()
        subplot4.annotate(f'{cost:.1f}', xy=(bar.get_x() + bar.get_width() / 2, height+4),
                        xytext=(0, 3), textcoords='offset points', ha='center', va='bottom', fontsize=7)
        
    
    #*********************************EV*****************************************
    subplot5 = figure.add_subplot(gs[1,:])
    EV = result.solution.EV
    EV = [[round(value, 2) for value in row] for row in EV]
    empty_row = [None] * len(EV[0])
    EV.insert(0, empty_row)
    table = subplot5.table(cellText=EV, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    rows_labels = [f'Cliente {i + 1}' for i in range(len(EV)-1)]
    columns_labels = [f'Día {i + 1}' for i in range(len(EV[0]))]
    for i, label in enumerate(rows_labels):
        table.add_cell(i + 1, -1, 0.1, 0.1, text=label, loc='center', facecolor='lightgray')
    for j, label in enumerate(columns_labels):
        table.add_cell(0, j, 0.1, 0.1, text=label, loc='center', facecolor='lightgray')
    subplot5.set_title('Energía vendida x cliente')
    subplot5.axis('off')
    # Mostrar la figura
    #figure.tight_layout()
    #*********************************Daily Capacity H*****************************************
    subplot6 = figure.add_subplot(gs[2,:2])
    daily_cap_h = result.solution.cap_diaria_H
    days = list(range(1,len(daily_cap_h)+1))
    color = 'b'
    label = 'Hidroeléctrica'
    subplot6.plot(days, daily_cap_h, label=label, color=color)
    for day, value in zip(days, daily_cap_h):
        subplot6.text(day, value, f"{value:.1f}", ha='center', va='bottom', fontsize=8)
    subplot6.legend()
    subplot6.set_xlabel('Días')
    subplot6.set_ylabel('MW')
    subplot6.set_title('Capacidad por día')
    #*********************************Consecutives days*****************************************
    subplot7 = figure.add_subplot(gs[2,2:])
    rah = result.solution.dias_consec_RAH
    columns_labels = [f'Día {i + 1}' for i in range(len(rah))]
    table = subplot7.table(cellText=[rah], loc='center', cellLoc='center',colLabels=columns_labels)
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    

    subplot7.set_title('Días consecutivos en régimen alto (Hidroeléctrica)')
    subplot7.axis('off')
    # Mostrar la figura
    #figure.tight_layout()
    # Agregar la figura a la ventana
    figure_canvas = FigureCanvasTkAgg(figure, results_window)
    figure_canvas.get_tk_widget().pack(padx=5, pady=5)
    
if __name__ == "__main__":
    config_gui()
