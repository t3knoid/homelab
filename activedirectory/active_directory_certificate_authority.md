# Active Directory Certificate Services

## Step 1: Install the AD CS Role
First, you need to install the AD CS role and management tools:

### Install the AD CS role and management tools

```powershell
Install-WindowsFeature -Name ADCS-Cert-Authority -IncludeManagementTools
```

## Step 2: Install the AD CS Role Services

### Install the Certification Authority service

Next, install the necessary AD CS role services. For a typical Certification Authority (CA), you might want to include:

- Certification Authority
- Certification Authority Web Enrollment (if needed)

```powershell
Install-WindowsFeature ADCS-Cert-Authority -IncludeManagementTools
```

### (Optional) Install the Certification Authority Web Enrollment service
```powershell
Install-WindowsFeature ADCS-Web-Enrollment
```

## Step 3: Configure the Certification Authority
After installing the necessary role services, you need to configure the Certification Authority.

### Define the Configuration Parameters:

- CA Type: EnterpriseRootCA or StandaloneRootCA
- Common Name: Name of the CA
- Validity Period: Validity period for the CA certificate

```powershell
# Define the configuration parameters
$CAType = "EnterpriseRootCA"
$CACommonName = "RefolCA"
$ValidityPeriod = 5
$ValidityPeriodUnits = 4
```

### Install the Certification Authority

Install and configure the Certification Authority using the **Install-AdcsCertificationAuthority** cmdlet

```powershell
Install-AdcsCertificationAuthority -CAType $CAType -CACommonName $CACommonName -KeyLength 2048 -ValidityPeriod $ValidityPeriod -ValidityPeriodUnits $ValidityPeriodUnits
```

## Full PowerShell Script

```powershell
# Step 1: Install the AD CS role and management tools
Install-WindowsFeature -Name ADCS-Cert-Authority -IncludeManagementTools

# Step 2: Install the Certification Authority service
Install-WindowsFeature ADCS-Cert-Authority -IncludeManagementTools

# (Optional) Install the Certification Authority Web Enrollment service
Install-WindowsFeature ADCS-Web-Enrollment

# Step 3: Configure the Certification Authority
# Define the configuration parameters
$CAType = "EnterpriseRootCA"
$CACommonName = "MyCA"
$ValidityPeriod = 5
$ValidityPeriodUnits = 4

# Install and configure the Certification Authority
Install-AdcsCertificationAuthority -CAType $CAType -CACommonName $CACommonName -KeyLength 2048 -ValidityPeriod $ValidityPeriod -ValidityPeriodUnits $ValidityPeriodUnits
```
