# Izy3S
This project is a prototype of a semantic search engine

## How to install

Make sure you are running Python 3.7 or higher

Make sure you have Elasticsearch installed and configured on your computer and listening on the default port 9200

`$ pip install -r requirements.txt`



## requirements

This search engine works with our api for automatic document annotation 
Gate Rest API you can find [here](https://duckduckgo.com). 

API for annotating documents is a Tomcat server that the search engine uses to find all the concepts in the documents for semantic indexing. So for the engine to work, you need to deploy this server on your machine and run it.

*RG* : `You have to clone and launch this annotation server before testing the search engine`



## Debug Installation

**Launch Annotation API and make sure it is listening on port 8080**  

**Launch Elasticsearch and make sure it is listening on port 9200**

## Lunch application
Open the project directory and run the command  

`python launch.py` or `python3 launch.py `

If everything works well the server will run on `http://localhost:5002`

# Documentation of API



**Indexation**
----
  Index a document collection, as a text list.

* **URL**

  /indexation

* **Method:**

  `POST`
  
*  **BODY**

   **Required:**
 
   ```
      {
            "ontology_path": "Location_of_ontology",
            "url_api": "url_ontology_api",
            "index_name": "index_name",
            "documents": [
                "doc1",
                "doc2",
                "doc3",
                "doc4"
                ....
            ]
        }
      ```

* **Data Params**

  None

* **Success Response:**

  * **Code:** 201 <br />
    **Content:** `Successful indexing`
 
* **Error Response:**

  * **Code:** 500 INTERNAL ERROR <br />
    **Content:** `{ bat request }`


#### Description of the body ####
 * **ontology_path** : The path to your ontology on your machine

 * **url_api** : api url for semantic annotation

 * **index_name** : The name of the Elasticsearch index where the documents will be indexed







**Make Query**
----
  Make a query to find documents sharing the same concepts as those in the query

* **URL**

  /query

* **Method:**

  `POST`
  
*  **BODY**

   **Required:**
 
   ```
    {
           "query":"Search query"
    }
    ```

* **Data Params**

  None

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** 
      ```
      [
                {
                    "text": "document",
                    "norm": 3.695,
                    "conceps_labels": [
                        {
                            "startNode": 181,
                            "endNode": 194,
                            "label": "SportRaquette",
                            "concept": "SportRaquette"
                        },
                        {
                            "startNode": 376,
                            "endNode": 386,
                            "label": "AutreSport",
                            "concept": "AutreSport"
                        }
                        ...
                    ],
                    "_score": 0.99559164,
                    "id": "id"
                }
                ...
         ]
      ```
 
* **Error Response:**

  * **Code:** 500 INTERNAL ERROR <br />
    **Content:** `{ bat request }`



**Upload onotology for annotation**
----
  For annotation, you must upload the ontology owl file before 

* **URL**

  /upload

* **Method:**

  `POST`
  
*  **BODY**

   **Required:**
   *type: multipart formdata*
 
   ``` 
        {
           "file":"file_to_upload"
        }
   ```

* **Data Params**

  None

* **Success Response:**

  * **Code:** 201 <br />
    **Content:** 
    
    ```
           {
                "id": "id of new file"
            }
      ```
 
* **Error Response:**

  * **Code:** 500 INTERNAL ERROR <br />
    **Content:** `{ bat request }`


**GEt all ontology files**
----
  Get the list of all ontology files uploaded on the server.

* **URL**

  /ontology

* **Method:**

  `GET`
  
*  **BODY**

   **Required:**
 
   None

* **Data Params**

  None

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** 
     ```
      [   
                {
                    "createAt": "2022-02-17T16:04:56.947Z",
                    "fileName": "activity.owl",
                    "id": "59e370dabbb8da8ff49ca1ff28f5fb279161c72d"
                },
                
                 ....
        ]

    ```

 
* **Error Response:**

  * **Code:** 500 INTERNAL ERROR <br />
    **Content:** `{ bat request }`


**Indexation**
----
  Delete an ontology from id

* **URL**

  /delete_onto

* **Method:**

  `DELETE`
  
*  **BODY**

    None
   
  
 


* **Data Params**

   **Required:** `{
           "id":"file_to_delete"
        }`
     


* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `ok`
 
* **Error Response:**

  * **Code:** 500 INTERNAL ERROR <br />
    **Content:** `{ bat request }`



**Annotation**
----
 When you have added an ontology, you can make an annotation by indicating the ontology id and the document to annotate 

* **URL**

  /annotation_id

* **Method:**

  `GET`
  
*  **BODY**

  None

  * **Data Params**

   **Required:** 
   ```
        {
          "id": "id of ontology",
          "document":"text doc"
        }
        
  ```



* **Success Response:**

  * **Code:** 201 <br />
    **Content:**  
    ```  
      {
         "text": "annotated text",
         "concepts_labels":[
          {
            "startNode": 0,
            "endNode": 14,
            "label": "HockeySurGlace",
            "concept": "HockeySurGlace"
          }
          ...
        ]
      }
    ```
 
* **Error Response:**

  * **Code:** 500 INTERNAL ERROR <br />
    **Content:** `{ bat request }`


#### Description of the params ####
 * **id** : id you ontology file to use for annotation

 * **document** : Text of the document to be annotated 

**When you make an annotation, the labels in the annotated text having the concepts in the ontology are in the  \<strong>**


 

For more information about this api, you can read our [article](https://duckduckgo.com) about semantic document annotation.
