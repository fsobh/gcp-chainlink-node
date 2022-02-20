## [0] Requirements
(1) GCP account with project created

(2) Chainlink node GUI accessible at http://localhost:6688 or https://localhost:6689

## [1] Creating an external adapter for ETHUSD with failover for API providers
Within the GCP GUI, navigate to the hamburger menu button, Serverless category, and finally Cloud Functions.

### 1.1 Create External Adapter
Create ```function```, choose a ```function name```, ```region``` close to or on the same region of your Chainlink Node VM, and ```allow unauthenticated invocations```, ```save``` and then ```next```. 

![154829213-018dfaac-056d-4a24-b071-53e2d6ea4371](https://user-images.githubusercontent.com/100059207/154830706-5a9ea23d-544a-4b98-a422-728794baabe7.png)


Copy the ```URL``` reserved for this external adapter. This will be used to test the external adapter after creation.

### 1.2 Deploy External Adapter Source Code
In ```Runtime``` field, choose ```Python 3.7```, ```Entry point``` field is ```gcp_cfn_handler``` which can be found within the python-script.py.

Replace the pre-loaded in ```main.py``` code with the contents of ```ethusd-coingecko-failover-coinpaprika-EA.py``` or choose to upload the ```ethusd-coingecko-failover-coinpaprika-EA.py``` via zip upload, and ```deploy``` the function.

![image](https://user-images.githubusercontent.com/100059207/154829312-011459ff-e11a-434f-a4e3-4cf7c355294d.png)

### 1.3 Test the deployed cloud function
Test the newly deployed external adapter through GCP serverless cloud functions by going to a terminal CLI:
```
curl -X POST "<http://cloud-function-url>" -H "Content-Type:application/json" --data '{ "id" : 653 }' -w "\n"
```
Expected output
```
>>{"jobRunID": 653, "data": {"base asset": "ETH", "quote asset": "USD", "price": "2935.86"}, "statusCode": 200}
```
## [2] Adding external adapter to Chainlink Node as a bridge

### 2.1 Create new bridge
Enter a ```name``` for the new bridge, and the associated GCP serverless cloud function generated http URL: ```<http://cloud-function-url>```

![image](https://user-images.githubusercontent.com/100059207/154829902-ad43f4f5-75e4-4f01-90fe-21a70200ed22.png)

## [3] Test Chainlink Node bridge with webhook job
The following instructions are for integration and testing on a chainlink node running ```v1.1.0.``` using job coding format of toml only.
Testing the bridge does not require capital resources or an oracle contract deployed and linked to the chainlink node testing the deployed bridge with associated external adapter.

### 3.1 Create new job
Paste the code below into the Job Spec TOML blob field in the chainlink node new job GUI, and create the job
```
type = "webhook"
schemaVersion = 1
name = "ethusd-coingecko-failover-cryptocompare-adapter"
observationSource = """
fetch_1       [type=bridge name="coingecko-ethusd-failover-coinpaprika-adapter" requestData="{\\"id\\": $(jobSpec.externalJobID)}"]
parse_1       [type=jsonparse path="data,price" data="$(fetch_1)"]

fetch_1 -> parse_1
"""
```


### 3.2 Confirm job run and job run output
Navigate to the ```Jobs``` tab, find the newly created job by the name, open the job to see its ```overview``` and ```defintion``` (TOML job spec).

```Run``` the job in the upper left hand corner of the chainlink node GUI

![image](https://user-images.githubusercontent.com/100059207/154830293-67735643-9b3d-4c1c-bfc3-0382370b6863.png)

### References
(1) https://docs.chain.link/docs/developers/

(2) https://docs.chain.link/docs/node-operators/

(3) https://docs.chain.link/docs/jobs/types/webhook/
