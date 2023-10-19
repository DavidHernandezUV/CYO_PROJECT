% Lectura de Datos
array[1..3] of float: C; %Costo de producir un MW para cada planta
array[1..3] of int: CAP; %Capacidad de producción diara en MW
int: m; %Cantidad de clientes
int: n; %Cantidad de días a planificar
array[1..m, 1..n] of int: d; %Demanda diaria de cada cliente
float: Vmin; %Venta mínima de energía a cada cliente si la producción no alcanza a cubrir la demanda
array[1..m] of float: precio; %Precio de MW para cada cliente
float: PRAH; %Porcentaje de capacidad del régimen alto en la hidroeléctrica (H).
int: DCH; %Cantidad de días consecutivos que se prohíbe a H permanecer en régimen alto.

int: capacidad_total = sum(planta in 1..3)(CAP[planta]);
array[1..n] of float: demanda_diaria = [ sum(cliente in 1..m)(d[cliente, dia]) | dia in 1..n ];
array[1..n] of float: cota_sup_costo_diario = [ demanda_diaria[dia] * max(C) | dia in 1..n ];
array[1..n] of float: cota_sup_ingreso_diario = [ demanda_diaria[dia] * max(precio) | dia in 1..n ];


%Variables
array[1..3, 1..n] of var 0.0..capacidad_total: produccion; % MW producidos por cada planta cada día.

array[1..m, 1..n] of var float: EV; % Energía vendida a cada cliente cada día.


array[1..n] of var float: costo_total_diario; % Costo diario total de la producción de energía
array[1..n] of var float: ingresos_diarios; % Ingresos diarios producto de los pagos de cada cliente
var float: f; % Función objetivo: suma de las ganancias de cada día


% Régimen alto Hidroeléctrica (RA)

float: min_H = CAP[2] * PRAH;
float: res_H = CAP[2] * ( 1 - PRAH );


array[1..n] of var int: dias_consec_RAH; % cada día, indica el número de días consecutivos completados en RA

array[1..n] of var float: cap_diaria_H;  % Capacidad diaria de producción de la hidroeléctrica, la cual varía si 
  % la hidroeléctrica ya no puede seguir en régimen alto


%Restricciones

% NO NEGATIVIDAD
constraint forall(dia in 1..n)(
  forall(planta in 1..3)(produccion[planta, dia] >= 0)
);

constraint forall(dia in 1..n)(
  forall(cliente in 1..m)(EV[cliente, dia] >= 0)
);

constraint forall(dia in 1..n)(
  costo_total_diario[dia] >= 0
);

constraint forall(dia in 1..n)(
  ingresos_diarios[dia] >= 0
);


constraint f >= 0;

constraint forall(dia in 1..n)(
  dias_consec_RAH[dia] >= 0
);

constraint forall(dia in 1..n)( cap_diaria_H[dia] >= ( min_H ) );


% COTAS SUPERIORES

constraint forall(dia in 1..n)(
  forall(planta in 1..3)(produccion[planta, dia] <= (CAP[planta]))
);

% Energía vendida a cada cliente menor o igual a la capacidad
constraint forall(dia in 1..n, cliente in 1..m)(
  EV[cliente, dia] <= capacidad_total
);
constraint forall(dia in 1..n, cliente in 1..m)(
  EV[cliente, dia] <= d[cliente, dia]
);


constraint forall(dia in 1..n)(
  costo_total_diario[dia] <= cota_sup_costo_diario[dia]
);

constraint forall(dia in 1..n)(
  ingresos_diarios[dia] <= cota_sup_ingreso_diario[dia]
);



constraint f <= sum(dia in 1..n)( cota_sup_ingreso_diario[dia] );



constraint forall(dia in 1..n)(
  dias_consec_RAH[dia] <= dia
);

% Restricción de días consecutivos en régimen alto
constraint forall(dia in 1..n)( dias_consec_RAH[dia] <= (DCH - 1) );


constraint forall(dia in 1..n)( cap_diaria_H[dia] <= CAP[2] );

% Costo diario de producción
constraint forall(dia in 1..n)(
  costo_total_diario[dia] = sum(planta in 1..3)( produccion[planta, dia] * C[planta] )
);


% Ingreso diario de ventas
constraint forall(dia in 1..n)(
  ingresos_diarios[dia] = sum(cliente in 1..m)( EV[cliente, dia] * precio[cliente] )
);



% Cada día, la cantidad de energía vendida es igual a la producida
constraint forall(dia in 1..n)( (sum(cliente in 1..m)(EV[cliente, dia])) = 
( sum(planta in 1..3)(produccion[planta, dia]) ) );



% Función objetivo: Ganancia total
f = ( sum(dia in 1..n)( ingresos_diarios[dia] - costo_total_diario[dia] ) );


% CRITERIO DE VENTA MINIMA

% Si hay producción insuficiente un día, aplica el criterio de venta mínima. En caso
% contrario se satisface la demanda completa.
constraint forall(cliente in 1..m, dia in 1..n)(EV[cliente, dia] >= 
  (Vmin * d[cliente, dia] + ( 1 - bool2int(
    ( sum(clien in 1..m) (d[clien, dia])) >= 
    CAP[1] + cap_diaria_H[dia] + CAP[3] )
  ) * (1-Vmin) * d[cliente, dia]));




% RÉGIMEN ALTO HIDROELÉCTRICA


constraint forall (dia in 1..(DCH - 1))( produccion[2, dia] <= CAP[2] );
constraint forall (dia in DCH..n)( produccion[2, dia] <= 
  min_H + ( res_H * ( bool2int( dias_consec_RAH[(dia - 1)] <= (DCH - 2) ) ) )
);

constraint forall (dia in 1..(DCH - 1))( cap_diaria_H[dia] = CAP[2] );
constraint forall (dia in DCH..n)(cap_diaria_H[dia] = 
  min_H + ( res_H * ( bool2int( dias_consec_RAH[(dia - 1)] <= (DCH - 2) ) ) )
);






constraint dias_consec_RAH[1] = if produccion[2,1] >= (PRAH * CAP[2]) then 1 else 0 endif;

constraint forall(dia in 2..n)(
    dias_consec_RAH[dia] = 
    if produccion[2,dia] >= (PRAH * CAP[2]) then 
        dias_consec_RAH[dia-1] + 1
    else 
        0 
    endif
);


solve maximize f;