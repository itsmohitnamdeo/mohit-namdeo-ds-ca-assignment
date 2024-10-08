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
