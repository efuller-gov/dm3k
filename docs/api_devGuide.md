# API Development Guide #

The API contains two endpoints used to access the back-end and optimizer for Open-DM3K.  These endpoints are described below.

> NOTE: the URL for the API is based on where you established the project docker containers.  The system is available on **port 80** of whatever IP or URL the server you started the docker containers on.

## GET /api/version ##

Presents a simple endpoint to check aliveness and the API version

* **URL**: /api/version
* **METHODS**: `GET`
* **URL Params**: None
* **Data Params**: None
* **Success Response**: 
  * **Code**: 200
  * **Content**: `{'api_version': "1.0"}`
* **Error Response**: None
* **Sample Call**:

    ```python
        import requests
        version_url = URL + '/api/version'   # URL is where you established the docker containers
        response = requests.get(version_url)
    ```

## POST /api/vizdata ##

The Main endpoint to provide visual data to the optimizer.  The response is the results of the optimizer on the problem that was posted.

* **URL**: /api/vizdata
* **METHODS**: `POST`
* **URL Params**: None
* **Data Params**:  *See Expected Data Params Below*
* **Success Response**:
  * **Code**: 200
  * **Content**: *See Expected Success Response Below*
* **Error Response**:
  * **Code**: 400 [Validation Errors]
  * **Content**: *See Validation Error Response Below*
* **Sample Call**:
    python
    ```python
        import os
        import json
        import requests

        version_url = URL + '/api/vizdata'   # URL is where you established the docker containers

        app_directory = "<path to open-dm3k top folder>"  # insert your path to top folder
        
        # load up an example file
        path_to_file = os.path.join(app_directory, "examples", "simpleKnapsack.json")
        with open(path_to_file, "r") as f:
            input_dict = json.load(f)

        # for now, add algorithm = KnapsackViz
        input_dict["algorithm"] = "KnapsackViz"

        # send the POST
        response = requests.post(vizinput_url, json=input_dict)
    ```

### Expected Data Params ###

In order for the optimizer to run, it requires the definition of a problem to solve.  

In order to define a problem you need to define: the resource classes, the activity classes, the resource instances, the activity instances, the allocation instances, the contains instances, and the allocation constraints.  For more detail on these terms see */docs/resource_allocation_101.md*

> NOTE - see */examples* folder for a series of different examples of the expected data params

The expected data params for the POST /api/vizdata endpoint include a single JSON object with the following attributes:

* *datasetName*:  string name of the data set that you are posting
* *files*: the list of files that represent this data set. (Typically only 1 file), where each file is a JSON object with the following attributes:
  * *fileName*: string name of the file
  * *fileContents*: a JSON object with the following attrbutes:
    * *resourceClasses*: a list of JSON objects, where each JSON object represents a resource class and consists of the following attributes:
      * *className*: string name of the class
      * *budgets*: a list of strings representing one or more budget types for this class
      * *containsClasses*: a list of strings of other resource *className*s that are contained by this class
      * *canBeAllocatedToClasses*: a list of strings of other activity *className*s that this resource class can be allocated to
    * *activityClasses*: a list of JSON objects, where each JSON object represents a activity class and has the following attributes:
      * *className*: string name of the class
      * *rewards*: a list of strings representing one or more reward types for this class
      * *costs*: a list of strings representing one or more costs for this class. Costs are expressed as a budget type.
      * *containsClasses*: a list of strings of other activity *className*s that are contained by this class
    * *resouceInstances*: a list of JSON objects, where each JSON object represents an instance of a *resourceClass*.  A resourceInstance has the following attributes:
      * *className*: the string name of the resource class that this is an instance of
      * *instanceTable*: a list of JSON objects where each JSON object represents an instance of the resource class and has the following attributes:
        * *instanceName*: the string name of the instance
        * *budget*: the value of each budget of the resource for this instance
    * *activityInstances*: a list of JSON objects, where each JSON object represents an instance of a *activityClass*.  A activityInstance has the following attributes:
      * *className*: the string name of the activity class that this is an instance of
      * *instanceTable*: a list of JSON objects where each JSON object represents an instance of the activity class and has the following attributes:
        * *instanceName*: the string name of the instance
        * *cost*: the cost value of this activity for each budget type
        * *reward*: the reward value of selecting this activity
    * *allocationInstances*: a list of JSON objects which establish which specific *resourceInstances* are available to be allocated to which specific *activityInstances*.  Each allocationInstance has the following attributes:
      * *resourceClassName*: which resource class does this allocation instance start at
      * *activityClassName*: which activity class does this allocation instance end at
      * *instanceTable*: a list of JSON objects where each JSON object represents an allocation of a specific resource instance to a specific activity instance and has the following attributes:
        * *resourceInstanceName*: can be "ALL" or the *instanceName* of the resource Instance.  Where "ALL" means all instances of the *resourceClassName*
        * *activityInstanceName*: can be "ALL" or the *instanceName* of the activity Instance.  Where "ALL" means all instances of the *activityClassName*
    * *containsInstances*: TODO
    * *allocationConstraints*: TODO

Example:

```json
{
    "datasetName": "simpleKnapsack",
    "files": [
    {
        "fileName": "simpleKnapsack.json",
        "fileContents": {
            "resourceClasses": [
                {"className": "backpack",
                    "loc": 100,
                    "locY": 0,
                    "typeName": "computer",
                    "budgets": ["space"],
                    "containsClasses": [],
                    "canBeAllocatedToClasses": ["item"]}],
            "activityClasses": [
                {"className": "item",
                    "locX": 550,
                    "locY": 0,
                    "typeName": "product",
                    "rewards": ["money"],
                    "costs": ["space"],
                    "containsClasses": [],
                    "allocatedWhen": {}
                    }
            ],
            "resourceInstances": [
                {"className": "backpack",
                    "instanceTable": [
                    {"instanceName": "backpack_Resource_instance_0",
                        "budget": {
                            "space": 1
                        }
                    }
                    ]
                }
            ],
            "activityInstances": [
                {"className": "item",
                    "instanceTable": [
                    {"instanceName": "item_Activity_instance_0",
                        "cost": {
                            "space": 1
                        },
                        "reward": 1}
                    ]
                }
            ],
            "allocationInstances": [
                {"resourceClassName": "backpack",
                    "activityClassName": "item",
                    "instanceTable": [
                    {"resourceInstanceName": "ALL",
                        "activityInstanceName": "ALL"
                    }
                    ]
                }
            ],
            "containsInstances": [],
            "allocationConstraints": []
        }
    }]
}
```


### Expected Success Response ###

### Validation Error Response ###
