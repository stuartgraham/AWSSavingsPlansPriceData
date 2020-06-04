# AWS Savings Plans Price Data
Outputs AWS Savings Plans Data to Microsoft Excel based on region, OS, tenancy and term parameters

### main.py
Parameters
```sh
CSVFILE = 'savings-plans.xlsx'
CSV_PER_TAB = False
PLANLENGTH = [1,3]                              # 1 year, 3 years
PLANCOMMIT = ['A','N']                          # [A]ll Upfront, [N]o Upfront, [P]artial Upfront
REGIONS = ['eu-west-1', 'eu-west-2']
TYPES = ['Windows', 'RHEL', 'Linux']
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
