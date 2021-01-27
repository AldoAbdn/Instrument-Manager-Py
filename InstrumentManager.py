import sys, getopt, pyvisa
from flask import Flask, render_template, jsonify, request
from instrument import Instrument
import json

app = Flask(__name__)

opts, args = getopt.getopt(sys.argv[1:],"s")
if len(opts) > 0:
    resourceManager = pyvisa.ResourceManager('dummy_instruments.yaml@sim')
    print("Sim")
else:
    resourceManager = pyvisa.ResourceManager('@py')

# Home Page
@app.route('/')
def index():
    return render_template('login.html')

# Instrument Manager Page
@app.route('/instrumentmanager')
def instrumentmanager():
    return render_template('instrumentmanager.html', instrumentDetails=getInstrumentDetails())

# API
@app.route('/api/instruments')
@app.route('/api/instruments/')
@app.route('/api/instruments/<search>')
def instruments(search="?*::INSTR"):
    instruments = getInstrumentDetails(search)
    numResults = len(instruments)
    for x in range(len(instruments)):
        instruments[x] = instruments[x].__dict__
    response = {"search":search,"numResults":numResults,"instruments":instruments}
    return jsonify(response)

@app.route('/api/instrument/<ID>')
def instrument(ID):
    query = request.args.get("query")
    if query == None:
        instrumentDetails = getInstrumentDetail(ID)
        if(instrumentDetails != None):
            response = {"ID":ID, "instrument":instrumentDetails.__dict__}
        else:
            response = {"ERROR":"Error Occured"}
        return jsonify(response)
    else:
        result = queryInstrument(ID, query)
        response = {"ID":ID,"query":query,"result":result}
        return jsonify(response)

# Util
def getInstrumentDetail(ID):
    try:
        instrument = resourceManager.open_resource(ID, write_termination='\r\n', read_termination='\n');
    except:
        return None
    instrumentDetails = Instrument(instrument.resource_name, instrument.resource_manufacturer_name, instrument.interface_number, "")
    try:
        instrumentDetails.status = instrument.last_status
    except:
        instrumentDetails.status = ""
    if not isinstance(instrumentDetails.manufacturer, str):
        instrumentDetails.manufacturer = ""
    if instrument != None:
        instrument.close()
    return instrumentDetails

def queryInstrument(ID,query):
    instrument = resourceManager.open_resource(ID, write_termination='\r\n', read_termination='\n');
    if isinstance(instrument, pyvisa.resources.MessageBasedResource):
        result = instrument.query(query)
    elif isinstance(instrument, pyvisa.resources.RegisterBasedResource):
        result = None
    else:
        result = None
    return result
    
def getInstrumentDetails(query="?*::INSTR"):
    instrumentDetails = []
    ids = resourceManager.list_resources(query)
    for ID in ids:
        try:
            instrument = resourceManager.open_resource(ID, write_termination='\r\n', read_termination='\n');
            instrumentDetail = getInstrumentDetail(ID)
            if(instrumentDetail != None):
                instrumentDetails.append(instrumentDetail)
            instrument.close()
        except:
            pass
    return instrumentDetails

if __name__ == '__main__':
    app.run(threaded=True, debug=True, host='0.0.0.0')
