all: clean init validate build-dev build-prod 
all-dev: clean init validate build-dev
all-prod: clean init validate build-prod

clean:
	@echo clean...
	cd infra && rm -rf .terraform 
	cd infra && rm -f .terraform.lock.hcl  terraform.tfstate.backup 
	cd infra && rm -f dev.tfstate dev.tfstate.backup 
	cd infra && rm -f prod.tfstate prod.tfstate.backup 


init:
	@echo Initializing the Acme project, please wait...
	cd infra && terraform init

validate:
	@echo validating the code...
	cd infra && terraform validate

build-dev:
	@echo Generating an executinon build dev, please wait...
	cd infra &&  terraform plan  
	cd infra &&  terraform apply -var-file="env-dev/tf-dev.tfvars"  -state-out=dev.tfstate  --auto-approve

build-prod: 
	@echo "Are you sure to deploy?: "; \
	read YES; \
	
	@echo Generating an executinon build prod, please wait...
	cd infra &&  terraform plan  
	cd infra &&  terraform apply -var-file="env-prod/tf-prod.tfvars" -state-out=prod.tfstate --auto-approve
	
destroy-dev: 
	@echo tearing down the Acme deployment dev...
	cd infra && terraform destroy -state=dev.tfstate --auto-approve
	
destroy-prod:
	@echo teraing down the Acme deployment prod...	
	cd infra && terraform destroy -state=prod.tfstate --auto-approve
	