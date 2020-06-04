# AWS Savings Plans Price Data
Outputs to AWS Savings Plans Data to Microsoft Excel based on region, OS, tenancy and term parameters

### main.py
Parameters
```sh
CSVFILE = 'savings-plans.xlsx'
REGIONS = ['eu-west-1', 'eu-west-2']
TYPES = ['Windows', 'RHEL', 'Linux']
SPPRICES = ['1YALL', '1YNO', '3YALL', '3YNO']  # add 1YPA and 3YPA for partials
TENANCY = ['Shared', 'Dedicated']
```

### Requirements
```sh
pip install -p requirements.txt
```

### Execution 
```sh
python3 .\main.py
```
