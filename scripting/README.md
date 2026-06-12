<<<<<<< HEAD
script.py inspects a Terraform plan (converted to JSON) and decides whether
terraform apply is safe to run automatically.

The python script is pushed to the new branch and working fine as expected.

Run the below command to see the output.
Command:
python .\scripting\script.py .\scripting\tfplan.json → APPLY ALLOWED
python .\scripting\script.py .\scripting\tfplan-1.json → APPLY BLOCKED
python .\scripting\script.py .\scripting\tfplan-2.json → APPLY BLOCKED

Exit codes

CodeMeaning 0 APPLY ALLOWED — safe to run terraform apply
CodeMeaning 1 APPLY BLOCKED — review the printed issue(s) first
CodeMeaning 2 Error reading or parsing the plan file
=======
# Assessment
>>>>>>> b66523a (Add local scripting files to the repository)
