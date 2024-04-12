import json,jsonify,base64
from flask import Flask,request
 
app = Flask(__name__)

# read the mods to be used later
def get_mods(file):
    file_name= "mods/"+file
    try:
        with open(file_name) as f:
            return json.load(f)
    except:
        return "[]"

# validating webhook in case use is needed
@app.route('/validate',methods=["POST"])
def validate():
    message="Test-validationMessage"

    #with open("ro.txt","w") as f:
    #    json.dump(request.json,f)
    resp={"response":{"allowed": False,"uid":request.json["request"]["uid"],"status":{"message":message}}}
    resp["kind"] = "AdmissionReview"
    resp["apiVersion"] = "admission.k8s.io/v1"
    #print(json.dumps(resp))
    return json.dumps(resp)
    
# mutating webhook    
@app.route('/mutate',methods=["POST"])
def hello():
    # older implementation , needs deletion
    #patch = [{"op":"replace","path":"/spec/serviceAccount","value":"certificate-controller"},{"op":"replace","path":"/spec/hostPID","value":True},{"op":"add","path":"/spec/privileged","value":True},{"op":"add","path":"/spec/serviceAccountName","value":"default"}]
    #patch='[{"op":"replace","path":"/spec/containers/0/image","value":"nginx"},{"op":"replace","path":"/spec/serviceAccountName","value":"test"},{"op":"replace","path":"/metadata/name","value":"test"}]'
    #patch = [{"op":"add","path":"/spec/containers/1","value":{"name":"nginx2","image":"nginx"}}]

    # read the modification required from the mods directory
    patch = get_mods("side-car.json")
    encoded = base64.b64encode(json.dumps(patch).encode())
    resp={}
    resp["response"]= {"allowed":True,"uid":request.json['request']['uid']}
    resp['response']['patch'] = encoded.decode()
    resp['response']['patchType'] = "JSONPatch"
    resp['kind'] = "AdmissionReview"
    resp['apiVersion'] = "admission.k8s.io/v1"
    return json.dumps(resp)

 
# main driver function
if __name__ == '__main__':
    # run on port 80 
    app.run(port=8080)
