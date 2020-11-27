# -*- coding: utf-8 -*-
#import matplotlib.pyplot as plt
import os, sys, traceback
from pathlib import Path
import io


class SimuladorG9C2():
    """ Implementación de simulación de 
    asignación de memoria con particiones fijas
    y planificación de procesos con algoritmo SJF
    """

    def __init__(self):
        super(SimuladorG9C2, self).__init__()
        # Inicializacion de datos para carga de procesos
        self.process = []          #Almacene información de proceso completa
        self.name = ''             
        self.irrupcion_time = 0
        self.arribo_time = 0
        self.size = 0
        self.state = ''
        self.number = 0
        self.timeout = 0
        self.start = 0
        self.end = 0   
        self.partitions =  []
        self.listos = []
        self.partitions_history = []
        self.partitions_allocation = []
        self.tiempo_total = 0

    def insert_process_data(self, name, arribo_time, irrupcion_time, size):
        ''' Agrega los procesos a la tabla a medida que lo cargamos
            ya sea a traves del archivo o manualmente
        '''
        self.process.append({
            'id': self.number,
            'name': name,
            'arribo_time': int(arribo_time),
            'irrupcion_time': int(irrupcion_time),
            'size':int(size),
            'state': 'Cargado',
            'respuesta_time': 0,
            'authorized_turnover_time': 0,
            'start': 0,
            'end': 0
        })
        self.timeout = max(self.timeout, int(arribo_time))
        self.number += 1
        return self.process

    def create_partition_table(self):
        ''' Carga la tabla de particiones 
            luego de que se cargan los procesos
        ''' 
        so = {
                'id': 1,
                'partition_name': 'SO',
                'partition_size': 100,
                'partition_size_fixed': 100,
                'partition_state': True,
                'partition_start': 0,
                'partition_end':99,
                'proc_asig': 'SO',
                'fragint': 0,
                'probable_assignment': []
            }
        self.partitions.append(so)
        grandes = {
                'id': 2,
                'partition_name': 'TGRANDES',
                'partition_size': 250,
                'partition_size_fixed': 250,
                'partition_state': False,
                'partition_start': 100,
                'partition_end':350,
                'proc_asig': '-',
                'fragint': 0,
                'probable_assignment': []
            }
        self.partitions.append(grandes)
        medianos = {
                'id': 3,
                'partition_name': 'TMEDIANOS',
                'partition_size': 120,
                'partition_size_fixed': 120,
                'partition_state': False,
                'partition_start': 351,
                'partition_end':471,
                'proc_asig': '-',
                'fragint': 0,
                'probable_assignment': []
            }
        self.partitions.append(medianos)
        pequenios = {
                'id': 4,
                'partition_name': 'TPEQUES',
                'partition_size': 60,
                'partition_size_fixed': 60,
                'partition_state': False,
                'partition_start': 472,
                'partition_end':532,
                'proc_asig': '-',
                'fragint': 0,
                'probable_assignment': []
            }
        self.partitions.append(pequenios)

        return self.partitions

    def get_data_file(self):
        ''' Esta funcion carga los datos de procesos 
            a partir de un archivo de texto
        '''

        #this_folder = os.path.dirname(os.path.abspath(__file__))
        #data_file = os.path.join(this_folder, 'data.txt')
        data_file = resource_path("data_files/data.txt")
        with open(data_file, "r", encoding="utf-8") as file:
            lines = file.readlines()
            num_lines = len([l for l in lines if l.strip(' \n') != ''])
            if num_lines>10:
                print('Puede procesar hasta 10 procesos como máximo')
                print('Por favor modifique el archivo y vuelva a ejecutar')
            else:
                for line in lines:
                    name, arribo_time, irrupcion_time, size = line.split('\t')
                    # Agrego el proceso a la lista
                    self.insert_process_data(name, arribo_time, irrupcion_time, size)
        file.close()
        # Cola inicial
        # Ordenar por tiempo de arribo y tiempo de irrupcion
        self.process.sort(key=lambda x: (x['arribo_time'], x['irrupcion_time']))
        # Actualizo id de proceso
        for i in range(self.number):
            self.process[i]['index'] = i

    def get_data_input(self):
        ''' Esta funcion carga los datos de procesos 
            a partir del ingreso de datos proceso por proceso
        '''

        # Solicito el ingreso de la cantidad de procesos a utilizar en la simulacion
        try:
            print('Cuantos procesos utilizara en la simulación?')
            print('Puede procesar hasta 10 procesos como máximo')
            process_number = int(input('Ingrese cantidad de procesos:'))
            print("\n")

        # Verifico que ingrese un valor entero sino solicito que ingrese nuevamente
        except ValueError:                                                      
            print('Por favor ingrese un numero entero que indique la cantidad de procesos a utilizar en la simulación')
            print('Cuantos procesos utilizara en la simulación?')
            print('Puede procesar hasta 10 procesos como máximo')
            process_number = int(input('Ingrese cantidad de procesos:'))
            print("\n")

        # Verifico que ingrese un valor menor a 10 sino solicito que ingrese nuevamente
        finally:
            while process_number>10:
                try:
                    print('Puede procesar hasta 10 procesos como máximo. Ingrese un valor menor a 10')
                    print('Cuantos procesos utilizara en la simulación?')
                    process_number = int(input('Ingrese cantidad de procesos:'))
                    print("\n")

                # Verifico que ingrese un valor entero sino solicito que ingrese nuevamente
                except ValueError:                                                      
                    print('Por favor ingrese un numero entero que indique la cantidad de procesos a utilizar en la simulación')
                    print('Cuantos procesos utilizara en la simulación?')
                    print('Puede procesar hasta 10 procesos como máximo')
                    process_number = int(input('Ingrese cantidad de procesos:'))
                    print("\n")
        
        print('Por favor ingrese nombre de proceso, tiempo de arribo, tiempo de irrupcion y tamaño separados por espacios')
        print('Por ejemplo: A 0 5 50')
        try:
            for _ in range(process_number):
                name, arribo_time, irrupcion_time, size = input('Por favor ingrese datos del proceso, como se muestra en el ejemplo:\n').split()
                self.insert_process_data(name, arribo_time, irrupcion_time, size)
        except ValueError:
            print("Debe ingresar los datos separados por un espacio en el siguiente formato:")
            print('Nombre de proceso    Tiempo de arribo   Tiempo de irrupcion  Tamaño de proceso')
            print('Por ejemplo: A 0 5 50')
    
    def are_all_partitions_occupied(self):
        occupied = True
        for j in range(1, len(self.partitions)):
            if( self.partitions[j].get('proc_asig') == '-'):
                occupied = False
                break
        return occupied

    def implement_best_fit(self):
        '''
            Realiza asignación de memoria a bloques 
            según el algoritmo de mejor ajuste
        '''
        # Almacena el ID de bloque del bloque asignado a un proceso
        allocation_id = [-1] * (len(self.partitions)-1)
        #Recorre la lista de procesos y encuentra lugar que tiene mejor ajuste para asignacion
        for i in range(len(self.process)): 
            # Encuentra la particion que mejor ajusta al proceso actual
            best_alloc = -1
            for j in range(1, len(self.partitions)): 
                # Compara el tamanio de la particion con el del proceso para realizar la asignacion
                if self.partitions[j].get('partition_size') >= self.process[i].get('size') and self.process[i].get('size'): 
                    if best_alloc == -1:  
                        best_alloc = j  
                    elif self.partitions[best_alloc].get('partition_size') > self.partitions[j].get('partition_size'):  
                        best_alloc = j      
    
            # If we could find a block for current process
            if best_alloc != -1:
                # allocate block j to p[i] process
                try:
                    allocation_id[i-1] = best_alloc 
                except Exception as identifier:
                    #print(i)
                    pass
                
                # Reduce available memory in this block.  
                #blockSize[best_alloc] -= processSize[i] 
                #print(self.process[i].get('name'), best_alloc)
                self.partitions[best_alloc]['probable_assignment'].append(self.process[i].get('name'))


    def show_data_running(self, start, end, process):
        print('-'*40)
        print("Desde t={:} Hasta t={:}".format(start, end))
        print("Proceso en ejecucion : {:}".format(process['name']))
        print("Estado de proceso: {:}\n".format(process['state']))
        def process_in_partition(partition):
            #print(partition)
            #print(process['name'])
            if partition['proc_asig']==process['name']:
                return True
            else:
                return False
        filtered = list(filter(process_in_partition, self.partitions))
        #print(filtered)
        #print("Asignado a particion: {:}\n".format(self.partitions['partition_name']))
        #print("Fragmentacion: {:}\n".format(self.partitions['fragint']))
        print("Cola de Listos: {:}\n".format(self.listos))
        print("Tabla de Particiones X\n")
        #print(self.partitions)
        print("{:<6}{:<10}{:<10}{:<7}{:<10}{:<15}{:<15}{:<15}".format(
            'id', 'partname', 'size','state', 'dir_ini', 'dir_fin', 'proc_asignado', 'fragmentacion'))
        for i in range(len(self.partitions)):
            print("{:<6}{:<10}{:<10}{:<7}{:<10}{:<15}{:<15}{:<15}".format(
                self.partitions[i]['id'],
                self.partitions[i]['partition_name'],
                self.partitions[i]['partition_size'],
                self.partitions[i]['partition_state'],
                self.partitions[i]['partition_start'],
                self.partitions[i]['partition_end'],
                self.partitions[i]['proc_asig'],
                self.partitions[i]['fragint']))
            history_dict= { 'desde':start, 
                            'hasta':end, 
                            'idpart':self.partitions[i]['id'], 
                            'namepart':self.partitions[i]['partition_name'],
                            'statepart':self.partitions[i]['partition_state'],
                            'proc_asig':self.partitions[i]['proc_asig']}
            self.partitions_history.append(history_dict.copy())
        print("\n")


    def show_data_inicio(self):
        print("\n")
        print('- Inicio de simulacion -')
        print('Tiempo total de ejecucion esperado:', self.tiempo_total)
        print("\n")
        print("Tabla de Procesos Inicial\n")
        print("{:<6}{:<10}{:<10}{:<7}{:<10}{:<15}{:<15}{:<7}{:<4}".format(
            'name', 'arr_time', 'irr_time','size', 'state', 'time_rta', 'time_rta_prom', 'start', 'end'))
        for process in sorted(self.process, key=lambda x: x['id']):
            print("{:<6}{:<10}{:<10}{:<7}{:<10}{:<15}{:<15}{:<7}{:<4}".format(
                process['name'],
                process['arribo_time'],
                process['irrupcion_time'],
                process['size'],
                process['state'],
                process['respuesta_time'],
                process['authorized_turnover_time'],
                process['start'],
                process['end']))
        print("\n")
        
        print("Tabla de Particiones Inicial\n")
        print("{:<6}{:<10}{:<10}{:<7}{:<10}{:<15}".format(
            'id', 'partname', 'size','state', 'dir_ini', 'dir_fin'))
        for partition in sorted(self.partitions, key=lambda x: x['id']):
            print("{:<6}{:<10}{:<10}{:<7}{:<10}{:<15}".format(
                partition['id'],
                partition['partition_name'],
                partition['partition_size'],
                partition['partition_state'],
                partition['partition_start'],
                partition['partition_end']))
        print("\n")

        print('Cola de Listos', 'Vacia')

        print('-'*40)
        print('Inicio de ejecucion de procesos')

    def cmp(self):
        '''Esta funcion indica la manera en que 
            se van a ir ordenando los procesos.
        '''
        return lambda x: (x['irrupcion_time'], x['arribo_time'], x['index'])

    def sort_process_data(self, process):
        self.listos = []
        for x in sorted(process, key=self.cmp()):
            self.listos.append(x['name'])
        return sorted(process, key=self.cmp())


    def update_information(self, index, start, end):
        self.process[index]['start'] = start
        self.process[index]['end'] = end
        self.process[index]['respuesta_time'] = end - \
            self.process[index]['arribo_time']
        self.process[index]['authorized_turnover_time'] = self.process[index]['respuesta_time'] / \
            self.process[index]['irrupcion_time']
        self.start = start
        self.end = end
        if self.process[index]['state'] == 'Ejecucion':
            #print(self.process[index]['name']
            self.listos.pop(0)
        self.show_data_running(start, end, self.process[index])

    def get_next_data(self, index,  process):
        ''' Obtiene siguiente proceso
        '''
        # obtener procesos desde el tiempo inicial hasta el tiempo final del proceso actual
        result = [x for x in self.process if x ['arribo_time'] <=
                self.end and x['state'] == 'Cargado' and x not in process]
        if (result and len(result) > 0) or process:
            if(len(result) > 0) :
                #Cambio de estado porque arranca nueva ejecucion
                #print(index)
                #print(result)
                realindex = 0 if len(result) == 1 else index
                result[realindex]['state']='Ejecucion'
            return result
        # No se han ingresado procesos hasta este momento
        for iprocess in self.process:
            if iprocess['state'] == 'Cargado':
                self.start = self.end = iprocess['arribo_time']
                return [iprocess]
        return []

    def update_partition_table(self, process):
        for j in range(1, len(self.partitions)):
            if(process['name'] in self.partitions[j]['probable_assignment']):
                self.partitions[j]['partition_size_fixed'] = self.partitions[j].get('partition_size')-process['size']
                self.partitions[j]['fragint'] = self.partitions[j].get('partition_size')-process['size']
                self.partitions[j]['partition_state'] = True
                self.partitions[j]['proc_asig'] = process['name']
                break

    def implement(self):
        '''Implementa simulacion completa'''
        
        # Cola inicial
        # Ordenar por tiempo de arribo y tiempo de irrupcion
        self.process.sort(key=lambda x: (x['arribo_time'], x['irrupcion_time']))
        for l in self.process:
            self.listos.append(l['name'])
        # Actualizar id de proceso
        self.tiempo_total = 0
        for i in range(self.number):
            self.process[i]['index'] = i
            self.tiempo_total += self.process[i]['irrupcion_time']
        # Obtiene el primer proceso
        process = [self.process[0]]
        Simulador.create_partition_table()
        self.partitions_allocation = self.partitions
        Simulador.implement_best_fit()
        Simulador.show_data_inicio()
        # Actualiza el tiempo de inicio
        self.start = self.end = process[0]['arribo_time']
        self.tiempo = 0
        while process:
            print(self.listos)
            self.process[0]['state'] = 'Ejecucion'
            # actualiza informacion del proceso
            self.update_partition_table(process[0])
            self.update_information(
                process[0]['index'], self.end, self.end + process[0]['irrupcion_time'])
            self.tiempo = self.tiempo + process[0]['irrupcion_time']
            if self.tiempo == self.end:
                self.process[0]['state'] = 'Terminado'
                for p in range(len(self.partitions)):
                    if self.partitions[p]['proc_asig'] == self.process[0]['name']:
                        self.partitions[p]['partition_state'] = False
                        self.partitions[p]['proc_asig'] = '-'
                        self.partitions[p]['fragint'] = 0
            # obtiene siguiente proceso
            process += self.get_next_data(process.pop(0)['index'], process)
            # se genera cola de procesos
            process = self.sort_process_data(process)
        self.process.sort(key=lambda x: x['id'])


    def main(self):
        if input('Quiere ingresar los datos para simulación subiendo un archivo? Ingrese si/SI or no/NO \n') in ['si', 'SI']:
            Simulador.get_data_file()
        else:
            Simulador.get_data_input()
        Simulador.implement()
        #Simulador.show_image()
            
def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

def print_file(file_path):
        file_path = resource_path(file_path)
        with open(file_path) as fp:
            for line in fp:
                print(line)
if __name__ == '__main__':
    try:
        print_file('data_files/data.txt')
        Simulador = SimuladorG9C2()
        Simulador.main()
    except Exception as e:
        print('No es posible ejecutar, excepcion encontrada:', e)
        traceback.print_exc(file=sys.stdout)
    except BaseException:
        import sys
        print(sys.exc_info()[0])
        import traceback
        print(traceback.format_exc())
    else:
        print('Simulación finalizada')
    finally:
        print("Presione Enter para cerrar la ventana ...")
        input()
