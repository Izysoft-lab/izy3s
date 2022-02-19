import numpy as np
from elasticsearch import Elasticsearch
import sys
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import random
from hashlib import blake2b
import operator

class Vectorization:
    def __init__(self,index_name="demonstration_sigir_paper",ontology_path="F:/activity.owl",url_api="http://localhost:8080/", base=[],clusters=[]):
        self.clusters = clusters
        self.documents=[]
        self.docs =[]
        self.es = Elasticsearch(timeout=200)
        self.val_dim=2048
        self.index_name=index_name
        self.base= base
        self.ontology_path=ontology_path
        self.url_api = url_api
    
    
    
    
    
    def get_tokens(self,text):
        tokens =[]
        concepts = self.get_concepts(text)
        for concept in concepts:
            tokens.append(concept["concept"])
        return tokens, concepts
    
  
    
    def gethash(self,word):
        h = blake2b(digest_size=35)
        h.update(str(word).encode('utf-8'))
        return h.hexdigest()
    
    def getword(self,text):
        if len(text)<15:
            return text[0:len(text)]
        else:
            return text[0:15]
    
    def nb_doc_incluster(self,concept):
        nbr=0
        for document in self.documents:
            is_in = False
            for word in set(document["tokens"]):
                if word == concept["concept"]:
                    is_in  =True
                    break
            if is_in ==True:
                nbr +=1
        if nbr==0:
            return 0
        else:
            return np.log(len(self.base)/nbr)
        
    def df(self,document,concept):
        tf=0
        val= self.count_concepts(document["tokens"],concept)
        tf +=val
        if len(document["tokens"])==0:
               return 0,1
        else:
            return np.power(tf/len(document["tokens"]),0.5),1
    
    def count_concepts(self,concepts, concept):
        num = 0
        for element in concepts:
            if element == concept:
                num+=1
        return num

    
    def get_vectors(self):
        for document in self.progressbar(self.documents, "get vectors: ", 80):
            vector = np.zeros(shape=len(self.clusters))
            for index, cluster in enumerate(self.base):
                tf,facto=self.df(document,cluster)
                vector[index]=tf*self.clusters[index]["idf"]
            document["vector"]=self.neated_vectors(vector)
            document["norm"]= np.linalg.norm(vector)
        print("Done.")
        
        
    def buil_documents(self,texts):
        concept_count = 0
        all_tokens = []
        for index, text in enumerate(self.progressbar(texts, "build documents: ", 80)):
            wordhas=None
            if len(text)<15:
                wordhas= self.getword(text[0:len(text)])+str(np.array(random.sample(range(0, 500), 15)).sum())
            else:
                wordhas= self.getword(text[0:15])+str(np.array(random.sample(range(0, 500), 15)).sum())
            idhas = self.gethash(wordhas)
            tokens,concepts = self.get_tokens(text)
            all_tokens.extend(tokens)
            document ={
                "text":text,
                "vector":None,
                "id":idhas,
                "tokens":tokens,
                "norm":None,
                "concepts":concepts
                }
            self.documents.append(document)
        self.base = list(set(all_tokens))
        for e in self.base:
            self.clusters.append({"concept": e})
        if len(self.clusters)<2048:
            self.val_dim =len(self.clusters)
        print("Done.")
        
    
    
    def compute_idf(self):    
        for cluster in self.progressbar(self.clusters, "compute idf: ", 80):
            cluster["idf"]=self.nb_doc_incluster(cluster)
        print("Done.")
            
    def fit(self,docs_texts):
        self.buil_documents(docs_texts)
        self.compute_idf()
        self.get_vectors()
        print("get_docs")
        self.get_docs()
        print("Done.")
        print("create index")
        try:
            self.create_index()
            print("Done.")
            for doc in self.progressbar(self.docs, "build docs index: ", 80):
                res = self.es.index(index=self.index_name, id=doc["doc_id"], body=doc)
            print("Done.")
            return self
        except:
            print("An exception accurred during de index creation")
            return self
            
        
    
    def get_docs(self):
        self.docs = [{"texte":doc["text"],"vectors":doc["vector"],"doc_id":doc["id"],"norm":doc["norm"],"concepts":doc["concepts"]} for doc in self.documents]
    

    def buil_query(self,text):
        tokens,concepts = self.get_tokens(text)
        vector = np.zeros(shape=len(self.clusters))
        vectors=[]
        for word in tokens:
            index_cluster =None
            if word in self.base:
                index_cluster = self.base.index(word)
           
            if index_cluster!=None:
                vector[index_cluster]+=6
                vectors.append({"indice":index_cluster,"val":6})
                
        return {"vectors":vectors, "norm":np.linalg.norm(vector)}, concepts
    
    def buil_query_ontology(self,text):
        tokens,concepts = self.get_tokens(text)
        
        return tokens
    
    
    def neated_vectors(self,vec):
        part = len(vec)//self.val_dim
        rest = len(vec)%self.val_dim
        vector = []
        for i in range(0,part):
            vector.append({"vector":vec[i*self.val_dim: i*self.val_dim+self.val_dim]})
        if rest!=0:
            val= np.zeros(self.val_dim)
            for i in range(part*self.val_dim,part*self.val_dim+rest):
                val[i-part*self.val_dim]=vec[i]
            vector.append({"vector":val})
        return vector

    
    def create_index(self):
        settings = {
        "settings": {
        "number_of_shards": 1,
        "index" : {
            "similarity" : {
              "default" : {
                "type" : "BM25",
                "b": 0.5,
                "k1": 0
              }
            }
        }
      },
        "mappings": {
               "properties" : {
                      "vectors":{
                            "type":"nested",
                            "properties":{
                                "vector":{
                                "type": "dense_vector",
                                "dims": self.val_dim
                            },
                        },
                        "fielddata":{
                            "loading":"eager"
                        }
                        },
                      "doc_id" : {
                          "type" : "text"
                          },
                        "texte": {
                             "type" : "text"
                         },
                       "norm": {
                             "type" : "double"
                         },
                       "concepts": {
                            "type": "nested" 
                        },
                    }
            }
        }
    
        self.es.indices.create(index=self.index_name, ignore=400, body=settings)
        
        
        
    def annotation(self, text):
        tokens,conceptse = self.get_tokens(text)
        doc_text =text
        concepts_all = list({v['label']:v for v in conceptse}.values())
        concepts =[]
        for el in concepts_all:
            concepts.append({'startNode': int(el['startNode']),'endNode': int(el['endNode']),'label': el['label'],'concept': el['concept']})
        concepts =sorted(concepts,key=operator.itemgetter('endNode'))
        if(len(concepts))>0:
            for i in range(0,len(concepts)):
                doc_text= doc_text[0:i*17+int(concepts[i]["startNode"])]+"<strong>"+doc_text[i*17+int(concepts[i]["startNode"]):i*17+int(concepts[i]["endNode"])]+"</strong>"+doc_text[i*17+int(concepts[i]["endNode"]):len(doc_text)]
    
        return {"text":doc_text, "concepts_labels":concepts}
    
    
    
    def get_res_query(self,query_text):
        query_vect,concepts_query =  self.buil_query(query_text)
        query ={
              "query": {
                "script_score": {
                  "query" : {
                    "match_all": {}
                  },
                  "script": {
                     "source": """
                    double dot_produit = 0.0;
                    def li = params['_source'].vectors; 
                    def nor_doc = params['_source'].norm;
            
                    for(int i=0;  i<params.query_vector.length ; i++){    
                        int part = params.query_vector[i].indice/params.val_dim;
                        int rest = params.query_vector[i].indice % params.val_dim;
                        dot_produit += li[part].vector[rest]*params.query_vector[i].val;
                        
                    }
                    if(dot_produit==0){
                    return 0
                    } 
                    return dot_produit/(nor_doc*params.norm);
        
                """, 
                    "params": {
                      "query_vector":query_vect["vectors"],
                        "norm":query_vect["norm"],
                        "val_dim":self.val_dim
                    }
                  }
                ,
                "min_score":0.05
                }
              }
            }
        res = self.es.search(index=self.index_name, body=query)
        responses = []
        for e in res["hits"]["hits"]:
            doc_text =e["_source"]["texte"]
            concepts_all = list({v['label']:v for v in e["_source"]["concepts"]}.values())
            concepts =[]
            for el in concepts_all:
                is_in =False
                for con in concepts_query:
                    if el['concept'].lower()==con["concept"].lower():
                        is_in = True
                if is_in ==True:
                    concepts.append({'startNode': int(el['startNode']),'endNode': int(el['endNode']),'label': el['label'],'concept': el['concept']})
            
            
            concepts =sorted(concepts,key=operator.itemgetter('endNode'))
            if(len(concepts))>0:
                for i in range(0,len(concepts)):
                    doc_text= doc_text[0:i*17+int(concepts[i]["startNode"])]+"<strong>"+doc_text[i*17+int(concepts[i]["startNode"]):i*17+int(concepts[i]["endNode"])]+"</strong>"+doc_text[i*17+int(concepts[i]["endNode"]):len(doc_text)]
                    
            responses.append({"text":doc_text,"norm":e["_source"]["norm"],"conceps_labels":concepts,"_score":e["_score"],"id":e["_source"]["doc_id"]})
        return responses
        
    
        
    def progressbar(self,it, prefix="", size=60, file=sys.stdout):
        count = len(it)
        def show(j):
            x = int(size*j/count)
            file.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), j, count))
            file.flush()        
        show(0)
        for i, item in enumerate(it):
            yield item
            show(i+1)
        file.write("\n")
        file.flush()
        
        
    def get_concepts(self,text):
            param = {'document': text}
            file = {'myFile': ('activity.owl', open(self.ontology_path, 'rb'), 'text/plain')}
            response = requests.post(self.url_api, files=file, data= param)
            data= response.json()
            return data
    
    def get_all_concepts(self):
        file = {'myFile': ('activity.owl', open(self.ontology_path, 'rb'), 'text/plain')}
        response1 = requests.post(self.url_api+'allconcept', files=file)
        return response1.json()

    
    def get_all_concepts_labels(self):
        file = {'myFile': ('activity.owl', open(self.ontology_path, 'rb'), 'text/plain')}
        response1 = requests.post(self.url_api+'allconcept/labels', files=file)
        return response1.json()
    
    

