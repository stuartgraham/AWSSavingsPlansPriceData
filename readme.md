# AWS Savings Plans Price Data
Outputs AWS Savings Plans Data to Microsoft Excel based on region, OS, tenancy and term parameters

### main.py
Manipulate settings as needed

| Settings | Description | Inputs |
| :----: | --- | --- |
| `CSVFILE` | xlsx file name | `savings-plans.xlsx` |
| `CSV_PER_TAB` | Per Instance Family price tabs | `True/False` |
| `LOOKUP_CODE` | Concatenated code for VLOOKUP | `True/False` |
| `PLANLENGTH` | Savings Plans Years | `[1,3]` |
| `PLANCOMMIT` | Commitment [A]ll, [N]o, [P]artial Upfront | `['A','N','P']` |
| `REGIONS` | AWS Region code | `['eu-west-1', 'eu-west-2']` |
| `TYPES` | Operating System type | `['Windows', 'RHEL', 'Linux', SUSE]` |
| `TENANCY` | AWS Tenancy | `['Shared', 'Dedicated']` |


### Requirements
```sh
pip install -p requirements.txt
```

### Execution 
```sh
python3 .\main.py
```
