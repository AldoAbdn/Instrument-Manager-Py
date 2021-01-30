import sys, getopt, pyvisa, string, json
from flask import Flask, render_template, jsonify, request, redirect, make_response
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, create_refresh_token, set_access_cookies, set_refresh_cookies, jwt_refresh_token_required, unset_jwt_cookies, jwt_optional
from werkzeug.security import safe_str_cmp
from instrument import Instrument
from user import User

app = Flask(__name__)
jwt = JWTManager(app)

users = [User(1, "Admin", "1234A")]
username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}

opts, args = getopt.getopt(sys.argv[1:],"s")
if len(opts) > 0:
    resourceManager = pyvisa.ResourceManager('dummy_instruments.yaml@sim')
    print("Sim")
else:
    resourceManager = pyvisa.ResourceManager('@py')

# Home Page
@jwt_optional
@app.route('/')
def index():
    identity = get_jwt_identity()
    if not identity:
        resp = make_response(render_template('login.html'))
        unset_jwt_cookies(resp)
        return resp
    else:
        return redirect('/instrumentmanager')

# JWT
@app.route('/authenticate', methods=['POST'])
def authenticate():
    # Check params
    response = validateUser()
    if response != None:
        return response
    else:
        username = request.json.get('username', None)
        # Create the tokens we will be sending back to the user
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)

        # Set the JWT cookies in the response
        resp = jsonify(login=True)
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        return resp, 200

@app.route('/token/generate', methods=['POST'])
def generate():
    response = validateUser()
    if response != None:
        return response
    else:
        username = request.json.get('username', None)
        # Identity can be any data that is json serializable
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200

# Same thing as login here, except we are only setting a new cookie
# for the access token.
@app.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    # Set the JWT access cookie in the response
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200


# Because the JWTs are stored in an httponly cookie now, we cannot
# log the user out by simply deleting the cookie in the frontend.
# We need the backend to send us a response to delete the cookies
# in order to logout. unset_jwt_cookies is a helper function to
# do just that.
@app.route('/token/remove', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200

@jwt.unauthorized_loader
def invalid_token(expired_token):
    return redirect('/')

# Instrument Manager Page
@app.route('/instrumentmanager')
@jwt_required
def instrumentmanager():
    return render_template('instrumentmanager.html', instrumentDetails=getInstrumentDetails())

# API
@app.route('/api/instruments')
@app.route('/api/instruments/')
@app.route('/api/instruments/<search>')
@jwt_required
def instruments(search="?*::INSTR"):
    instruments = getInstrumentDetails(search)
    numResults = len(instruments)
    for x in range(len(instruments)):
        instruments[x] = instruments[x].__dict__
    response = {"search":search,"numResults":numResults,"instruments":instruments}
    return jsonify(response)

@app.route('/api/instrument/<ID>')
@jwt_required
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
        instrument = resourceManager.open_resource(ID, write_termination='\r\n', read_termination='\n')
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
    instrument = resourceManager.open_resource(ID, write_termination='\r\n', read_termination='\n')
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
            instrument = resourceManager.open_resource(ID, write_termination='\r\n', read_termination='\n')
            instrumentDetail = getInstrumentDetail(ID)
            if(instrumentDetail != None):
                instrumentDetails.append(instrumentDetail)
            instrument.close()
        except:
            pass
    return instrumentDetails

def getUser(username, password):
    user = username_table.get(username, None)
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return user

def validateUser():
    # Check params
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    user = getUser(username, password)
    if not user:
        return jsonify({"msg": "Invalid credentials"}), 400
    return None

if __name__ == '__main__':
    app.config['JWT_SECRET_KEY'] = "yolo"
    app.config['JWT_TOKEN_LOCATION'] = ['cookies', 'headers']
    app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
    app.run(threaded=True, debug=True, host='0.0.0.0')
