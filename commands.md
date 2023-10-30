# To run program

Run using `python -m Runitup.main` from the main repo

# To run postgres in mac

brew services run postgresql

# To stop postgres in mac

brew services stop postgresql

# To Connect to the PostgreSQL server

psql postgres

# To get usernames

SELECT u.usename AS "User Name" FROM pg_catalog.pg_user u;
or
\du

# To get databases

\l

# To download the Terraform provider required to manage your resources

terraform init -upgrade

# Create a Terraform execution plan

terraform plan -out main.tfplan

# To apply the execution plan to your cloud infrastructure

terraform apply main.tfplan

# To delete resources

terraform plan -destroy -out main.destroy.tfplan # Creates an execution plan
terraform apply main.destroy.tfplan # Destorys resources

# To get Azure resource group name

resource_group_name=$(terraform output -raw resource_group_name)
az vm list --resource-group $resource_group_name --query "[].{\"VM Name\":name}" -o table

# Exporting keys at once

Create a file named .env containing:
`export ARM_CLIENT_ID="xxx" <appID>
export ARM_CLIENT_SECRET="xxx" <Password>`

# Source the file and create environment variables

source .env

# To ssh into VM

chmod 400 secureadmin_id_rsa.pem
ssh -i secureadmin_id_rsa.pem azureadmin@ip
