all: clean init validate build-dev build-prod 
all-dev: clean init validate build-dev
all-prod: clean init validate build-prod

clean:
	@echo clean
	cd infrastructure && rm -rf .terraform 
	cd infrastructure && rm -rf  terraform.tfstate.d
	cd infrastructure && rm  -f .terraform.lock.hcl   ftprod_plan ftdev_plan

init:
	@echo Initializing the terraform project Acme, please wait...
	cd infrastructure && terraform init

validate:
	@echo code validation......
	cd infrastructure && terraform validate	
	
build-dev:
	@echo creation workspace and resource for Dev.....
	cd infrastructure && terraform workspace new dev
	cd infrastructure && terraform plan -out=ftdev_plan -var 'env=dev'
	cd infrastructure && terraform apply "ftdev_plan"

build-prod:
	@echo creation workspace and resource for Prod.....
	cd infrastructure && terraform workspace new prod
	cd infrastructure && terraform plan -out=ftprod_plan -var 'env=prod'
	@echo "Are you sure to apply?: "; \
	read YES; \
	cd infrastructure && terraform apply "ftprod_plan" 

destroy: 
	@echo tearing down the entire terraform deployment dev....
	cd infrastructure &&  terraform workspace select dev
	cd infrastructure &&  terraform destroy -var 'env=dev' --auto-approve

	@echo tearing down the entire terraform deploymennt prod...
    
	cd infrastructure && terraform workspace select prod
	cd infrastructure && terraform destroy -var "env=prod" --auto-approve	