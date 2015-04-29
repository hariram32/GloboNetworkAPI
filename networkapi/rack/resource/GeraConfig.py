#coding=utf-8
import pprint
from netaddr import *
import re
import os
from networkapi.rack.models import RackConfigError


#### HARDCODED - MUDA SEMPRE QE ATUALIZARMOS O SO DO TOR
KICKSTART_SO_LF="n6000-uk9-kickstart.7.1.0.N1.1b.bin"
IMAGE_SO_LF="n6000-uk9.7.1.0.N1.1b.bin"
#### <<<<<

PATH_TO_GUIDE = "/opt/app/GloboNetworkAPI/networkapi/rack/roteiros/"
PATH_TO_CONFIG = "/opt/app/GloboNetworkAPI/networkapi/rack/configuracao/"


#substitui key's do dicionario que aparecem em filein, pelos respectivos valores, gerando o arquivo fileout (o restante do arquivo é copiado)
def replace(filein,fileout, dicionario):
    try:
        # Read contents from file as a single string
        file_handle = open(filein, 'r')
        file_string = file_handle.read()
        file_handle.close()
        #
        for key in dicionario:
        # Use RE package to allow for replacement (also allowing for (multiline) REGEX)
            file_string = (re.sub(key, dicionario[key], file_string))
    
        # Write contents to file.
        # Using mode 'w' truncates the file.
        file_handle = open(fileout, 'w')
        file_handle.write(file_string)
        file_handle.close()
    except:
        raise RackConfigError(None,None, "Erro no template.")

#divide a rede net em n subredes /bloco e retorna a subrede n
def splitnetworkbyrack(net,bloco,posicao):
    subnets=list(net.subnet(bloco))
    return subnets[posicao]

def dic_vlan_core(variablestochangecore, rack, name_core, name_rack): 
    """
    variablestochangecore: list
    rack: Numero do Rack
    name_core: Nome do Core
    name_rack: Nome do rack
    """
 
    core = int(name_core.split("-")[2])

    #valor base para as vlans e portchannels 
    BASE_SO = 1000

    #variavels para manipular as redes
    SO_OOB_NETipv4 = {}
    subSO_OOB_NETipv4={}

    #rede para conectar cores aos racks
    SO_OOB_NETipv4= IPNetwork('10.143.64.0/18') 

    #Vlan para cadastrar
    variablestochangecore["VLAN_NAME"]="VLAN_SO"+"_"+name_rack 
    variablestochangecore["VLAN_NUM"]=str(BASE_SO+rack) 

    #Rede para cadastrar  
    subSO_OOB_NETipv4=list(SO_OOB_NETipv4.subnet(25)) 
    variablestochangecore["REDE_IP"]=str(subSO_OOB_NETipv4[rack]).split("/")[0]
    variablestochangecore["REDE_MASK"]=str(subSO_OOB_NETipv4[rack].prefixlen)
    variablestochangecore["NETMASK"]=str(subSO_OOB_NETipv4[rack].netmask)
    variablestochangecore["BROADCAST"]=str(subSO_OOB_NETipv4[rack].broadcast)
                 
    #cadastro ip 
    ip = 124 + core
    variablestochangecore["EQUIP_NAME"]=name_core 
    variablestochangecore["IPCORE"]=str(subSO_OOB_NETipv4[rack][ip])

    #ja cadastrado
    variablestochangecore["IPHSRP"]=str(subSO_OOB_NETipv4[rack][1]) 
    variablestochangecore["NUM_CHANNEL"]=str(BASE_SO+rack)
    
    return variablestochangecore
    

def dic_lf_spn(user, rack):

    BASE_RACK = 120
    BASE_AS = 65000

    VLANBE = 2000
    VLANFE = 2480
    VLANBORDA = 2960
    VLANBORDACACHOS = 3440

    CIDREBGP = {}
    CIDRBE = {}
    ########
    VLANBELEAF = {}
    VLANFELEAF = {}
    VLANBORDALEAF = {}
    VLANBORDACACHOSLEAF = {}
    ########
    VLANBELEAF[rack]=[]
    VLANFELEAF[rack]=[]
    VLANBORDALEAF[rack]=[]
    VLANBORDACACHOSLEAF[rack]=[]

    #CIDR sala 01 => 10.128.0.0/12
    CIDRBE[0] = IPNetwork('10.128.0.0/12')
    CIDREBGP[0] = IPNetwork('10.10.0.0/22')

    SPINE1ipv4 = IPNetwork('10.0.0.0/24')
    SPINE2ipv4 = IPNetwork('10.0.1.0/24')
    SPINE3ipv4 = IPNetwork('10.0.2.0/24')
    SPINE4ipv4 = IPNetwork('10.0.3.0/24')
    #REDE subSPINE1ipv4[rack]
    subSPINE1ipv4=list(SPINE1ipv4.subnet(31))
    subSPINE2ipv4=list(SPINE2ipv4.subnet(31))
    subSPINE3ipv4=list(SPINE3ipv4.subnet(31))
    subSPINE4ipv4=list(SPINE4ipv4.subnet(31))

    #Vlans BE RANGE
    VLANBELEAF[rack].append(VLANBE+rack) 
    # rede subSPINE1ipv4[rack]
    VLANBELEAF[rack].append(VLANBE+rack+BASE_RACK)
    VLANBELEAF[rack].append(VLANBE+rack+2*BASE_RACK)
    VLANBELEAF[rack].append(VLANBE+rack+3*BASE_RACK)
    #Vlans FE RANGE
    VLANFELEAF[rack].append(VLANFE+rack)
    VLANFELEAF[rack].append(VLANFE+rack+BASE_RACK)
    VLANFELEAF[rack].append(VLANFE+rack+2*BASE_RACK)
    VLANFELEAF[rack].append(VLANFE+rack+3*BASE_RACK)
    #Vlans BORDA RANGE
    VLANBORDALEAF[rack].append(VLANBORDA+rack)
    VLANBORDALEAF[rack].append(VLANBORDA+rack+BASE_RACK)
    VLANBORDALEAF[rack].append(VLANBORDA+rack+2*BASE_RACK)
    VLANBORDALEAF[rack].append(VLANBORDA+rack+3*BASE_RACK)
    #Vlans BORDACACHOS RANGE
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS+rack)
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS+rack+BASE_RACK)
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS+rack+2*BASE_RACK)
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS+rack+3*BASE_RACK)

    ########### BD ############
    vlans = dict()
    vlans['VLANBELEAF'] = VLANBELEAF
    vlans['VLANFELEAF'] = VLANFELEAF
    vlans['VLANBORDALEAF'] = VLANBORDALEAF
    vlans['VLANBORDACACHOSLEAF'] = VLANBORDACACHOSLEAF
    vlans['BE'] = [VLANBE, VLANFE]
    vlans['FE'] = [VLANFE, VLANBORDA]
    vlans['BORDA'] = [VLANBORDA, VLANBORDACACHOS]
    vlans['BORDACACHOS'] = [VLANBORDACACHOS, 3921]

    redes = dict()
    redes['SPINE1ipv4'] = str(SPINE1ipv4)
    redes['SPINE2ipv4'] = str(SPINE2ipv4)
    redes['SPINE3ipv4'] = str(SPINE3ipv4)
    redes['SPINE4ipv4'] = str(SPINE4ipv4)
    
    return vlans, redes


def dic_pods(user, rack):

    CIDRBEipv4 = {}
    PODSBEipv4 = {}
    redesPODSBEipv4 = {}
    PODSBEFEipv4 = {}
    redesPODSBEFEipv4 = {}
    PODSBEBOipv4 = {}
    redesPODSBEBOipv4 = {}
    PODSBECAipv4 = {}
    redesPODSBECAipv4 = {}

    PODSBEipv4[rack]=[]
    redesPODSBEipv4[rack]=[]
    PODSBEFEipv4[rack]=[]
    redesPODSBEFEipv4[rack]=[]
    PODSBEBOipv4[rack]=[]
    redesPODSBEBOipv4[rack]=[]
    PODSBECAipv4[rack]=[]
    redesPODSBECAipv4[rack]=[]
 
    #CIDR sala 01 => 10.128.0.0/12
    CIDRBEipv4 = IPNetwork('10.128.0.0/12')
    CIDRBEipv6 = IPNetwork('fdbe:bebe:bedc::/48')


    #          ::::::: SUBNETING FOR RACK NETWORKS - /19 :::::::

    #Redes p/ rack => 10.128.0.0/19, 10.128.32.0/19 , ... ,10.143.224.0/19
    subnetsRackBEipv4[rack]=splitnetworkbyrack(CIDRBEipv4,19,rack)
    subnetsRackBEipv6[rack]=splitnetworkbyrack(CIDRBEipv6,55,rack)


    #PODS BE => /20 
    subnetteste=subnetsRackBEipv4[rack] 
    PODSBEipv4[rack]=splitnetworkbyrack(subnetteste,20,0) 
         # => 128 redes /27     # Vlan 2 a 129
    redesPODSBEipv4[rack] = list(PODSBEipv4[rack].subnet(27)) 
    #PODS BEFE => 10.128.16.0/21 
    PODSBEFEipv4[rack]=splitnetworkbyrack(splitnetworkbyrack(subnetteste,20,1),21,0)
         # => 64 redes /27    # Vlan 130 a 193
    redesPODSBEFEipv4[rack] = list(PODSBEFEipv4[rack].subnet(27))
    #PODS BEBO => 10.128.24.0/22
    PODSBEBOipv4[rack]=splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(subnetteste,20,1),21,1),22,0)
         # => 64 redes /28    # Vlan 194 a 257
    redesPODSBEBOipv4[rack]=list(PODSBEBOipv4[rack].subnet(28))
    #PODS BECA => 10.128.28.0/23
    PODSBECAipv4[rack]=splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(subnetteste,20,1),21,1),22,1),23,0)
         # => 32 redes /28    # Vlan 258 a 289
    redesPODSBECAipv4[rack]=list(PODSBECAipv4[rack].subnet(28))

    redes = dict()
    redes['BE_VLAN_MIN']= 2
    redes['BE_VLAN_MAX']= 129
    redes['BE_PREFIX']= str(redesPODSBEipv4[rack][0].prefixlen)
    redes['BE_REDE']= str(PODSBEipv4[rack])

    redes['BEFE_VLAN_MIN']= 130
    redes['BEFE_VLAN_MAX']= 193
    redes['BEFE_PREFIX']= str(redesPODSBEFEipv4[rack][0].prefixlen)
    redes['BEFE_REDE']= str(PODSBEFEipv4[rack])

    redes['BEBORDA_VLAN_MIN']= 194
    redes['BEBORDA_VLAN_MAX']= 257
    redes['BEBORDA_PREFIX']= str(redesPODSBEBOipv4[rack][0].prefixlen)
    redes['BEBORDA_REDE']= str(PODSBEBOipv4[rack])

    redes['BECACHOS_VLAN_MIN']= 258
    redes['BECACHOS_VLAN_MAX']= 289
    redes['BECACHOS_PREFIX']= str(redesPODSBECAipv4[rack][0].prefixlen)
    redes['BECACHOS_REDE']= str(PODSBECAipv4[rack])

    return redes


def dic_hosts_cloud(rack):

    subnetsRackBEipv4 = {}
    subnetsRackBEipv4[rack] = []
    redesHostsipv4={}
    redesHostsipv4[rack]=[]
    redeHostsBEipv4={}
    redeHostsBEipv4[rack]=[]
    redeHostsFEipv4={}
    redeHostsFEipv4[rack]=[]
    redeHostsBOipv4={}
    redeHostsBOipv4[rack]=[]
    redeHostsCAipv4={}
    redeHostsCAipv4[rack]=[]
    redeHostsFILERipv4={}
    redeHostsFILERipv4[rack]=[]


    #CIDR sala 01 => 10.128.0.0/12
    CIDRBEipv4 = IPNetwork('10.128.0.0/12')
    CIDRBEipv6 = IPNetwork('fdbe:bebe:bedc::/48')

    subnetsRackBEipv4[rack]=splitnetworkbyrack(CIDRBEipv4,19,rack) #10.128.32.0/19
    subnetteste=subnetsRackBEipv4[rack] #10.128.32.0/19

    #VLANS CLoud
    # ambiente BE - MNGT_NETWORK - RACK_AAXX
    # 10.128.30.0/23
    # vlans MNGT_BE/FE/BO/CA/FILER
        #PODS BE => /20 
    #Hosts => 10.128.30.0/23
    #IPNetwork('10.128.62.0/23')
    redesHostsipv4[rack]=splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(subnetteste,20,1),21,1),22,1),23,1)
    #Hosts BE => 10.128.30.0/24 => 256 endereços
    #IPNetwork('10.128.62.0/24')
    redeHostsBEipv4[rack]= splitnetworkbyrack(redesHostsipv4[rack],24,0)
    #Hosts FE => 10.128.31.0/25 => 128 endereços
    redeHostsFEipv4[rack] = splitnetworkbyrack(splitnetworkbyrack(redesHostsipv4[rack],24,1),25,0)
    #Hosts BO => 10.128.31.128/26 => 64 endereços
    redeHostsBOipv4[rack] = splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(redesHostsipv4[rack],24,1),25,1),26,0)
    #Hosts CA => 10.128.31.192/27 => 32 endereços
    redeHostsCAipv4[rack] = splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(redesHostsipv4[rack],24,1),25,1),26,1),27,0)
    #Hosts FILER => 10.128.15.224/27 => 32 endereços
    redeHostsFILERipv4[rack] = splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(redesHostsipv4[rack],24,1),25,1),26,1),27,1)       

    hosts=dict()
    BE=dict()
    FE=dict()
    BO=dict()
    CA= dict()
    FILER=dict()
    hosts['VLAN_MNGT_BE']=296
    hosts['VLAN_MNGT_FE']=297
    hosts['VLAN_MNGT_BO']=298
    hosts['VLAN_MNGT_CA']=299
    hosts['VLAN_MNGT_FILER']=300
    hosts['PREFIX']=str(redesHostsipv4[rack].prefixlen)
    hosts["REDE"]=str(redesHostsipv4[rack])
    BE['REDE_IP']=str(redeHostsBEipv4[rack].ip)
    BE['REDE_MASK']=redeHostsBEipv4[rack].prefixlen
    BE['NETMASK']=str(redeHostsBEipv4[rack].netmask)
    BE['BROADCAST']=str(redeHostsBEipv4[rack].broadcast)
    hosts['BE']=BE
    FE['REDE_IP']=str(redeHostsFEipv4[rack].ip)
    FE['REDE_MASK']=redeHostsFEipv4[rack].prefixlen
    FE['NETMASK']=str(redeHostsFEipv4[rack].netmask)
    FE['BROADCAST']=str(redeHostsFEipv4[rack].broadcast)
    hosts['FE']=FE
    BO['REDE_IP']=str(redeHostsBOipv4[rack].ip)
    BO['REDE_MASK']=redeHostsBOipv4[rack].prefixlen
    BO['NETMASK']=str(redeHostsBOipv4[rack].netmask)
    BO['BROADCAST']=str(redeHostsBOipv4[rack].broadcast)
    hosts['BO']=BO
    CA['REDE_IP']=str(redeHostsCAipv4[rack].ip)
    CA['REDE_MASK']=redeHostsCAipv4[rack].prefixlen
    CA['NETMASK']=str(redeHostsCAipv4[rack].netmask)
    CA['BROADCAST']=str(redeHostsCAipv4[rack].broadcast)
    hosts['CA']=CA
    FILER['REDE_IP']=str(redeHostsFILERipv4[rack].ip)
    FILER['REDE_MASK']=redeHostsFILERipv4[rack].prefixlen
    FILER['NETMASK']=str(redeHostsFILERipv4[rack].netmask)
    FILER['BROADCAST']=str(redeHostsFILERipv4[rack].broadcast)
    hosts['FILER']=FILER

    return hosts

def autoprovision_coreoob(rack, FILEINCR, name_core1, name_core2, name_oob, int_oob_core1, int_oob_core2, int_core1_oob, int_core2_oob ):

    #roteiro para configuracao de core
    fileincore=PATH_TO_GUIDE+FILEINCR
    
    #nome dos cores, do console de gerencia dos lf do rack, e do rack
    HOSTNAME_CORE1=name_core1
    HOSTNAME_CORE2=name_core2
    HOSTNAME_OOB=name_oob
    HOSTNAME_RACK = HOSTNAME_OOB.split("-",1)

    #interfaces de conexão entre os cores e o console
    INT_OOBC1_DESCRIP = int_oob_core1
    INT_OOBC2_DESCRIP = int_oob_core2
    INTERFACE_CORE1  = int_core1_oob
    INTERFACE_CORE2  = int_core2_oob

    #gerando dicionarios para substituir paravras chaves do roteiro
    variablestochangecore1={}
    variablestochangecore2={}

    variablestochangecore1["INT_OOB_DESCRIP"]= INT_OOBC1_DESCRIP
    variablestochangecore1["INTERFACE_CORE"]= INTERFACE_CORE1
    variablestochangecore1["HOSTNAME_RACK"]= HOSTNAME_RACK[1]
    variablestochangecore1["SO_HOSTNAME_OOB"]="SO_"+ HOSTNAME_RACK[1]
    if (1+rack)%2==0:
        variablestochangecore1["HSRP_PRIORITY"]="100"
    else:
        variablestochangecore1["HSRP_PRIORITY"]="101"    

    variablestochangecore2["INT_OOB_DESCRIP"]= INT_OOBC2_DESCRIP
    variablestochangecore2["INTERFACE_CORE"]= INTERFACE_CORE2
    variablestochangecore2["HOSTNAME_RACK"]= HOSTNAME_RACK[1]
    variablestochangecore2["SO_HOSTNAME_OOB"]= "SO_"+ HOSTNAME_RACK[1]
    if(2+rack)%2==0:
        variablestochangecore2["HSRP_PRIORITY"]="100"
    else:
        variablestochangecore2["HSRP_PRIORITY"]="101"    

    variablestochangecore1 = dic_vlan_core(variablestochangecore1, rack, HOSTNAME_CORE1, HOSTNAME_RACK[1])
    variablestochangecore2 = dic_vlan_core(variablestochangecore2, rack, HOSTNAME_CORE2, HOSTNAME_RACK[1])

    #arquivos de saida, OOB-CM-01.cfg e OOB-CM-02.cfg
    fileoutcore1=PATH_TO_CONFIG+HOSTNAME_CORE1+"-"+HOSTNAME_RACK[1]+".cfg"    
    fileoutcore2=PATH_TO_CONFIG+HOSTNAME_CORE2+"-"+HOSTNAME_RACK[1]+".cfg" 

    #gerando arquivos de saida
    replace(fileincore,fileoutcore1,variablestochangecore1)
    replace(fileincore,fileoutcore2,variablestochangecore2)

    return True

def autoprovision_splf(rack,FILEINLF,FILEINSP,name_lf1, name_lf2, name_oob, name_sp1, name_sp2, name_sp3, name_sp4, ip_mgmtlf1, ip_mgmtlf2, int_oob_mgmtlf1, int_oob_mgmtlf2, int_sp1, int_sp2, int_sp3, int_sp4, int_lf1_sp1,int_lf1_sp2,int_lf2_sp3,int_lf2_sp4):


    fileinleaf=PATH_TO_GUIDE+FILEINLF
    fileinspine=PATH_TO_GUIDE+FILEINSP

    HOSTNAME_LF1=name_lf1
    HOSTNAME_LF2=name_lf2
    HOSTNAME_OOB=name_oob

    HOSTNAME_SP1=name_sp1
    HOSTNAME_SP2=name_sp2
    HOSTNAME_SP3=name_sp3
    HOSTNAME_SP4=name_sp4

    HOSTNAME_RACK=HOSTNAME_OOB.split("-", 1)

    IP_GERENCIA_LF1=ip_mgmtlf1
    IP_GERENCIA_LF2=ip_mgmtlf2
 
    INTERFACE_SP1=int_sp1
    INTERFACE_SP2=int_sp2
    INTERFACE_SP3=int_sp3
    INTERFACE_SP4=int_sp4
    INTERFACE_OOB_LF1=int_oob_mgmtlf1
    INTERFACE_OOB_LF2=int_oob_mgmtlf2

    BASE_RACK = 120
    BASE_AS = 65000

    VLANBE = 2000
    VLANFE = 2480
    VLANBORDA = 2960
    VLANBORDACACHOS = 3440


    # STRUCTURE: IPSPINE[rack][spine]: ip a configurar no spine 'spine' relativo à leaf do rack 'rack'
    # STRUCTURE: IPLEAF[rack][spine]: ip a configurar na leaf do rack 'rack' relativo ao spine 'spine' 
    CIDREBGP = {}
    CIDRBE = {}
    IPSPINEipv4 = {}
    IPSPINEipv6 = {}
    IPLEAFipv4 = {}
    IPLEAFipv6 = {}
    IPSIBGPipv4 = {}
    IPSIBGPipv6 = {}
    ASLEAF = {}
    #
    VLANBELEAF = {}
    VLANFELEAF = {}
    VLANBORDALEAF = {}
    VLANBORDACACHOSLEAF = {}
    #
    CIDRBEipv4 = {}
    PODSBEipv4 = {}
    redesPODSBEipv4 = {}
    #
    subnetsRackBEipv4 = {}
    #
    CIDRBEipv6 = {}
    PODSBEipv6 = {}
    redesPODSBEipv6 = {}
    PODSBEFEipv6 = {}
    redesPODSBEFEipv6 = {}
    PODSBEBOipv6 = {}
    redesPODSBEBOipv6 = {}
    PODSBECAipv6 = {}
    redesPODSBECAipv6 = {}
    redesHostsipv6 = {}
    redeHostsBEipv6 = {}
    redeHostsFEipv6 = {}
    redeHostsBOipv6 = {}
    redeHostsCAipv6 = {}
    redeHostsFILERipv6 = {}
    subnetsRackBEipv6 = {}
    subnetsRackFEipv4 = {}
    redesPODSFEipv4 = {}
    subnetsRackFEipv6 = {}
    redesPODSFEipv6 = {}
    #
    IPSPINEipv4[rack]=[]
    IPSPINEipv6[rack]=[]
    IPLEAFipv4[rack]=[]
    IPLEAFipv6[rack]=[]
    IPSIBGPipv4[rack]=[]
    IPSIBGPipv6[rack]=[]
    VLANBELEAF[rack]=[]
    VLANFELEAF[rack]=[]
    VLANBORDALEAF[rack]=[]
    VLANBORDACACHOSLEAF[rack]=[]
    ASLEAF[rack]=[]
    #
    PODSBEipv4[rack]=[]
    redesPODSBEipv4[rack]=[]
    #
    subnetsRackBEipv4[rack] = []
    #
    PODSBEipv6[rack]=[]
    redesPODSBEipv6[rack]=[]
    PODSBEFEipv6[rack]=[]
    redesPODSBEFEipv6[rack]=[]
    PODSBEBOipv6[rack]=[]
    redesPODSBEBOipv6[rack]=[]
    PODSBECAipv6[rack]=[]
    redesPODSBECAipv6[rack]=[]
    redesHostsipv6[rack]=[]
    redeHostsBEipv6[rack]=[]
    redeHostsFEipv6[rack]=[]
    redeHostsBOipv6[rack]=[]
    redeHostsCAipv6[rack]=[]
    redeHostsFILERipv6[rack]=[]
    subnetsRackBEipv6[rack] = []
    subnetsRackFEipv4[rack] = []
    redesPODSFEipv4[rack] = []
    subnetsRackFEipv6[rack] = []
    redesPODSFEipv6[rack] = []

    #CIDR sala 01 => 10.128.0.0/12
    CIDRBE[0] = IPNetwork('10.128.0.0/12')
    CIDREBGP[0] = IPNetwork('10.10.0.0/22')

    SPINE1ipv4 = IPNetwork('10.0.0.0/24')
    SPINE2ipv4 = IPNetwork('10.0.1.0/24')
    SPINE3ipv4 = IPNetwork('10.0.2.0/24')
    SPINE4ipv4 = IPNetwork('10.0.3.0/24')
    subSPINE1ipv4=list(SPINE1ipv4.subnet(31))
    subSPINE2ipv4=list(SPINE2ipv4.subnet(31))
    subSPINE3ipv4=list(SPINE3ipv4.subnet(31))
    subSPINE4ipv4=list(SPINE4ipv4.subnet(31))

    SPINE1ipv6 = IPNetwork('fdbe:0:0:1eaf::/120')
    SPINE2ipv6 = IPNetwork('fdbe:0:0:1eaf::100/120')
    SPINE3ipv6 = IPNetwork('fdbe:0:0:1eaf::200/120')
    SPINE4ipv6 = IPNetwork('fdbe:0:0:1eaf::300/120')
    subSPINE1ipv6=list(SPINE1ipv6.subnet(127))
    subSPINE2ipv6=list(SPINE2ipv6.subnet(127))
    subSPINE3ipv6=list(SPINE3ipv6.subnet(127))
    subSPINE4ipv6=list(SPINE4ipv6.subnet(127))


    IBGPToRLxLipv4 = IPNetwork('10.0.4.0/24')
    subIBGPToRLxLipv4 = list(IBGPToRLxLipv4.subnet(31))

    IBGPToRLxLipv6 = IPNetwork('fdbe:0:0:1eaf:8100::/120')
    subIBGPToRLxLipv6 = list(IBGPToRLxLipv6.subnet(127))


    IPSPINEipv4[rack].append(subSPINE1ipv4[rack][0])
    IPSPINEipv4[rack].append(subSPINE2ipv4[rack][0])
    IPSPINEipv4[rack].append(subSPINE3ipv4[rack][0])
    IPSPINEipv4[rack].append(subSPINE4ipv4[rack][0])
    #  
    IPLEAFipv4[rack].append(subSPINE1ipv4[rack][1])
    IPLEAFipv4[rack].append(subSPINE2ipv4[rack][1])
    IPLEAFipv4[rack].append(subSPINE3ipv4[rack][1])
    IPLEAFipv4[rack].append(subSPINE4ipv4[rack][1])   
    #
    IPSIBGPipv4[rack].append(subIBGPToRLxLipv4[rack][0])
    IPSIBGPipv4[rack].append(subIBGPToRLxLipv4[rack][1])
    #
    IPSPINEipv6[rack].append(subSPINE1ipv6[rack][0])
    IPSPINEipv6[rack].append(subSPINE2ipv6[rack][0])
    IPSPINEipv6[rack].append(subSPINE3ipv6[rack][0])
    IPSPINEipv6[rack].append(subSPINE4ipv6[rack][0])
    #  
    IPLEAFipv6[rack].append(subSPINE1ipv6[rack][1])
    IPLEAFipv6[rack].append(subSPINE2ipv6[rack][1])
    IPLEAFipv6[rack].append(subSPINE3ipv6[rack][1])
    IPLEAFipv6[rack].append(subSPINE4ipv6[rack][1])   
    #
    IPSIBGPipv6[rack].append(subIBGPToRLxLipv6[rack][0])
    IPSIBGPipv6[rack].append(subIBGPToRLxLipv6[rack][1])
    #
    VLANBELEAF[rack].append(VLANBE+rack)
    VLANBELEAF[rack].append(VLANBE+rack+BASE_RACK)
    VLANBELEAF[rack].append(VLANBE+rack+2*BASE_RACK)
    VLANBELEAF[rack].append(VLANBE+rack+3*BASE_RACK)
    #
    VLANFELEAF[rack].append(VLANFE+rack)
    VLANFELEAF[rack].append(VLANFE+rack+BASE_RACK)
    VLANFELEAF[rack].append(VLANFE+rack+2*BASE_RACK)
    VLANFELEAF[rack].append(VLANFE+rack+3*BASE_RACK)
    #
    VLANBORDALEAF[rack].append(VLANBORDA+rack)
    VLANBORDALEAF[rack].append(VLANBORDA+rack+BASE_RACK)
    VLANBORDALEAF[rack].append(VLANBORDA+rack+2*BASE_RACK)
    VLANBORDALEAF[rack].append(VLANBORDA+rack+3*BASE_RACK)
    #
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS+rack)
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS+rack+BASE_RACK)
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS+rack+2*BASE_RACK)
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS+rack+3*BASE_RACK)
    #
    ASLEAF[rack].append(BASE_AS+rack)


    ############################################################################
    ############################################################################
    #CIDR sala 01 => 10.128.0.0/12
    CIDRBEipv4 = IPNetwork('10.128.0.0/12')
    CIDRBEipv6 = IPNetwork('fdbe:bebe:bedc::/48')


    #          ::::::: SUBNETING FOR RACK NETWORKS - /19 :::::::

    #Redes p/ rack => 10.128.0.0/19, 10.128.32.0/19 , ... ,10.143.224.0/19
    subnetsRackBEipv4[rack]=splitnetworkbyrack(CIDRBEipv4,19,rack)
    subnetsRackBEipv6[rack]=splitnetworkbyrack(CIDRBEipv6,55,rack)

    #PODS BE => /20
    subnetteste=subnetsRackBEipv4[rack]

    #dic_pods()
    #dic_hosts()

    #    ::::::::::::::::::::::::::::::::::: FRONTEND


    CIDRFEipv4 = {}
    CIDRFEipv6 = {}

    #CIDR sala 01 => 172.20.0.0/14
    #Sumário do rack => 172.20.0.0/21
    CIDRFEipv4[0] = IPNetwork('172.20.0.0/14')
    #CIDRFE[1] = IPNetwork('172.20.1.0/14')
    CIDRFEipv6[0] = IPNetwork('fdfe:fefe:fedc:0100::/50')

    #          ::::::: SUBNETING FOR RACK NETWORKS - /19 :::::::

    #Sumário do rack => 172.20.0.0/21
    subnetsRackFEipv4[rack]=splitnetworkbyrack(CIDRFEipv4[0],21,rack)
    subnetsRackFEipv6[rack]=splitnetworkbyrack(CIDRFEipv6[0],57,rack)
    #          ::::::: SUBNETING EACH RACK NETWORK:::::::
    # PODS FE => 128 redes /27 ; 128 redes /64
    redesPODSBEipv4[rack] = list(subnetsRackFEipv4[rack].subnet(27))
    redesPODSBEipv6[rack] = list(subnetsRackFEipv6[rack].subnet(64))



    variablestochangespine1={}
    variablestochangespine2={}
    variablestochangespine3={}
    variablestochangespine4={}
    variablestochangeleaf1={}
    variablestochangeleaf2={}
    variablestochangecore1={}
    variablestochangecore2={}
   
    variablestochangespine1["IPSPINEIPV4"]=str(IPSPINEipv4[rack][0])+" 255.255.255.254" 
    variablestochangespine1["IPSPINEIPV6"]=str(IPSPINEipv6[rack][0])+ " 127"
    variablestochangespine1["VLANBELEAF"]=str(VLANBELEAF[rack][0])
    variablestochangespine1["VLANFELEAF"]=str(VLANFELEAF[rack][0])
    variablestochangespine1["VLANBORDALEAF"]=str(VLANBORDALEAF[rack][0])
    variablestochangespine1["VLANBORDACACHOSLEAF"]=str(VLANBORDACACHOSLEAF[rack][0])
    variablestochangespine1["ASSPINE"]=str(64600)
    variablestochangespine1["ASLEAF"]=str(ASLEAF[rack][0])
    variablestochangespine1["IPNEIGHLEAFIPV4"]=str(IPLEAFipv4[rack][0])
    variablestochangespine1["IPNEIGHLEAFIPV6"]=str(IPLEAFipv6[rack][0])
    variablestochangespine1["INTERFACE"]=INTERFACE_SP1
    variablestochangespine1["LEAFNAME"]=HOSTNAME_LF1
    variablestochangespine1["INT_LF_DESCRIP"]=int_lf1_sp1 
    #
    #
    variablestochangespine2["IPSPINEIPV4"]=str(IPSPINEipv4[rack][1])+" 255.255.255.254" 
    variablestochangespine2["IPSPINEIPV6"]=str(IPSPINEipv6[rack][1])+ " 127"
    variablestochangespine2["VLANBELEAF"]=str(VLANBELEAF[rack][1])
    variablestochangespine2["VLANFELEAF"]=str(VLANFELEAF[rack][1])
    variablestochangespine2["VLANBORDALEAF"]=str(VLANBORDALEAF[rack][1])
    variablestochangespine2["VLANBORDACACHOSLEAF"]=str(VLANBORDACACHOSLEAF[rack][1])
    variablestochangespine2["ASSPINE"]=str(64601)
    variablestochangespine2["ASLEAF"]=str(ASLEAF[rack][0])
    variablestochangespine2["IPNEIGHLEAFIPV4"]=str(IPLEAFipv4[rack][1])
    variablestochangespine2["IPNEIGHLEAFIPV6"]=str(IPLEAFipv6[rack][1])
    variablestochangespine2["INTERFACE"]=INTERFACE_SP2
    variablestochangespine2["LEAFNAME"]=HOSTNAME_LF1  
    variablestochangespine2["INT_LF_DESCRIP"]=int_lf1_sp2 
    #
    #
    variablestochangespine3["IPSPINEIPV4"]=str(IPSPINEipv4[rack][2])+" 255.255.255.254" 
    variablestochangespine3["IPSPINEIPV6"]=str(IPSPINEipv6[rack][2])+ " 127"
    variablestochangespine3["VLANBELEAF"]=str(VLANBELEAF[rack][2])
    variablestochangespine3["VLANFELEAF"]=str(VLANFELEAF[rack][2])
    variablestochangespine3["VLANBORDALEAF"]=str(VLANBORDALEAF[rack][2])
    variablestochangespine3["VLANBORDACACHOSLEAF"]=str(VLANBORDACACHOSLEAF[rack][2])
    variablestochangespine3["ASSPINE"]=str(64602)
    variablestochangespine3["ASLEAF"]=str(ASLEAF[rack][0])
    variablestochangespine3["IPNEIGHLEAFIPV4"]=str(IPLEAFipv4[rack][2])
    variablestochangespine3["IPNEIGHLEAFIPV6"]=str(IPLEAFipv6[rack][2])
    variablestochangespine3["INTERFACE"]=INTERFACE_SP3
    variablestochangespine3["LEAFNAME"]=HOSTNAME_LF2
    variablestochangespine3["INT_LF_DESCRIP"]=int_lf2_sp3  
    #
    #
    variablestochangespine4["IPSPINEIPV4"]=str(IPSPINEipv4[rack][3])+" 255.255.255.254" 
    variablestochangespine4["IPSPINEIPV6"]=str(IPSPINEipv6[rack][3])+ " 127"
    variablestochangespine4["VLANBELEAF"]=str(VLANBELEAF[rack][3])
    variablestochangespine4["VLANFELEAF"]=str(VLANFELEAF[rack][3])
    variablestochangespine4["VLANBORDALEAF"]=str(VLANBORDALEAF[rack][3])
    variablestochangespine4["VLANBORDACACHOSLEAF"]=str(VLANBORDACACHOSLEAF[rack][3])
    variablestochangespine4["ASSPINE"]=str(64603)
    variablestochangespine4["ASLEAF"]=str(ASLEAF[rack][0])
    variablestochangespine4["IPNEIGHLEAFIPV4"]=str(IPLEAFipv4[rack][3])
    variablestochangespine4["IPNEIGHLEAFIPV6"]=str(IPLEAFipv6[rack][3])
    variablestochangespine4["INTERFACE"]=INTERFACE_SP4
    variablestochangespine4["LEAFNAME"]=HOSTNAME_LF2 
    variablestochangespine4["INT_LF_DESCRIP"]=int_lf2_sp4
    #
    #
    variablestochangeleaf1["IPLEAFSP1IPV4"]=os.path.join( str(IPLEAFipv4[rack][0]),str(31) )
    variablestochangeleaf1["IPLEAFSP2IPV4"]=os.path.join( str(IPLEAFipv4[rack][1]),str(31) )
    variablestochangeleaf1["IPIBGPIPV4"]=os.path.join( str(IPSIBGPipv4[rack][0]),str(31) )
    variablestochangeleaf1["IPLEAFSP1IPV6"]=os.path.join( str(IPLEAFipv6[rack][0]),str(127) )
    variablestochangeleaf1["IPLEAFSP2IPV6"]=os.path.join( str(IPLEAFipv6[rack][1]),str(127) )
    variablestochangeleaf1["IPIBGPIPV6"]=os.path.join( str(IPSIBGPipv6[rack][0]),str(127) )
    variablestochangeleaf1["VLANBELEAFSP1"]=str(VLANBELEAF[rack][0])
    variablestochangeleaf1["VLANBELEAFSP2"]=str(VLANBELEAF[rack][1])
    variablestochangeleaf1["VLANFELEAFSP1"]=str(VLANFELEAF[rack][0])
    variablestochangeleaf1["VLANFELEAFSP2"]=str(VLANFELEAF[rack][1])
    variablestochangeleaf1["VLANBORDALEAFSP1"]=str(VLANBORDALEAF[rack][0])
    variablestochangeleaf1["VLANBORDALEAFSP2"]=str(VLANBORDALEAF[rack][1])
    variablestochangeleaf1["VLANBORDACACHOSLEAFSP1"]=str(VLANBORDACACHOSLEAF[rack][0])
    variablestochangeleaf1["VLANBORDACACHOSLEAFSP2"]=str(VLANBORDACACHOSLEAF[rack][1])
    variablestochangeleaf1["ASLEAF"]=str(ASLEAF[rack][0])
    variablestochangeleaf1["ASSPINE1"]=str(64600)
    variablestochangeleaf1["ASSPINE2"]=str(64601)
    variablestochangeleaf1["IPNEIGHSPINE1IPV4"]=str(IPSPINEipv4[rack][0])
    variablestochangeleaf1["IPNEIGHSPINE2IPV4"]=str(IPSPINEipv4[rack][1])
    variablestochangeleaf1["IPNEIGHIBGPIPV4"]=str(IPSIBGPipv4[rack][1])
    variablestochangeleaf1["IPNEIGHSPINE1IPV6"]=str(IPSPINEipv6[rack][0])
    variablestochangeleaf1["IPNEIGHSPINE2IPV6"]=str(IPSPINEipv6[rack][1])
    variablestochangeleaf1["IPNEIGHIBGPIPV6"]=str(IPSIBGPipv6[rack][1])
    variablestochangeleaf1["LF_HOSTNAME"]=HOSTNAME_LF1
    variablestochangeleaf1["NET_HOST_BE_IPV4"]= str(subnetsRackBEipv4[rack])
    variablestochangeleaf1["NET_HOST_FE_IPV4"]=str(subnetsRackFEipv4[rack])
    variablestochangeleaf1["NET_SPINE1_LF_IPV4"]=str(subSPINE1ipv4[rack])
    variablestochangeleaf1["NET_SPINE2_LF_IPV4"]=str(subSPINE2ipv4[rack])
    variablestochangeleaf1["NET_LF_LF_IPV4"]=str(subIBGPToRLxLipv4[rack])
    variablestochangeleaf1["NET_HOST_BE_IPV6"]= str(subnetsRackBEipv6[rack])
    variablestochangeleaf1["NET_HOST_FE_IPV6"]=str(subnetsRackFEipv6[rack])
    variablestochangeleaf1["NET_SPINE1_LF_IPV6"]=str(subSPINE1ipv6[rack])
    variablestochangeleaf1["NET_SPINE2_LF_IPV6"]=str(subSPINE2ipv6[rack])
    variablestochangeleaf1["NET_LF_LF_IPV6"]=str(subIBGPToRLxLipv6[rack])
    variablestochangeleaf1["ID_LEAF"]="1"
    variablestochangeleaf1["OWN_IP_MGMT"]=IP_GERENCIA_LF1
    variablestochangeleaf1["LFNEIGH_IP_MGMT"]=IP_GERENCIA_LF2
    variablestochangeleaf1["LFNEIGH_HOSTNAME"]= HOSTNAME_LF2
    variablestochangeleaf1["SP1_HOSTNAME"]=HOSTNAME_SP1
    variablestochangeleaf1["SP2_HOSTNAME"]=HOSTNAME_SP2
    variablestochangeleaf1["INTERFACE_SP1"]= INTERFACE_SP1
    variablestochangeleaf1["INTERFACE_SP2"]= INTERFACE_SP2
    variablestochangeleaf1["HOSTNAME_OOB"]= HOSTNAME_OOB
    variablestochangeleaf1["INTERFACE_OOB"]= INTERFACE_OOB_LF1
    variablestochangeleaf1["KICKSTART_SO_LF"]= KICKSTART_SO_LF
    variablestochangeleaf1["IMAGE_SO_LF"]= IMAGE_SO_LF
    #
    #
    variablestochangeleaf2["IPLEAFSP1IPV4"]=os.path.join( str(IPLEAFipv4[rack][2]),str(31) )
    variablestochangeleaf2["IPLEAFSP2IPV4"]=os.path.join( str(IPLEAFipv4[rack][3]),str(31) )
    variablestochangeleaf2["IPIBGPIPV4"]=os.path.join( str(IPSIBGPipv4[rack][1]),str(31) )
    variablestochangeleaf2["IPLEAFSP1IPV6"]=os.path.join( str(IPLEAFipv6[rack][2]),str(127) )
    variablestochangeleaf2["IPLEAFSP2IPV6"]=os.path.join( str(IPLEAFipv6[rack][3]),str(127) )
    variablestochangeleaf2["IPIBGPIPV6"]=os.path.join( str(IPSIBGPipv6[rack][1]),str(127) )
    variablestochangeleaf2["VLANBELEAFSP1"]=str(VLANBELEAF[rack][2])
    variablestochangeleaf2["VLANBELEAFSP2"]=str(VLANBELEAF[rack][3])
    variablestochangeleaf2["VLANFELEAFSP1"]=str(VLANFELEAF[rack][2])
    variablestochangeleaf2["VLANFELEAFSP2"]=str(VLANFELEAF[rack][3])
    variablestochangeleaf2["VLANBORDALEAFSP1"]=str(VLANBORDALEAF[rack][2])
    variablestochangeleaf2["VLANBORDALEAFSP2"]=str(VLANBORDALEAF[rack][3])
    variablestochangeleaf2["VLANBORDACACHOSLEAFSP1"]=str(VLANBORDACACHOSLEAF[rack][2])
    variablestochangeleaf2["VLANBORDACACHOSLEAFSP2"]=str(VLANBORDACACHOSLEAF[rack][3])
    variablestochangeleaf2["ASLEAF"]=str(ASLEAF[rack][0])
    variablestochangeleaf2["ASSPINE1"]=str(64602)
    variablestochangeleaf2["ASSPINE2"]=str(64603)
    variablestochangeleaf2["IPNEIGHSPINE1IPV4"]=str(IPSPINEipv4[rack][2])
    variablestochangeleaf2["IPNEIGHSPINE2IPV4"]=str(IPSPINEipv4[rack][3])
    variablestochangeleaf2["IPNEIGHIBGPIPV4"]=str(IPSIBGPipv4[rack][0])
    variablestochangeleaf2["IPNEIGHSPINE1IPV6"]=str(IPSPINEipv6[rack][2])
    variablestochangeleaf2["IPNEIGHSPINE2IPV6"]=str(IPSPINEipv6[rack][3])
    variablestochangeleaf2["IPNEIGHIBGPIPV6"]=str(IPSIBGPipv6[rack][0])
    variablestochangeleaf2["LF_HOSTNAME"]=HOSTNAME_LF2
    variablestochangeleaf2["NET_HOST_BE_IPV4"]= str(subnetsRackBEipv4[rack])
    variablestochangeleaf2["NET_HOST_FE_IPV4"]=str(subnetsRackFEipv4[rack])
    variablestochangeleaf2["NET_SPINE1_LF_IPV4"]=str(subSPINE3ipv4[rack])
    variablestochangeleaf2["NET_SPINE2_LF_IPV4"]=str(subSPINE4ipv4[rack])
    variablestochangeleaf2["NET_LF_LF_IPV4"]=str(subIBGPToRLxLipv4[rack])
    variablestochangeleaf2["NET_HOST_BE_IPV6"]= str(subnetsRackBEipv6[rack])
    variablestochangeleaf2["NET_HOST_FE_IPV6"]=str(subnetsRackFEipv6[rack])
    variablestochangeleaf2["NET_SPINE1_LF_IPV6"]=str(subSPINE3ipv6[rack])
    variablestochangeleaf2["NET_SPINE2_LF_IPV6"]=str(subSPINE4ipv6[rack])
    variablestochangeleaf2["NET_LF_LF_IPV6"]=str(subIBGPToRLxLipv6[rack])
    variablestochangeleaf2["ID_LEAF"]="2"
    variablestochangeleaf2["OWN_IP_MGMT"]=IP_GERENCIA_LF2
    variablestochangeleaf2["LFNEIGH_IP_MGMT"]=IP_GERENCIA_LF1
    variablestochangeleaf2["LFNEIGH_HOSTNAME"]= HOSTNAME_LF1
    variablestochangeleaf2["SP1_HOSTNAME"]=HOSTNAME_SP3
    variablestochangeleaf2["SP2_HOSTNAME"]=HOSTNAME_SP4
    variablestochangeleaf2["INTERFACE_SP1"]= INTERFACE_SP3
    variablestochangeleaf2["INTERFACE_SP2"]= INTERFACE_SP4
    variablestochangeleaf2["HOSTNAME_OOB"]= HOSTNAME_OOB
    variablestochangeleaf2["INTERFACE_OOB"]= INTERFACE_OOB_LF2
    variablestochangeleaf2["KICKSTART_SO_LF"]= KICKSTART_SO_LF
    variablestochangeleaf2["IMAGE_SO_LF"]= IMAGE_SO_LF


    fileoutspine1=PATH_TO_CONFIG+HOSTNAME_SP1+"-"+HOSTNAME_RACK[1]+".cfg"
    fileoutspine2=PATH_TO_CONFIG+HOSTNAME_SP2+"-"+HOSTNAME_RACK[1]+".cfg"
    fileoutspine3=PATH_TO_CONFIG+HOSTNAME_SP3+"-"+HOSTNAME_RACK[1]+".cfg"
    fileoutspine4=PATH_TO_CONFIG+HOSTNAME_SP4+"-"+HOSTNAME_RACK[1]+".cfg"
    fileoutleaf1=PATH_TO_CONFIG+HOSTNAME_LF1+".cfg"
    fileoutleaf2=PATH_TO_CONFIG+HOSTNAME_LF2+".cfg"

    replace(fileinspine,fileoutspine1,variablestochangespine1)
    replace(fileinspine,fileoutspine2,variablestochangespine2)
    replace(fileinspine,fileoutspine3,variablestochangespine3)
    replace(fileinspine,fileoutspine4,variablestochangespine4)
    replace(fileinleaf,fileoutleaf1,variablestochangeleaf1)
    replace(fileinleaf,fileoutleaf2,variablestochangeleaf2)

    return True

