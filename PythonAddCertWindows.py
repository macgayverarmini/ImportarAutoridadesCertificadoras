import zipfile
import os
import shutil
import glob
import subprocess, sys
import urllib.request

arquivo_certs_zip = "http://acraiz.icpbrasil.gov.br/credenciadas/CertificadosAC-ICP-Brasil/ACcompactado.zip"
pasta_temp = "c:\\programdata\\PythonAddCertWindows\\rbf\\"
filetemp = "download.zip"

def powershell_rulescript(insecure):
    #define conteúdo do arquivo do registro.
    sregcomand1 = ('reg add HKLM\\SOFTWARE\\Microsoft\\PowerShell\\1\\ShellIds\\Microsoft.PowerShell /v "ExecutionPolicy" /d "%s" /f')
    sregcomand2 = ('reg add HKLM\\SOFTWARE\\Microsoft\\PowerShell\\1\\ShellIds\\ScriptedDiagnostics /v "ExecutionPolicy" /d "%s" /f')
    if insecure:
        sregcomand1 = sregcomand1 % ('Unrestricted')
        sregcomand2 = sregcomand2 % ('Unrestricted')
    else:
        sregcomand1 = sregcomand1 % ('RemoteSigned')
        sregcomand2 = sregcomand2 % ('RemoteSigned')
    
    #escrevendo o BAT para fazer um bypass na segurança do windows.
    batstr = '@echo off\n' + sregcomand1 + ' /reg:32\n' + sregcomand2 + ' /reg:32\n' + sregcomand1 + ' /reg:64\n' + sregcomand2 + ' /reg:64\n'
    batfilename = pasta_temp + "allowpsscript.bat"
    bat = open(batfilename, 'w')
    bat.write(batstr)
    bat.close()

    #executa a alteração do registro silenciosamente.
    console1 = subprocess.Popen([batfilename], stdout=sys.stdout)
    console1.communicate() 
  
def ps_script_ca(cafile, root):
    if root:
        store = "Root"
    else:
        store = "CA"

    cmd = "Import-Certificate -FilePath " + cafile + " -CertStoreLocation Cert:\\CurrentUser\\" + store + "\n"
    return cmd 

#criando pasta
if not os.path.exists(pasta_temp):
    os.makedirs(pasta_temp)
#baixando arquivo
if not os.path.exists(pasta_temp + filetemp):
    urllib.request.urlretrieve(arquivo_certs_zip, pasta_temp + filetemp )
    #extrai os arquivos do Zip
    with zipfile.ZipFile(pasta_temp + filetemp) as zip_ref:
        zip_ref.extractall(pasta_temp)
# listando arquivos root
root_certs = glob.glob(pasta_temp + "*ICP-Brasil*")
# listando demais arquivos
ca_certs = glob.glob(pasta_temp + "*.crt")
# removendo root dos demais arquivos
ca_certs = [x for x in ca_certs if x not in root_certs]
# escrevendo script 
ps_file_name = pasta_temp + "certificate_add.ps1"
ps_file = open(ps_file_name, "w")
for root in root_certs:
    ps_file.write(ps_script_ca(root, True))
for ca in ca_certs:
    ps_file.write(ps_script_ca(ca, False))
ps_file.close()
# permissão para o powershell executar scripts
powershell_rulescript(True)
# executando o script
console = subprocess.Popen(["powershell", ps_file_name], stdout=sys.stdout)
console.communicate()
# tornando o powershell seguro novamente.
powershell_rulescript(False)
# clear all files 
shutil.rmtree(pasta_temp)