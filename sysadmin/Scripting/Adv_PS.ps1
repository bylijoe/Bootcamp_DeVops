#crear masivamente usuarios en AD

import-csv -path $UsersFilePath | foreach {

$Name = ($_.GivenName + " " + $_.LastName)
$UserPrincipalName = ($_.SamAccountName + ”@yourdomain.com”)
$UserPassword = Get-Random -maximum 20000 -Minimum 100
$UserPassword = "@" + "user" + $UserPassword.ToString()
#Create user in Students OU

new-aduser -name $Name -enabled $true -GivenName $_.GivenName –surname $_.lastName -accountpassword (convertto-securestring $UserPassword -asplaintext -force) -changepasswordatlogon $true -samaccountname $_.SamAccountName –userprincipalname $UserPrincipalName -EmailAddress $_.EmailAddress -Path 'OU=Students,DC=yourdomain,DC=com' -ErrorAction Stop

$WCEmailContent = Format-Email -WCEmailContent (Get-Content $WCEmailFile) -UserPrinciPalName $UserPrincipalName -UserPassword $UserPassword

Send-Email -Email $_.EmailAddress -Credential $Credential -WCEmailContent $WCEmailContent

Write-Host "User Created: $Name"
}

#Listar usuarios de AD
Get-ADuser -Filter * | Export-Csv -Path C:\data\ADusers.csv

# Listar usuarios locales
$computers = Get-Content -Path C:\data\computers.txt Get-WmiObject -ComputerName $computers -Class Win32_UserAccount -Filter "LocalAccount='True'" |
Select PSComputername, Name, Status, Disabled, AccountType, Lockout, PasswordRequired, PasswordChangeable, SID | Export-csv C:\data\local_users.csv -NoTypeInformation