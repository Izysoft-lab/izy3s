import json
import random
import shelve

from flask import Flask, jsonify, make_response, render_template, request
from flask_cors import CORS
from model import Vectorization
from waitress import serve
import requests
import operator

app = Flask(__name__)
CORS(app)


@app.route("/")
def welcome():
    return render_template("index.html")


@app.route("/query", methods=["POST"])
def query():
    if request.method == "POST":
        data = dict((key, request.form.getlist(key)) for key in request.form.keys())
        data = dict((key, request.form.getlist(key) if len(request.form.getlist(key)) > 1 else request.form.getlist(key)[0]) for key in request.form.keys())
        shelf =None
        
        try:
            shelf = shelve.open("index.shlf")
            if len(shelf["base"])==0:
                 return make_response("no index found", 404)
        except:
            print("An exception accurred during de index creation")

        model = Vectorization()
        model.base=shelf["base"]
        model.ontology_path=shelf["ontology_path"]
        model.url_api=shelf["url_api"]
        model.index_name=shelf["index_name"]
        model.clusters =shelf["clusters"]
        results = model.get_res_query(data["query"])
        return make_response(jsonify(results), 200)
    
@app.route("/indexation", methods=["POST"])
def indexation():
    if request.method == "POST":
        
        """
        data = request.form.to_dict()
        print(request.form)
        print(data["ontology_path"])
        print(data["url_api"])
        print(data["index_name"])
        print(data["documents"])
        results = []
        """
        data = dict((key, request.form.getlist(key)) for key in request.form.keys())
        data = dict((key, request.form.getlist(key) if len(request.form.getlist(key)) > 1 else request.form.getlist(key)[0]) for key in request.form.keys())
        print(len(data["documents"]))
        
        model = Vectorization(ontology_path=data["ontology_path"],url_api=data["url_api"],index_name="demonstration_sigir_paper")
        for element in model.es.indices.get_alias("*").keys():
            model.es.indices.delete(index=element)
        model.fit(data["documents"])
        shelf = shelve.open("index.shlf")
        shelf["base"]=model.base
        shelf["ontology_path"]=model.ontology_path
        shelf["url_api"]= model.url_api
        shelf["index_name"]=model.index_name
        shelf["clusters"]=model.clusters
        
        
        return make_response("Successful indexing", 201)

@app.route("/annotation", methods=["POST"])
def annotation():
    if request.method == "POST":
        data = dict((key, request.form.getlist(key)) for key in request.form.keys())
        data = dict((key, request.form.getlist(key) if len(request.form.getlist(key)) > 1 else request.form.getlist(key)[0]) for key in request.form.keys())
        shelf =None
        try:
            shelf = shelve.open("index.shlf")
            if len(shelf["base"])==0:
                 return make_response("no index found", 404)
        except:
            print("An exception accurred during loading")

        model = Vectorization()
        model.base=shelf["base"]
        model.ontology_path=shelf["ontology_path"]
        model.url_api=shelf["url_api"]
        model.index_name=shelf["index_name"]
        model.clusters =shelf["clusters"]
        results = model.annotation(data["text"])
        return make_response(jsonify(results), 200)
    
@app.route("/upload", methods=["POST"])
def upload():
    if request.method == "POST":
        if 'file' not in request.files:
            
            return "file"
        file = request.files['file']
        print(file.filename)
       
        fil = {'myFile': (file.filename, file, 'text/plain')}
        response1 = requests.post("http://localhost:8080/ontology", files=fil)
        return make_response(jsonify(response1.json()), 201)

@app.route("/ontology", methods=["GET"])
def ontology():
    if request.method == "GET":
       response1 = requests.get("http://localhost:8080/ontology")
       return make_response(jsonify(response1.json()), 200)
        

@app.route("/annotation_id", methods=["GET"])
def annotation_id():
        if request.method == "GET":
            text = request.args.get("document")
            id = request.args.get("id")
       
            file = {'id': id,'document':text}
            response1 = requests.get("http://localhost:8080/annotation_ontology", params=file)
            conceptse = response1.json()
            doc_text =text
            concepts_all = list({v['label']:v for v in conceptse}.values())
            concepts =[]
            for el in concepts_all:
                concepts.append({'startNode': int(el['startNode']),'endNode': int(el['endNode']),'label': el['label'],'concept': el['concept']})
            concepts =sorted(concepts,key=operator.itemgetter('endNode'))
            if(len(concepts))>0:
                for i in range(0,len(concepts)):
                    doc_text= doc_text[0:i*17+int(concepts[i]["startNode"])]+"<strong>"+doc_text[i*17+int(concepts[i]["startNode"]):i*17+int(concepts[i]["endNode"])]+"</strong>"+doc_text[i*17+int(concepts[i]["endNode"]):len(doc_text)]
             
            return make_response(jsonify({"text":doc_text, "concepts_labels":concepts}), 200)

@app.route("/delete_onto", methods=["DELETE"])
def delete_onto():
        if request.method == "DELETE":
            id = request.args.get("id")
       
            file = {'id': id}
            response1 = requests.get("http://localhost:8080/delete_onto", params=file)
            return "ok"


		
if __name__ == "__main__":
    print("Done")
    serve(app, listen='*:5002')
    
