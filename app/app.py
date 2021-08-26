import psycopg2
from os import error
from flask import Flask, json, render_template, request, jsonify
from werkzeug.utils import redirect
app = Flask(__name__)

# declaramos constantes globales
PSQL_HOST = "localhost"
PSQL_PORT = "5432"
PSQL_USER = "postgres"
PSQL_PASS = "1234"
PSQL_DB = "Planilla"

# Conexion
connection_address = """
host=%s port=%s user=%s password=%s dbname=%s
""" % (PSQL_HOST, PSQL_PORT, PSQL_USER, PSQL_PASS, PSQL_DB)
connection = psycopg2.connect(connection_address)



"""      --------------------------------------------------------------------       """

@app.route('/')
def Index():
  data = {}
  try:
    cursor = connection.cursor()
    SQL = "select case mes when '1' then 'Enero' when '2' then 'Febrero' when '3' then 'Marzo' when '4' then 'Abril' when '5' then 'Mayo' when '6' then 'Junio'	when '7' then 'Julio'	when '8' then 'Agosto' when '9' then 'Setiembre' when '10' then 'Octubre'	when '11' then 'Noviembre' when '12' then 'Diciembre'	end, anual, idmes	from mesproceso"
    cursor.execute(SQL)
    fechas = cursor.fetchall()
    data['fechas'] = fechas
    
  except Exception as ex:
    data['mensaje'] = 'error'
  connection.commit()
  cursor.close()
  return render_template('index.html', data=data)

@app.route('/planilla', methods=['GET'])
def planilla():
  data = {}
  try:
    cursor = connection.cursor()
    idfecha = request.args.get('fecha')
    SQL = "select CONCAT(t.apellidos,' ',t.nombres), t.basico, a.descripcion, p.diasfalta,p.horasfalta, p.totalingresos, p.totaldescuentos, p.idplanilla from planilla p inner join trabajador t on t.idtrabajador=p.idtrabajador inner join afp a on a.idafp=t.idafp where p.idmes='"+idfecha+"'"
    cursor.execute(SQL)
    planilla = cursor.fetchall()
    
    data['planilla'] = planilla
    data['num'] = 1
  except Exception as ex:
    data['mensaje'] = 'error'
  connection.commit()
  cursor.close()
  return render_template('planilla.html', data=data)

@app.route('/calcular', methods=['GET'])
def calcular():
  data = {}
  try:
    cursor = connection.cursor()
    idfecha = request.args.get('fecha2') 
    idfecha=idfecha.strip()
    QUERY_AFTER= "SELECT * FROM Planilla where idmes = '"+idfecha+"'"
    cursor.execute(QUERY_AFTER)
    planilla = cursor.fetchall()
    SQL = "select case mes when '1' then 'Enero' when '2' then 'Febrero' when '3' then 'Marzo' when '4' then 'Abril' when '5' then 'Mayo' when '6' then 'Junio'	when '7' then 'Julio'	when '8' then 'Agosto' when '9' then 'Setiembre' when '10' then 'Octubre'	when '11' then 'Noviembre' when '12' then 'Diciembre'	end, anual, idmes	from mesproceso"
    cursor.execute(SQL)
    fechas = cursor.fetchall()
    data['fechas'] = fechas
    print(len(planilla))
    if len(planilla)>0:
      data['calculado']="0"
    else:
      SQL = "select calculatePlanilla('"+ idfecha + "');"
      cursor.execute(SQL)
      print(idfecha)
      data['calculado'] = '1'
    #return redirect('/detalle'+idfecha+'a')
  except Exception as ex:
    print(idfecha)
    data['calculado'] = '2'
    raise ValueError(ex)
  connection.commit()
  cursor.close()
  return render_template('index.html', data=data)

@app.route('/detalle/<idplanilla>')
def detalle(idplanilla):
  data = {}
  try:
    cursor = connection.cursor()
    SQL = "select c.nombre, dp.monto, tc.descripcion, dp.idcuenta from detaplanilla dp inner join concepto c on dp.idconcepto=c.idconcepto inner join tipoconcepto tc on tc.idtipoconcepto=c.idtipoconcepto where idplanilla='"+idplanilla+"'"
    cursor.execute(SQL)
    detalle = cursor.fetchall()
    print('Get values: ', detalle)
    data['detalle'] = detalle
  except Exception as ex:
    data['mensaje'] = 'error'
  connection.commit()
  cursor.close()
  return render_template('detaplanilla.html', data=data)
  
@app.route('/cuentacorriente')
def cuentacorriente():
  data = {}
  try:
    cursor = connection.cursor()
    SQL = "select idtrabajador,apellidos from trabajador where estado='1'"
    cursor.execute(SQL)
    detalle = cursor.fetchall()
    data['detalle'] = detalle
  except Exception as ex:
    data['mensaje'] = 'error'
  connection.commit()
  cursor.close()
  return render_template('cuentacorriente.html',data=data)  
  
@app.route('/prestamo/<idcuenta>')
def prestamo(idcuenta):
  data = {}
  try:
    cursor = connection.cursor()
    SQL = "select * from cuentacorriente where idCuenta='"+idcuenta+"'"
    cursor.execute(SQL)
    prestamo = cursor.fetchall()
    print('Get values: ', prestamo)
    data['prestamo'] = prestamo
  except Exception as ex:
    data['mensaje'] = 'error'
  connection.commit()
  cursor.close()
  return render_template('prestamo.html', data=data)

@app.route('/guardarCta', methods=['POST'])
def guardarCta():
  data = {}
  try:
    cursor = connection.cursor()
    monto = request.form['monto']
    cuota = request.form['cuota']
    idTrabajador = request.form['idTrabajador']
    idfecha=idTrabajador.strip()
    QUERY_AFTER= "SELECT * FROM cuentacorriente where idtrabajador = '"+idTrabajador+"'"
    cursor.execute(QUERY_AFTER)
    cuentas = cursor.fetchall()
    SQL = "select idtrabajador,apellidos from trabajador where estado='1'"
    cursor.execute(SQL)
    trabajadores = cursor.fetchall()
    data['detalle'] = trabajadores
    if len(cuentas)>0:
      data['ingresado']="0"
    else:
      
      data['detalle'] = trabajadores
      SQL = "select PA_INSERT_CUENTA_CORRIENTE('"+ idTrabajador+ "',"+monto+","+cuota+");"
      cursor.execute(SQL)
      print(idfecha)
      data['ingresado'] = '1'
    #return redirect('/detalle'+idfecha+'a')
  except Exception as ex:
    print(idfecha)
    data['ingresado'] = '2'
    raise ValueError(ex)
  connection.commit()
  cursor.close()
  return render_template('cuentacorriente.html', data=data)



if __name__ == "__main__":
    app.run(port=5000, debug=True)


