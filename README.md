1. Authenticate with your AWS account using CLI. You should have root privileges
2. Run setup.sh, which will get you set up with the necessary resources.
3. In template.yaml, you will set up the infrastructure needed.
4. Use deploy_stack.sh to deploy any resources declared in template.yaml. 
5. In collate.sh, execute the Lambda, download the csv files to a temp folder, and collate them.

