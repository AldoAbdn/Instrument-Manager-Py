from flask import Flask, render_template, jsonify
import pyvisa

app = Flask(__name__)
resourceManager = pyvisa.ResourceManager('@py')

# Home Page
@app.route('/')
def index():
    return render_template('instrumentmanager.html', instruments=getInstruments())

# API
@app.route('/api/instruments')
@app.route('/api/instruments/')
@app.route('/api/instruments/<search>')
def instruments(search="?*::INSTR"):
    instruments = getInstruments(search)
    numResults = len(instruments)
    response = {"numResults":numResults,"instruments":instruments}
    return jsonify(response)

@app.route('/api/instrument/<ID>')
def instrument(ID):
    instrument = resourceManager.open_resource(id)
    if instrument != None:
        instrument.close()
    response = {"ID":ID, "instrument":instrument}
    return jsonify(response)

@app.route('/api/instrument/<ID>/<query>')
def queryInstrument(ID,query):
    instrument = resourceManager.open_resource(id)
    if isinstance(instrument, pyvisa.resources.MessageBasedResource):
        result = instrument.query(query)
    elif isinstance(instrument, pyvisa.resources.RegisterBasedResource):
        result = None
    else:
        result = None
    response = {"ID":ID,"query":query,"result":result}
    return jsonify(response)
    
# Util
def getInstruments(query="?*::INSTR"):
    instruments = []
    ids = resourceManager.list_resources(query)
    for id in ids:
        instrument = resourceManager.open_resource(id)
        instruments.append(instrument)
        instrument.close()
    instruments.append({"resource_name":"Test"})
    return instruments

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
