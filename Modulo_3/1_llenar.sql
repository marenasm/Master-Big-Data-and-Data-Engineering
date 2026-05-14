USE primera_parte;

-- -------------------------------------------------------
-- INSERT MEDICO 
-- -------------------------------------------------------
INSERT INTO MEDICO (NOMBRE, ESPECIALIDAD, TELEFONO, EMAIL) VALUES
('Dr. Carlos Mendoza',    'Cirugia de Trasplante', '3001234567', 'cmendoza@hospital.com'),
('Dra. Laura Rios',       'Nefrologia',            '3019876543', 'lrios@hospital.com'),
('Dr. Andres Castillo',   'Cardiologia',           '3027654321', 'acastillo@hospital.com'),
('Dra. Valentina Torres', 'Hepatologia',           '3035551234', 'vtorres@hospital.com'),
('Dr. Felipe Gomez',      'Inmunologia',           '3041239876', 'fgomez@hospital.com'),
('Dra. Marcela Herrera',  'Cirugia General',       '3054321098', 'mherrera@hospital.com'),
('Dr. Javier Morales',    'Neumologia',            '3063214567', 'jmorales@hospital.com'),
('Dra. Natalia Vargas',   'Endocrinologia',        '3079874321', 'nvargas@hospital.com'),
('Dr. Sebastian Ortiz',   'Urologia',              '3088765432', 'sortiz@hospital.com'),
('Dra. Diana Salcedo',    'Anestesiologia',        '3097654321', 'dsalcedo@hospital.com');

-- -------------------------------------------------------
-- INSERT PACIENTE 
-- -------------------------------------------------------
INSERT INTO PACIENTE (NOMBRE, FECHA_NACIMIENTO, GENERO, HISTORIAL_MEDICO, CONTACTO) VALUES
('Luis Ramirez',    '1980-03-15', 'M', 'Insuficiencia renal cronica desde 2015',      'luis.ramirez@gmail.com / 3101112233'),
('Maria Perez',     '1975-07-22', 'F', 'Cirrosis hepatica diagnosticada en 2018',     'mperez@yahoo.com / 3112223344'),
('Jorge Suarez',    '1990-11-08', 'M', 'Miocardiopatia dilatada desde 2020',          'jsuarez@hotmail.com / 3123334455'),
('Ana Diaz',        '1968-01-30', 'F', 'Diabetes tipo 1 con complicaciones renales',  'adiaz@gmail.com / 3134445566'),
('Carlos Vega',     '1985-05-19', 'M', 'Fibrosis pulmonar idiopatica',                'cvega@outlook.com / 3145556677'),
('Sandra Lopez',    '1992-09-14', 'F', 'Lupus eritematoso sistemico',                 'slopez@gmail.com / 3156667788'),
('Tomas Guerrero',  '1978-12-03', 'M', 'Hepatitis C cronica con cirrosis',            'tguerrero@yahoo.com / 3167778899'),
('Claudia Munoz',   '1983-04-27', 'F', 'Poliquistosis renal autosomica dominante',    'cmunoz@hotmail.com / 3178889900'),
('Ricardo Pena',    '1971-08-11', 'M', 'Insuficiencia cardiaca congestiva grado III', 'rpena@gmail.com / 3189990011'),
('Patricia Molina', '1995-02-25', 'F', 'Colangitis esclerosante primaria',            'pmolina@outlook.com / 3190001122');

-- -------------------------------------------------------
-- INSERT OPERACION_TRASPLANTE (10 registros)
-- -------------------------------------------------------
INSERT INTO OPERACION_TRASPLANTE (FECHA, TIPO_PROCEDIMIENTO, ZONA_DONANTE, ZONA_RECEPTORA, ID_PACIENTE, ID_MEDICO) VALUES
('2023-01-10', 'Trasplante renal',    'Rinon izquierdo donante cadaverico', 'Fosa iliaca derecha',      1,  1),
('2023-02-14', 'Trasplante hepatico', 'Lobulo derecho higado donante vivo', 'Abdomen superior derecho', 2,  4),
('2023-03-22', 'Trasplante cardiaco', 'Corazon donante cadaverico',         'Mediastino',               3,  3),
('2023-04-05', 'Trasplante renal',    'Rinon derecho donante vivo',         'Fosa iliaca izquierda',    4,  2),
('2023-05-18', 'Trasplante pulmonar', 'Pulmon derecho donante cadaverico',  'Cavidad toracica derecha', 5,  7),
('2023-06-30', 'Trasplante renal',    'Rinon izquierdo donante cadaverico', 'Fosa iliaca derecha',      6,  1),
('2023-07-12', 'Trasplante hepatico', 'Lobulo izquierdo donante vivo',      'Abdomen superior',         7,  4),
('2023-08-25', 'Trasplante renal',    'Rinon derecho donante cadaverico',   'Fosa iliaca izquierda',    8,  2),
('2023-09-09', 'Trasplante cardiaco', 'Corazon donante cadaverico',         'Mediastino',               9,  3),
('2023-10-21', 'Trasplante hepatico', 'Higado completo donante cadaverico', 'Abdomen superior',        10,  4);

-- -------------------------------------------------------
-- INSERT CITA (10 registros)
-- -------------------------------------------------------
INSERT INTO CITA (FECHA_HORA, MOTIVO, CONFIRMACION, ID_PACIENTE, ID_MEDICO) VALUES
('2024-01-08 09:00:00', 'Evaluacion pre-trasplante renal',           TRUE,  1,  1),
('2024-01-15 10:30:00', 'Revision funcion hepatica post-trasplante', TRUE,  2,  4),
('2024-01-22 08:00:00', 'Control cardiologico de rutina',            TRUE,  3,  3),
('2024-02-05 11:00:00', 'Ajuste de inmunosupresores',                FALSE, 4,  2),
('2024-02-12 14:00:00', 'Revision pulmonar mensual',                 TRUE,  5,  7),
('2024-02-20 09:30:00', 'Seguimiento nefrologico',                   TRUE,  6,  2),
('2024-03-01 10:00:00', 'Control enzimas hepaticas',                 FALSE, 7,  4),
('2024-03-10 08:30:00', 'Evaluacion funcion renal',                  TRUE,  8,  1),
('2024-03-18 13:00:00', 'Ecocardiograma de seguimiento',             TRUE,  9,  3),
('2024-03-25 15:00:00', 'Biopsia hepatica de control',               FALSE, 10, 4);

-- -------------------------------------------------------
-- INSERT VISITA_SEGUIMIENTO 
-- -------------------------------------------------------
INSERT INTO VISITA_SEGUIMIENTO (FECHA, OBSERVACIONES, RESULTADOS, RECOMENDACIONES, ID_PACIENTE, ID_MEDICO) VALUES
('2024-01-10', 'Paciente estable, sin signos de rechazo',          'Creatinina 1.2 mg/dL, funcion normal',        'Continuar inmunosupresion actual',         1,  1),
('2024-01-18', 'Leve ictericia, se investigan causas',             'Bilirrubina 2.8 mg/dL, transaminasas altas',  'Ajustar dosis de tacrolimus',              2,  4),
('2024-01-25', 'Paciente refiere fatiga moderada',                 'FE 55%, ritmo sinusal normal',                'Reposo relativo, control en 2 semanas',    3,  3),
('2024-02-08', 'Sin quejas, tension arterial controlada',          'Creatinina 1.4 mg/dL, electrolitos normales', 'Mantener dieta baja en sodio',             4,  2),
('2024-02-15', 'Disnea leve al esfuerzo',                         'Espirometria FVC 70%, DLCO reducida',         'Incrementar fisioterapia respiratoria',     5,  7),
('2024-02-22', 'Bien tolerada la medicacion actual',              'Creatinina 1.1 mg/dL, proteinuria minima',    'Continuar seguimiento mensual',            6,  1),
('2024-03-05', 'Dolor abdominal leve en hipocondrio derecho',     'Ecografia sin hallazgos significativos',       'Analgesia leve y observacion',             7,  4),
('2024-03-12', 'Paciente asintomatica, evolucion favorable',      'Creatinina 1.3 mg/dL, presion normal',        'Reducir gradualmente corticoides',         8,  2),
('2024-03-20', 'Edema leve en miembros inferiores',               'BNP 250 pg/mL, leve congestion',              'Aumentar diuretico, control semanal',      9,  3),
('2024-03-28', 'Sin sintomas, excelente adherencia al tratamiento','Funcion hepatica dentro de parametros',       'Espaciar controles a cada 2 meses',       10,  4);

-- -------------------------------------------------------
-- INSERT DOCUMENTO_ARCHIVO (10 registros)
-- -------------------------------------------------------
INSERT INTO DOCUMENTO_ARCHIVO (TIPO_DOCUMENTO, DESCRIPCION, ARCHIVO_ADJUNTO, FECHA, ID_PACIENTE) VALUES
('Historia Clinica',   'Historia clinica completa pre-trasplante',           'historia_luis_ramirez.pdf',       '2022-12-01',  1),
('Biopsia',            'Resultado biopsia hepatica inicial',                 'biopsia_maria_perez.pdf',         '2022-11-15',  2),
('Ecocardiograma',     'Ecocardiograma pre-trasplante cardiaco',             'eco_jorge_suarez.pdf',            '2023-02-10',  3),
('Analisis de Sangre', 'Panel metabolico completo',                          'labs_ana_diaz.pdf',               '2023-03-20',  4),
('Radiografia',        'Radiografia de torax pre-operatoria',                'rx_torax_carlos_vega.jpg',        '2023-04-30',  5),
('Consentimiento',     'Consentimiento informado trasplante renal',          'consentimiento_sandra_lopez.pdf', '2023-06-01',  6),
('TAC Abdominal',      'Tomografia abdominal post-trasplante',               'tac_tomas_guerrero.pdf',          '2023-07-20',  7),
('Urografia',          'Urografia excretora de seguimiento',                 'urografia_claudia_munoz.pdf',     '2023-08-30',  8),
('Electrocardiograma', 'ECG de control post-trasplante cardiaco',            'ecg_ricardo_pena.pdf',            '2023-09-15',  9),
('Colangiografia',     'Colangiografia de control post-trasplante hepatico', 'colangio_patricia_molina.pdf',    '2023-10-25', 10);

-- -------------------------------------------------------
-- INSERT MEDICACION_TRATAMIENTO
-- -------------------------------------------------------
INSERT INTO MEDICACION_TRATAMIENTO (NOMBRE, DOSIS, FRECUENCIA, DURACION, FECHA_INICIO, FECHA_FIN, ID_PACIENTE) VALUES
('Tacrolimus',              '2 mg',   'Cada 12 horas',  'Indefinido', '2023-01-15', NULL,         1),
('Micofenolato',            '500 mg', 'Cada 8 horas',   'Indefinido', '2023-02-20', NULL,         2),
('Prednisona',              '10 mg',  'Una vez al dia', '12 meses',   '2023-03-25', '2024-03-25', 3),
('Ciclosporina',            '100 mg', 'Cada 12 horas',  'Indefinido', '2023-04-10', NULL,         4),
('Azatioprina',             '50 mg',  'Una vez al dia', 'Indefinido', '2023-05-22', NULL,         5),
('Sirolimus',               '1 mg',   'Una vez al dia', 'Indefinido', '2023-07-05', NULL,         6),
('Omeprazol',               '20 mg',  'Una vez al dia', '6 meses',    '2023-07-15', '2024-01-15', 7),
('Furosemida',              '40 mg',  'Una vez al dia', '3 meses',    '2023-08-28', '2023-11-28', 8),
('Metoprolol',              '25 mg',  'Cada 12 horas',  'Indefinido', '2023-09-12', NULL,         9),
('Acido Ursodesoxicolico',  '500 mg', 'Cada 8 horas',   '24 meses',   '2023-10-25', '2025-10-25',10);

-- -------------------------------------------------------
-- INSERT FACTURA_PAGO 
-- -------------------------------------------------------
INSERT INTO FACTURA_PAGO (FECHA, CONCEPTO, MONTO, ESTADO_PAGO, DETALLES_TRANSACCION, ID_PACIENTE) VALUES
('2023-01-12', 'Cirugia de trasplante renal',          15000000.00, 'Pagado',     'Transferencia bancaria Bancolombia #TXN00123', 1),
('2023-02-16', 'Trasplante hepatico y hospitalizacion', 22000000.00, 'Pagado',     'Pago EPS Sanitas, autorizacion #AU456789',    2),
('2023-03-24', 'Trasplante cardiaco y UCI',             30000000.00, 'Pendiente',  'En tramite aseguradora Sura, caso #SU789',    3),
('2023-04-07', 'Trasplante renal mas inmunosupresores', 16500000.00, 'Pagado',     'Transferencia Davivienda #TXN00456',           4),
('2023-05-20', 'Trasplante pulmonar bilateral',         28000000.00, 'En proceso', 'Aprobacion parcial EPS Compensar #CP112',     5),
('2023-07-02', 'Trasplante renal y medicacion',         14800000.00, 'Pagado',     'Pago en efectivo recibo #RC00789',             6),
('2023-07-14', 'Trasplante hepatico donante vivo',      19500000.00, 'Pagado',     'Transferencia Bancolombia #TXN00891',          7),
('2023-08-27', 'Trasplante renal y seguimiento',        13200000.00, 'Pendiente',  'Factura enviada, plazo 30 dias',               8),
('2023-09-11', 'Trasplante cardiaco y rehabilitacion',  32000000.00, 'Pagado',     'Pago EPS Famisanar, autorizacion #FA334',      9),
('2023-10-23', 'Trasplante hepatico completo',          25000000.00, 'En proceso', 'Revision preautorizacion EPS Coomeva #CO556', 10);
