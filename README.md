# mohit-namdeo-ds-ca-assignment

Welcome! This repository documents the steps I followed to install a Directory Server (DS) and Certificate Authority (CA) using Dogtag PKI on a Fedora VM. Additionally, I've included a Python script to automate certificate requests and approvals.

## Prerequisites

## Install Required Packages
To begin the setup, I installed the necessary packages for 389 Directory Server (DS) and Dogtag PKI using the following command:

```bash
sudo apt install 389-ds-base dogtag-pki
```

This installs both the 389 Directory Server for LDAP management and Dogtag PKI for certificate authority management.

Before getting started, I ensured that my environment was ready with the following:

- A Fedora VM
- Root or sudo access to the system
- An active internet connection to install the required packages

## Set Up an LDAP Server (Creating DS Instance)

I configured an LDAP server by setting up a Directory Server (DS) instance. I used the 389-ds-base package for this purpose. Below are the steps I followed:

## DS Configuration

To create a DS instance, I started by generating a DS configuration file (ds.inf) and customized it for my setup.

Generate a DS Configuration File:

I used the following command to create a template configuration file:
``` bash
dscreate create-template ds.inf
```

Customize the DS Configuration File:

I modified the ds.inf file to include specific parameters, such as the instance name, root password, suffix, and self-signing options. Here’s how I customized the file:
```
sed -i \
    -e "s/;instance_name = .*/instance_name = localhost/g" \
    -e "s/;root_password = .*/root_password = Secret.123/g" \
    -e "s/;suffix = .*/suffix = dc=example,dc=com/g" \
    -e "s/;create_suffix_entry = .*/create_suffix_entry = True/g" \
    -e "s/;self_sign_cert = .*/self_sign_cert = False/g" \
    ds.inf
instance_name: Specifies the name of the DS instance. In this case, I set it to localhost.
root_password: This sets the password for the DS admin user (cn=Directory Manager). I used Secret.123 as the password.
suffix: Defines the namespace for the DS instance. I set it to dc=example,dc=com.
self_sign_cert: Indicates whether to create self-signed certificates for SSL connections. I set it to False as SSL can be enabled after installation.
You can review other parameters in the configuration file (ds.inf) or refer to the DS documentation for additional details.
```

Create the DS Instance:

After customizing the configuration file, I created the DS instance using the following command:

``` bash
dscreate from-file ds.inf
```

## Starting and Enabling the Directory Server
Once the DS instance was created, I started the Directory Server and ensured that it would automatically start on boot:
Start the Directory Server:
I used the following command to start the DS service:
```bash
sudo systemctl start dirsrv@localhost
```
Enable the Directory Server to Start on Boot:

To make sure the Directory Server would start automatically on boot, I ran:

```bash
sudo systemctl enable dirsrv@localhost
```

## CA Configuration - Set Up a CA Server (Creating PKI Subsystems)

After setting up the Directory Server, I moved on to configuring the CA server using Dogtag PKI:
Create a CA Instance: I created a CA instance using the following command:
```bash
sudo pkispawn
```
Configure the CA: Like the DS setup, I followed the configuration prompts, such as setting the admin password.
## Start the CA Service
I started the CA service to ensure it was up and running:
``` bash
sudo systemctl status pki-tomcatd@pki-tomcat.service
```
Enable CA to Start on Boot: I enabled the CA service to start automatically on boot:
```bash
sudo systemctl enable pki-tomcatd@pki-tomcat.service
```


## Automating Certificate Requests and Approvals with Python

To simplify the process, I created a Python script that automates the steps of requesting and approving certificates.

Here's the Python script I wrote, which automates the import of the admin certificate, requesting a new certificate, and approving it:

``` bash
import subprocess
import getpass

# Configuration
PKCS12_PATH = '/root/.dogtag/pki-tomcat/ca_admin_cert.p12'
ALIAS_PATH = '~/.dogtag/pki-tomcat/ca/alias'
PASSWORD = 'Secret.123'
USER_NAME = 'mohitnamdeo'
CERT_NICKNAME = 'PKI Administrator for asc-Latitude-3550'

def run_command(command, check=True):
    """Executes a command and returns its output."""
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if check and result.returncode != 0:
        print(f"Error running command: {result.stderr.strip()}")
        exit(1)
    return result.stdout.strip()

def import_pkcs12():
    """Import PKCS#12 file."""
    command = f"sudo pk12util -i {PKCS12_PATH} -d {ALIAS_PATH} -K {PASSWORD}"
    print("Importing PKCS#12 file...")
    output = run_command(command)
    print(output)

def list_certificates():
    """List certificates."""
    command = f"sudo certutil -L -d {ALIAS_PATH}"
    print("Listing certificates...")
    output = run_command(command)
    print(output)

def create_certificate_request():
    """Create a certificate request."""
    command = f"pki -d {ALIAS_PATH} -c {PASSWORD} -n '{CERT_NICKNAME}' client-cert-request uid={USER_NAME}"
    print(f"Requesting certificate for user: {USER_NAME}...")
    output = run_command(command)
    print(output)
    return output.split("Request ID: ")[1].split()[0]  # Extract request ID

def approve_certificate_request(request_id):
    """Approve the certificate request."""
    command = f"pki -d {ALIAS_PATH} -c {PASSWORD} -n '{CERT_NICKNAME}' ca-cert-request-approve {request_id}"
    print(f"Approving certificate request with ID: {request_id}...")
    output = run_command(command)
    print(output)

def main():
    import_pkcs12()
    list_certificates()
    
    request_id = create_certificate_request()
    approve_certificate_request(request_id)

if __name__ == "__main__":
    main()
```

## Manual Certificate Request and Approval
With the CA server running, I proceeded to create and approve a certificate request:

- Import the Admin Certificate: I imported the admin certificate from the .p12 file using pk12util:

```bash
sudo pk12util -i /root/.dogtag/pki-tomcat/ca_admin_cert.p12 -d ~/.dogtag/pki-tomcat/ca/alias -K Secret.123
```
- Verify Certificate Import: I verified that the certificate was successfully imported:

```bash
sudo certutil -L -d ~/.dogtag/pki-tomcat/ca/alias
```

- Create a Certificate Request: I used the following command to create a certificate request:
```bash
pki -d ~/.dogtag/pki-tomcat/ca/alias -c Secret.123 -n "PKI Administrator for myCAInstance" client-cert-request uid=mohitnamdeo
```
The output provided me with the request ID, and the operation was marked as successful:
```bash
Request ID: 15
Type: enrollment
Request Status: pending
Operation Result: success
```
- Approve the Certificate Request: Once the request was generated, I manually reviewed and approved it with the following command:

```bash
pki -d ~/.dogtag/pki-tomcat/ca/alias -c Secret.123 -n "PKI Administrator for myCAInstance" ca-cert-request-approve 9
```
The request was successfully approved:

```bash
Request ID: 15
Type: enrollment
Request Status: complete
Operation Result: success
Certificate ID: 0xB
```

## Contact

If you have any questions, suggestions, or need assistance related to the CMS-Server, feel free to reach out to Me.

- MailId - namdeomohit198@gmail.com
- Mob No. - 9131552292
- Portfolio: [https://itsmohitnamdeo.github.io](https://itsmohitnamdeo.github.io)
- Linkedin: [https://www.linkedin.com/in/mohit-namdeo](https://www.linkedin.com/in/mohit-namdeo)
